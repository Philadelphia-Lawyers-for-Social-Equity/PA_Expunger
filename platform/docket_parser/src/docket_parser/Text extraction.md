Content Streams
---
Text is stored in the PDF content streams. 
Specifically, all displayed text originates from a `Tj` or `TJ` operation in the content stream.
Each page has exactly one content stream, which describes how to draw everything on the page. 
Content streams can reference Resources which are stored elsewhere in the PDF, such as fonts and images.

It's rarely advisable to scrape text information out of a content stream, but our case is one of those rare situations.
Because:

- The PDFs are generated by the [state website] upon request, rather than stored on their servers.
- The software that generates the PDFs (Crystal Reports by SAP) writes the content stream the same way each time,
  only changing with new versions of that software.
- The order of text in the content stream is amenable to parsing with a relatively simple Parsing Expressive Grammar (
  PEG)

The drawback of reading directly from content streams is that if the way the state website generates PDFs changes,
either from an update to Crystal Reports or a switch to different PDF exporter, we would have to rewrite a lot of code
to adapt.
Even if the final rendered PDFs look identical.

[state website]: https://ujsportal.pacourts.us/CaseSearch

PDF content streams are stateful, and important elements of the current state for us are:

- Font name
- Font size
- Text matrix (`tm` in pypdf). Technically, this matrix converts the text space coordinates to user space coordinates,
  and characters are always placed starting at the origin in text space. See 8.3 in the [PDF 1.7 specification][PDF] for
  more details.
  However, in these PDFs, the text matrix always represents a simple translation from the origin. So, we can think of
  the text matrix as describing "where the text cursor is."
- Current transformation matrix (a.k.a. CTM, or `cm` in pypdf).
  Text matrix multiplied by CTM yields the matrix transforming text space to device space,
  which describes where things end up on the page. Note that matrix multiplication is not commutative.

Pypdf keeps track of text matrix and current transformation matrix for us, and passes them to our operand visitor.
We need to keep track of font name and font size, which are components of the Text State.
The text state is in turn a component of the Graphics State.
There is a graphics state stack, which is pushed to and popped from with the operators `q` and `Q` respectively.
We need to keep track of that stack.



Character IDs (a.k.a. cid's)
---
Each character in a font has a character id (cid). For the fonts we're looking at, the cids are one byte each.
The individual text characters actually rendered on the display/printer are called **glyphs**.
Fonts must describe how cids map to glyphs, and how to draw the glyphs. 
Fonts can also optionally include a /ToUnicode character map, which describes how character ids map to unicode characters.
This /ToUnicode map is essential for extracting text from PDFs. 
pypdf provides a function to parse the /ToUnicode character map and return a python dictionary mapping cids to unicode characters. 
The function `get_unicode_map` in font.py converts those keys to integers, and returns a dictionary mapping integer cids to unicode characters.
For some fonts, the character ids are equal to the ascii characters they represent, making the content streams somewhat readable.
This is not true in general, and is not the case for the fonts found in recently generated pacourts PDFS.
PDFs generated on pacourts website use TrueType fonts, with a /ToUnicode character map.

Note: The actual content stream of the PDF is compressed.
qpdf, the software which pypdf relies on, handles compression/decompression.
We don't need to worry about it.

Here is the first few lines of an uncompressed PDF content stream from a docket. Each character is one ascii-encoded
byte.
See section 7.8 of the [PDF specification][PDF] for details on content streams,
and sections 7.1-7.3 for details on syntax of and objects in PDFs.

```text
1 0 0 1 0 792 cm
0 0 0 rg
0 0 0 RG
18 -28.8 583.2 -748.8 re
W
n
2 J
2 w
31 -31.9 556 -674.4 re
S
BT
1 0 0 1 109.25 -47.55 Tm
/9 14.3 Tf
<434f555254204f4620434f4d4d4f4e20504c454153204f46205048494c4144454c504849> Tj
[ (A) 35 ( COUNT) (Y) 17 (  ) ] TJ
0.753 0.753 0.753 sc
ET
35.25 -54.3 542.25 -15 re
f
BT
1 0 0 1 260.85 -65.45 Tm
0 0 0 sc
/9 10.5 Tf
<53454355524520444f434b4554> Tj
0.902 0.902 0.902 sc
ET
```
Annotated with explanation:

`1 0 0 1 0 792 cm` Set current transformation matrix \
`0 0 0 rg` Set color for non-stroking operations to RGB (0,0,0) (black)\
`0 0 0 RG` Set color for stroking operations to RGB (0,0,0) (black)\
`18 -28.8 583.2 -748.8 re` Add a rectangle to path (details unimportant for us) \
`W` Make that rectangle be the new clipping path (irrelevant for text extraction)\
`n` End path without filling or stroking\
`2 J` Set a property of drawing lines\
`2 w` Set line width\
`31 -31.9 556 -674.4 re` Add a rectangle to path\
`S` Stroke that rectangle path\
`BT` Begin text block\
`1 0 0 1 109.25 -47.55 Tm` Set text matrix\
`/9 14.3 Tf` Set current font to '/9' and font size to 14.3\
`<434f555254204f4620434f4d4d4f4e20504c454153204f46205048494c4144454c504849> Tj` Show this text string.\
`[ (A) 35 ( COUNT) (Y) 17 (  ) ] TJ` Show the text strings in parentheses. Spacing is adjusted by the numbers between
strings.\
`0.753 0.753 0.753 sc` Set color to gray for non-stroking operations (for upcoming rectangle fill)\
`ET` End text block\
`35.25 -54.3 542.25 -15 re` Add rectangle to path\
`f` Fill the rectangle\
`BT` Begin text block\
`1 0 0 1 260.85 -65.45 Tm` Set text matrix. In this case, move next text position 260.85 text units to the right and
65.45 text units down\
`0 0 0 sc` Set color for non-stroking operations\
`/9 10.5 Tf` Set current font to '/9' and font size to 10.5\
`<53454355524520444f434b4554> Tj` Show this text string\
`0.902 0.902 0.902 sc` Set color for non-stroking operations\
`ET` End text block

Currently, the only operators that we look at are:
- `TF` Sets current font and font size.
- `Td` Applies a transformation to text matrix. Effectively, moves where the next shown text will start.
- `q`, `Q` Push and pop, respectively, from the graphics state stack (which includes text state).
- `ET` Ends text block.
- `Tj` Shows a string of characters.
- `TJ` Shows a string of characters, allowing for horizontal position adjustments between characters.
These horizontal spacing adjustments are used for one of two reasons in these documents: 
  - Positive adjustments (to the left) are exclusively used for [kerning], moving characters closer together when appropriate.
  - Negative adjustments (to the right) are exclusively used for adding space between words to achieve [fully justified alignment]

pypdf does some processing of the content stream before passing its contents to our visitor function. 
For example, where the content stream has the bytes `[ (A) 35 ( COUNT) (Y) 17 (  ) ] TJ`, 
pypdf will convert the operand to a python list of `bytes` and `int`s:
`[b'A', 35, b' COUNT', b'Y', 17, b'  ']`.
pypdf will also convert the hexadecimal strings like `<53454355524520444f434b4554>` into python bytes objects, where each byte is one character id:
`b'SECURE DOCKET'`.

The extract_text method of DocketReader and DocketPageObject can take an optional bool `debug_log_operations`.
If this argument is True, all operations will be logged at log level `DEBUG`, in the format that pypdf sends them to our visitor,
except the arguments for `Tj` and `TJ` will be decoded.
`DocketReader._debug_get_all_operations` returns a list of all operations, without decoding text.

X and Y tolerance
---
Text is considered to be on the same line if y position adjustment is less than `y_tolerance`.
This is necessary because many logical lines on these PDFs have slight variations in y coordinates.

Similarly, we use `x_tolerance` whenever we check if two horizontal positions are the same.

Both tolerances are measured in text space units.

Segments
---
We process the text into 'segments' which are sequences of text with the same properties usually on the same horizontal line.
We concatenate decoded characters from `Tj` and `TJ` operations to build the segments.
We also keep track of the horizontal displacement (formal name for width) of the segments, 
so that we can tell if a `Td` operation moves the cursor directly at the end of the last character shown, or far enough to insert a tab.
We end one segment and start the next when one of the following occurs in the content stream:
- `Tf` or `Q` operators, which change the font and or font size.
- `ET` operator, which indicates the end of a text block.
- `Td` operator that moves the cursor vertically more than the `y_tolerance`, UNLESS it looks like a new line of a text
  box

We say that we're in a (left justified) textbox if the cursor is moved directly under the start of the current segment,
within `x_tolerance` of the starting x position.

Special inserted characters
---
We use a handful of special characters to indicate different kinds of text spacing/positioning.
The actual character inserted in output text is determined by the DocketReader.
For parsing, it is very important that the inserted characters do not appear in the text of the PDF.

- `terminator` - inserted at the end of each segment
- `tab` - inserted when the cursor moves to the right on the same line, at least `x_tolerance` past the end of the last
  shown character
- `comes_before` - inserted when the cursor moves to the left on the same line
- `box_wrap` - inserted when a left justified textbox continues to the next line
- `properties_open` and `properties_close` - used to delimit the information we add at the end of each segment in the
  output

User space coordinates and font type are added at the end of each segment


[PDF]: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
[kerning]: https://en.wikipedia.org/wiki/Kerning
[fully justified alignment]: https://en.wikipedia.org/wiki/Typographic_alignment#Justified
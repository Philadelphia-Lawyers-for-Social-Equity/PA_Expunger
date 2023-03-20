Where does the data come from and where does it go?

- The text in the PDF is stored in each page's content stream. See section 7.8 of the [PDF 1.7 specification].
- We read through the content streams to get the text, along with some other properties like font and positioning information.
- We also insert some special characters to indicate different kinds of spacing from the PDF.
- The text extractor spits out one very long string, composed of 'segments,' separated by terminator characters (usually '\n').
  - These segments contain text from the PDF, our inserted spacing characters, and properties enclosed in more special characters.
  - Example: `10/11/2018_11:00 am_378_Scheduled|Payment Plan ^Conference[143.25,150.45,normal]`
  - In above segment, x and y coordinates in PDF user space are 143.25 and 150.45 respectively. The font is normal (not bold)
- We use the [Parsimonious] library to parse the extracted text.
  - Parsimonious is based on [parsing expression grammars] (PEGs). 
  - We give it a parsimonious flavored PEG, and it uses the grammar to build a [*parse tree*].
  - Every node in the parse tree will correspond to a term or expression in the grammar. The leaves of the tree will be string literals.
- We traverse the parse tree with a class inheriting parsimonious's `NodeVisitor`, to retrieve the information from the relevant nodes.
  - We need a visitor function for each node that we care about, to collect the relevant text from itself or its children, and pass it up the tree.
  - The visitor for the root node, which is the left hand side of the first rule listed in grammar, returns the final result with all the information.

[Parsimonious]: https://github.com/erikrose/parsimonious/
[PDF 1.7 specification]: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
[*parse tree*]: https://en.wikipedia.org/wiki/Parse_tree
[parsing expression grammars]: https://en.wikipedia.org/wiki/Parsing_expression_grammar
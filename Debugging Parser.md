The `docket_parser` package has a simple command line interface for debugging. 
It can be run with `python3 [directory of the docket_parser package]`

To print the text extracted from a pdf (which is the subject of parsing), use it without `-o`.

To print the information which is the output of the parser, use `-o`.
Usage information:
```
usage: Debug Docket Parser [-h] [-o] [--loglevel LOGLEVEL] [--verbose] filename

positional arguments:
  filename             Docket to analyze. If not a valid filename, will try to find matching test pdf

optional arguments:
  -h, --help           show this help message and exit
  -o                   Return the output of the parser, rather than the text being parsed
  --loglevel LOGLEVEL  set log level
  --verbose            print logging messages

```


For convenience, in the docker expunger container, `debug_parser` is an alias of `python3 /srv/plse/install/docket_parser/docket_parser`
So, to run command line debug in docker, you would:
```sh
# Open a bash terminal in the docker container
docker-compose exec -it expunger bash

# Print text extracted from test-01.pdf
debug_parser 01

# Print information gleaned from test-03.pdf
debug_parser -o 03
```

In a local environment, it could be run like
```sh
# Print text extracted from your-test-docket.pdf
python3 docket_dashboard/platform/docket_parser/docket_parser ~/your-test-docket.pdf

# Save the text extracted from test-02.pdf to test-02.txt
python3 docket_dashboard/platform/docket_parser/docket_parser 2 > ~/temp/test-02.txt
```

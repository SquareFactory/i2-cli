# i2

`i2py`, for isquare python client, is the name of the general command used for the client:

```bash
Usage: i2py [OPTIONS] COMMAND [ARGS]...

  Command line interface for isquare.

Options:
  --help  Show this message and exit.

Commands:
  build  Build an docker image ready for isquare.
  infer  Send data for inference.
  test   Verify that an docker image matches the isquare standard.
```

## build

```bash
Usage: i2py build [OPTIONS] SCRIPT

  Build an docker image ready for isquare.

Options:
  -df, --dockerfile PATH  Name of the Dockerfile. If none provided, base image
                          is used.
  -nc, --no-cache         Do not use previous cache when building the image
  -t, --tag TEXT          Name and optionally a tag in the 'name:tag' format
  --cpu                   Force the use of CPU base image when no dockerfile
                          available
  -ba, --build-args TEXT  Set build-time variables, like in docker
  --debug                 Increase logging verbosity level to debug
  --help                  Show this message and exit.
```

Note that after building, the image is tested to see if it follow isquare nomenclature. 

If the command ends correctly, you can directly push the image to your docker registry 
(only dockerhub and gitlab are supported for now) and use it on isquare.

## test

If you just want to test an image without rebuilding it completely you can just use the 
following command:

```bash
Usage: i2py test [OPTIONS] TAG

  Verify that an docker image matches the isquare standard.

Options:
  --debug  Increase logging verbosity level to debug
  --help   Show this message and exit.
```

## infer

The `i2py infer` command is used to send the data to your models running on isquare:

```bash
Usage: i2py infer [OPTIONS] DATA

  Send data for inference.

Options:
  --url TEXT         url given by isquare.  [required]
  --access-key TEXT  Access key provided by isquare.  [required]
  --save-path TEXT   Path to save your data (img,txt or json).
  --help             Show this message and exit.
```

The DATA entry is the path to your data. Accepted data formats are images (.png, .jpeg &.jpg), text documents (.txt) and jsons (.json).
The url is your model url, which is obtained via `isquare.ai`, where you can also create an access key.
The save path can be used to save your results. Attention! If no save path is specified, the response will either be printed in the terminal or shown on the screen (if the result is an image). The save formats are the same as the loading formats.

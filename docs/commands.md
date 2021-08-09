# i2

`i2`, for isquare, is the name of the general command used for the client:

```bash
Usage: i2 [OPTIONS] COMMAND [ARGS]...

  Command line interface for isquare.

Options:
  --verbose  Increase logging depth
  --help     Show this message and exit.

Commands:
  infer  Send data for inference.
  test   Test the build of your worker before uploading to isquare.
```

## infer

The `i2 infer` command is used to send the data to your models running on isquare:

```bash
Usage: i2 infer [OPTIONS] DATA

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

## test

The `i2 test` command is used to check wether your model will run without errors on isquare. It simulates the build and an inference. In this way, we hope to save you a lot of time, by pushing only functional code to isquare.ai!

```bash
Usage: i2 test [OPTIONS] COMMAND [ARGS]...

  Test the build of your worker before uploading to isquare.

Options:
  --help  Show this message and exit.

Commands:
  worker  Test the build and logic of a worker before deploying on archipel.
```

For the moments, only workers can be tested:

```bash
Usage: i2 test worker [OPTIONS] TASK_SCRIPT

  Test the build and logic of a worker before deploying on archipel.

Options:
  --dockerfile PATH  Provide a dockerfile path
  --task_name TEXT
  --cpu              Force only CPU mode
  --no-cache         Do not use cached files for build
  --help             Show this message and exit.
```

The options are the same when deploying to `isquare.ai`

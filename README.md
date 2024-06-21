# Yarn: A YAML to Release Note generator :yarn:

There's only one [file](yarn/yarn.py), so read it if you want the docs.

## Install

``` bash
pip3 install git+https://github.com/biosafetylvl5/yarn.git
```

or

``` bash
pip install git+https://github.com/biosafetylvl5/yarn.git
```

## Usage

``` bash
pink file.rst # to process individual file
```

``` bash
pink --max-line-length 100 file.rst # set max line length
```

``` bash
pink # to process files in dir and recursively processes sub-folder files
```

``` bash
pink --no-recurse # to process files in dir WITHOUT recusion
```

``` bash
# to process files recursively in dir WITHOUT ensuring there's a trailing newline at the end of files
pink --disable-trailing-newline
```

``` bash
 # or go crazy, see next section
pink --no-recurse --disable-replace-tabs --spaces-per-tab 4 --disable-smart-wrap --max-line-length 100 directory/
```

### CLI Arguments

| Argument                          | Description                                                               |
|-----------------------------------|---------------------------------------------------------------------------|
| `-h, --help`                      | Show help message and exit.                                               |
| `-y, --write-yaml-template` | |
| `-v, --version` | |
| `-r, --release-date` | |
| `-nc, --no-color` | |
| `-p, --prefix-file` | |
| `-s, --suffix-file` | |
| `-o, --output-file` | |
| `-nr, --no-rich` | |
| `-q, --quiet` | |


Positional Arguments:
  input_files_or_folders
                        The folder(s) containing YAML files and/or YAML files. Folders will be searched
                        recursively.

Optional Arguments:
  -h, --help            show this help message and exit
  -t, --write-yaml-template [WRITE_YAML_TEMPLATE]
                        Write template YAML to provided file. If folder provided, place template in
                        folder with current git branch name as file name.
  -v, --version VERSION
                        Version number of the release. Default is '[UNKNOWN]'.
  -r, --release-date RELEASE_DATE
                        Date of the release. Default is current system time.
  -nc, --no-color       Disable text formatting for CLI output.
  -p, --prefix-file PREFIX_FILE
                        A header file to prepend to the release notes.
  -s, --suffix-file SUFFIX_FILE
                        A footer file to suffix to the release notes.
  -o, --output-file OUTPUT_FILE
                        The output file for release notes.
  -nr, --no-rich        Disable rich text output
  -q, --quiet           Only output errors

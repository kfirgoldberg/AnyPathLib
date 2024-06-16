<p align="center"><img src="https://raw.githubusercontent.com/kfirgoldberg/AnyPathLib/master/docs/anypathlib_logo.png" alt="logo" width="70%" /></p>


<div align="center">

[![wsc_logo](https://raw.githubusercontent.com/kfirgoldberg/AnyPathLib/master/docs/wsc_logo.png)](https://wsc-sports.com/)

</div>

# AnyPathLib - Crossing Cloud Borders With a Simple API

<p align="center">
    <a href="https://badge.fury.io/py/AnyPathLib"><img src="https://badge.fury.io/py/AnyPathLib.svg" alt="PyPI version" height="18"></a>
    <a href="https://pepy.tech/project/anypathlib"><img src="https://pepy.tech/badge/anypathlib" alt="Downloads" height="18"></a>
    <a href="#contributors-"><img src="https://img.shields.io/badge/all_contributors-2-orange.svg" alt="All Contributors" height="18"></a>
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0" height="18"></a>
</p>


Welcome to AnyPathLib, a Python library designed to allow hassle-free file operations across different cloud and local
storage

## Why `AnyPathLib`?

With `AnyPathLib` you can write the same code to handle files across different storage systems, without worrying about
the
underlying details.
Operations can be optimized per-backend and the library is easily extendable to support additional cloud storage
providers.

## Getting Started With `AnyPathLib` with 3 easy examples ️🛣️

### ️🛣️ 1/3 Copying a file or directory from anywhere to anywhere ️🛣️

```python
from anypathlib import AnyPath

# Create an AnyPath instance for a local file
local_file = AnyPath("/path/to/local/file.txt")

# Create an AnyPath instance for an S3 object
s3_file = AnyPath("s3://bucket/path/to/object.txt")

# Copy a file from local to S3
local_file.copy(s3_file)

# Copy a directory from S3 to Azure
s3_dir = AnyPath("s3://bucket/path/to/dir")
azure_dir = AnyPath("https://account_name.blob.core.windows.net/container_name/path")
s3_dir.copy(azure_dir)
```

### ️🛣️ 2/3 Local caching for quicker access ️🛣️

Use "copy" without a target to get a local copy of the file which is stored in a local cache.
Use `force_overwrite=False` to prevent repeated downloads of the same file

```python
my_dir = AnyPath("https://account_name.blob.core.windows.net/container_name/path/to/dir")
local_dir_path = my_dir.copy()

my_file = AnyPath("s3://bucket/path/to/file.txt")
local_file_path = my_file.copy()
local_file_path = my_file.copy(force_overwrite=False)  # Returns the path of the previously downloaded file
```

### 🛣️ 3/3 A simplified pathlib-like Interface 🛣️

```python
my_dir = AnyPath("https://account_name.blob.core.windows.net/container_name/path/to/dir")
my_dir.exists()  # True if my_path exists, otherwise False
parent, name, stem = my_dir.parent, my_dir.name, my_dir.stem
files_in_dir: List[AnyPath] = my_dir.rglob('*')  # List of AnyPath instances for files in the directory

my_file = AnyPath("s3://bucket/path/to/file.txt")
my_file.is_file()  # True if my_path exists, otherwise False
my_file.is_dir()  # False
my_file.remove()
```

### CLI Usage

`AnyPathLib` also comes with a CLI tool that allows you to perform file operations from the command line.
You can run `anypathlib --help` to get a list of available commands and options.

Here are some examples:

Copy:
```bash
anypathlib copy -i /path/to/source -o /path/to/destination
```

Remove a file or directory:
```bash
anypathlib remove -p /path/to/file_or_directory
```

### Key Features

* **Unified, Cloud Agnostic, API**: Perform file operations across different storage backends using the same set of
  methods.
* **Path-like Operations**: Supports common path operations like joining paths, listing directories, checking file
  existence, etc.
* **Performance**: Local caching for repeated downloads across different sessions, multithreading, and more.
* **Extensibility**: Easily extendable to support additional cloud storage providers.

### Security and Credentials

`AnyPath` does not store any credentials in it. In order to access cloud storage, you need to have the necessary
environment variables defined.

#### Azure

```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_RESOURCE_GROUP_NAME="your-resource-group-name"
```

#### AWS S3

Same as Boto3:

```bash
export AWS_DEFAULT_REGION="your-region"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_ACCESS_KEY_ID="your-key"
```

# TODOs:

- [ ] Add support for additional cloud storage providers.

> GCP

- [ ] Improve API

> Add support for file-to-dir in copy

- [ ] Implement cloud-to-cloud ops more efficiently.

> For example, s3->azure can use AZCopy

- [ ] Improve logging and add verbose mode.

> progress bar, etc.

## Contributors ✨

Thanks goes to these wonderful people:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/shomerYu"><img src="https://avatars.githubusercontent.com/u/49059794?v=4" width="100px;" alt=""/><br /><sub><b>Yuval Shomer</b></sub></a><br /><a href="#design-shomerYu" title="Design">🎨</a> <a href="#ideas-shomerYu" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/jeremy-levy"><img src="https://avatars.githubusercontent.com/u/61752548?v=4" width="100px;" alt=""/><br /><sub><b>Jeremy Levy</b></sub></a><br /><a href="#design-jeremy-levy" title="Design">🎨</a> <a href="#ideas-jeremy-levy" title="Ideas, Planning, & Feedback">🤔</a></td>


  </tr>
</table>

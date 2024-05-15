import random
import string

import pytest
from pathlib import Path
import tempfile

from anypathlib import PathType
from tests.tests_urls import PATH_TYPE_TO_BASE_TEST_PATH, PATH_TYPE_TO_HANDLER


def create_files_in_directory(directory: Path, n_files: int = 5):
    for _ in range(n_files):
        # Generate a random file name
        file_name = ''.join(random.choices(string.ascii_lowercase, k=10)) + '.txt'
        file_path = directory / file_name

        # Write some random short content to each file
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        file_path.write_text(content)


@pytest.fixture
def temp_dir_with_files():
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        create_files_in_directory(tmpdir)
        yield tmpdir, list(tmpdir.iterdir())


@pytest.fixture
def temp_nested_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        nested = tempfile.TemporaryDirectory(dir=tmpdirname)
        create_files_in_directory(tmpdir)
        create_files_in_directory(Path(nested.name))
        yield tmpdir, list(tmpdir.iterdir()), list(Path(nested.name).iterdir())

        # yield tmpdir, [fn for fn in tmpdir.iterdir() if fn.is_file()], [fn for fn in Path(nested.name).iterdir() if
        #                                                                 fn.is_file()]


@pytest.fixture
def temp_local_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def clean_remote_dir(request, path_type: PathType):
    test_name = request.node.name
    remote_base_dir = PATH_TYPE_TO_BASE_TEST_PATH[path_type]
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    remote_dir = f"{remote_base_dir}{test_name}/"
    cloud_handler.remove(remote_dir)
    yield remote_dir
    cloud_handler.remove(remote_dir)

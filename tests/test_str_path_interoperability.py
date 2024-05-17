from pathlib import Path

import pytest

from anypathlib import AnyPath, PathType
from fixtures_anypath import temp_local_dir, temp_dir_with_files, clean_remote_dir
from tests.tests_urls import PATH_TYPE_TO_HANDLER


def test_init_anypath_from_anypath(tmpdir):
    tmpdir_str = str(Path(tmpdir.dirname))
    local_path = AnyPath(tmpdir_str)
    local_path_init_from_anypath = AnyPath(local_path)
    assert local_path_init_from_anypath.base_path == local_path.base_path
    local_path_init_from_path = AnyPath(Path(tmpdir_str))
    assert local_path_init_from_path.base_path == local_path.base_path


@pytest.mark.usefixtures("temp_dir_with_files", "temp_local_dir", "clean_remote_dir")
@pytest.mark.parametrize("target_type", [str, Path, AnyPath])
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3])
def test_copy_targets(path_type: PathType, target_type, temp_dir_with_files, temp_local_dir, clean_remote_dir):
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_dir_files = temp_dir_with_files
    temp_local_dir = target_type(temp_local_dir)
    remote_dir = clean_remote_dir
    cloud_handler.upload_directory(local_dir=local_dir_path, target_url=remote_dir, verbose=False)
    local_download_dir = AnyPath(remote_dir).copy(target=temp_local_dir, force_overwrite=True)
    remote_files = AnyPath(remote_dir).listdir()
    assert sorted([fn.name for fn in remote_files]) == sorted([fn.name for fn in local_download_dir.listdir()])

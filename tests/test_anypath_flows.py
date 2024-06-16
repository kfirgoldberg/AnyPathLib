import pytest

from anypathlib import PathType, AnyPath
from tests.tests_urls import PATH_TYPE_TO_HANDLER
from fixtures_anypath import temp_dir_with_files, clean_remote_dir


@pytest.mark.usefixtures("temp_dir_with_files", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3, PathType.local])
def test_exists_copy_exists_rglob_remove_exists(path_type: PathType, temp_dir_with_files, clean_remote_dir):
    remote_base_dir = clean_remote_dir
    local_dir_path, local_dir_files = temp_dir_with_files
    remote_dir = remote_base_dir + 'test_exists_copy_exists_rglob_remove_exists/'
    local_any_path = AnyPath(local_dir_path)
    target_any_path = AnyPath(remote_dir)
    assert not target_any_path.exists()
    local_any_path.copy(target=target_any_path, force_overwrite=True)
    assert target_any_path.exists()
    target_dir_files = target_any_path.rglob('*')
    assert sorted([remote_file.name for remote_file in target_dir_files]) == sorted(
        [local_dir_file.name for local_dir_file in local_dir_files])
    target_any_path.remove()
    assert not target_any_path.exists()


@pytest.mark.usefixtures("temp_dir_with_files", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3, PathType.local])
def test_is_dir(path_type: PathType, temp_dir_with_files, clean_remote_dir):
    local_dir_path, local_dir_files = temp_dir_with_files
    remote_dir = clean_remote_dir
    remote_dir_any_path = AnyPath(remote_dir)
    assert not remote_dir_any_path.is_dir()
    assert not remote_dir_any_path.is_file()
    AnyPath(local_dir_path).copy(target=remote_dir_any_path, force_overwrite=True)
    assert remote_dir_any_path.is_dir()
    assert not remote_dir_any_path.is_file()
    remote_dir_any_path.remove()
    assert not remote_dir_any_path.exists()
    assert not remote_dir_any_path.is_dir()


@pytest.mark.usefixtures("temp_dir_with_files", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3, PathType.local])
def test_is_file(path_type: PathType, temp_dir_with_files, clean_remote_dir):
    local_dir_path, local_dir_files = temp_dir_with_files
    local_file = local_dir_files[0]
    remote_dir = clean_remote_dir
    remote_file = f'{remote_dir}/{local_file.name}'
    remote_file_any_path = AnyPath(remote_file)
    assert not remote_file_any_path.is_dir()
    assert not remote_file_any_path.is_file()
    AnyPath(local_file).copy(target=remote_file_any_path)
    assert not remote_file_any_path.is_dir()
    assert remote_file_any_path.is_file()
    remote_file_any_path.remove()
    assert not remote_file_any_path.exists()
    assert not remote_file_any_path.is_file()


@pytest.mark.usefixtures("clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3, PathType.local])
@pytest.mark.parametrize("verbose", [True, False])
def test_caching(path_type: PathType, temp_dir_with_files, clean_remote_dir, verbose: bool):
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_dir_files = temp_dir_with_files
    remote_dir = clean_remote_dir
    cloud_handler.upload_directory(local_dir=local_dir_path, target_url=remote_dir, verbose=verbose)
    target1 = AnyPath(remote_dir).copy(target=None, force_overwrite=False, verbose=verbose)
    target2 = AnyPath(remote_dir).copy(target=None, force_overwrite=False, verbose=verbose)
    target1.remove()
    if target2.exists():
        target2.remove()
    assert target1.base_path == target2.base_path

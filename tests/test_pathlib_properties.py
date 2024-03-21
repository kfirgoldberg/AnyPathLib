from anypathlib import AnyPath


def test_pathlib_properties():
    s3_test_dir = AnyPath(r's3://bucket/AnyPath/tests/')
    assert s3_test_dir.stem == 'tests'
    assert s3_test_dir.name == 'tests'
    assert s3_test_dir.parent.base_path == AnyPath(r's3://bucket/AnyPath/').base_path

    s3_test_file = AnyPath(r's3://bucket/AnyPath/tests/a.txt')
    assert s3_test_file.stem == 'a'
    assert s3_test_file.name == 'a.txt'
    assert s3_test_file.parent.base_path == AnyPath(r's3://bucket/AnyPath/tests/').base_path

    azure_test_dir = AnyPath(r'https://storage_account.blob.core.windows.net/container/AnyPath/tests/')
    assert azure_test_dir.stem == 'tests'
    assert azure_test_dir.name == 'tests'
    assert azure_test_dir.parent.base_path == AnyPath(
        r'https://storage_account.blob.core.windows.net/container/AnyPath/').base_path

    azure_test_file = AnyPath(r'https://storage_account.blob.core.windows.net/container/AnyPath/tests/a.txt')
    assert azure_test_file.stem == 'a'
    assert azure_test_file.name == 'a.txt'
    assert azure_test_file.parent.base_path == AnyPath(
        r'https://storage_account.blob.core.windows.net/container/AnyPath/tests/').base_path

    local_test_dir = AnyPath(r'/tmp/AnyPath/tests/')
    assert local_test_dir.stem == 'tests'
    assert local_test_dir.name == 'tests'
    assert local_test_dir.parent.base_path == AnyPath(r'/tmp/AnyPath').base_path

    local_test_file = AnyPath(r'/tmp/AnyPath/tests/a.txt')
    assert local_test_file.stem == 'a'
    assert local_test_file.name == 'a.txt'
    assert local_test_file.parent.base_path == AnyPath(r'/tmp/AnyPath/tests').base_path

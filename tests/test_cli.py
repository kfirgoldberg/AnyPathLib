from pathlib import Path

import pytest

from anypathlib.cli import cli

FOLDER_NAME = 'folder'


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_copy_command_success(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]

    output_path = local_dir_path / FOLDER_NAME / input_file.name

    result = cli_runner.invoke(cli, ['copy', '-i', local_dir_files[0], '-o', output_path])
    assert result.exit_code == 0
    assert output_path.exists()


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_copy_command_without_output(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]

    result = cli_runner.invoke(cli, ['copy', '-i', input_file])
    assert result.exit_code == 0
    output_path = result.output.split(" ")[-1]
    assert Path(output_path.strip()).exists()


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_exists_command_true(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]
    result = cli_runner.invoke(cli, ['exists', '-p', input_file])
    assert result.exit_code == 0
    assert 'True' in result.output


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_exists_command_false(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]
    input_file.unlink()
    result = cli_runner.invoke(cli, ['exists', '-p', input_file])
    assert result.exit_code == 0
    assert 'False' in result.output


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_iterdir_command_with_files(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    result = cli_runner.invoke(cli, ['iterdir', '-p', local_dir_path])
    assert result.exit_code == 0

    for file in local_dir_files:
        assert file.name in result.output


@pytest.mark.usefixtures("temp_local_dir", 'cli_runner')
def test_iterdir_command_empty(temp_local_dir, cli_runner):
    result = cli_runner.invoke(cli, ['iterdir', '-p', temp_local_dir])
    assert result.exit_code == 0
    assert result.output.strip() == '[]'


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_remove_command_success(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]

    result = cli_runner.invoke(cli, ['remove', '-p', input_file])
    assert result.exit_code == 0
    assert not input_file.exists()


@pytest.mark.usefixtures("temp_dir_with_files", 'cli_runner')
def test_remove_command_non_existing_path(temp_dir_with_files, cli_runner):
    local_dir_path, local_dir_files = temp_dir_with_files
    input_file = local_dir_files[0]

    result = cli_runner.invoke(cli, ['remove', '-p', input_file])
    assert result.exit_code == 0

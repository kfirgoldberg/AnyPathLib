import click
from anypathlib import AnyPath


@click.group()
def cli():
    pass


@click.command()
@click.option('-i', '--input', 'input_path', required=True, type=click.STRING, help='Input path to copy from')
@click.option('-o', '--output', 'output_path', type=click.STRING, help='Output path to copy to')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbose flag')
@click.option('-f', '--force/--no-force', is_flag=True, default=True, help='Force overwrite flag')
def copy(input_path, output_path, verbose, force):
    """Copy files from input to output path. """
    AnyPath(input_path).copy(target=AnyPath(output_path) if output_path else None,
                             verbose=verbose, force_overwrite=force)


@click.command()
@click.option('-p', '--path', required=True, type=click.STRING, help='Path to check')
def exists(path):
    """Check if the path exists. """
    print(AnyPath(path).exists())


@click.command()
@click.option('-p', 'path', required=True, type=click.STRING, help='Path to list')
def listdir(path):
    """List the directory. """
    print(AnyPath(path).listdir())


@click.command()
@click.option('-p', 'path', required=True, type=click.STRING, help='Path to remove')
def remove(path):
    """Remove the path. """
    AnyPath(path).remove()


cli.add_command(copy)
cli.add_command(exists)
cli.add_command(listdir)
cli.add_command(remove)

if __name__ == '__main__':
    cli()

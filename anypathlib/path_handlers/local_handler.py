import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from anypathlib.path_handlers.base_path_handler import BasePathHandler


class LocalPathHandler(BasePathHandler):

    @classmethod
    def is_dir(cls, url: str) -> bool:
        return Path(url).is_dir()

    @classmethod
    def is_file(cls, url: str) -> bool:
        return Path(url).is_file()

    @classmethod
    def exists(cls, url: str) -> bool:
        return Path(url).exists()

    @classmethod
    def remove(cls, url: str):
        local_path = Path(url)
        if local_path.is_file():
            local_path.unlink()
        elif local_path.is_dir():
            shutil.rmtree(local_path)

    @classmethod
    def upload_file(cls, local_path: str, target_url: str):
        cls.copy_path(url=Path(local_path).absolute().as_posix(), target_path=Path(target_url), force_overwrite=True)

    @classmethod
    def upload_directory(cls, local_dir: Path, target_url: str, verbose: bool):
        cls.copy_path(url=local_dir.absolute().as_posix(), target_path=Path(target_url), force_overwrite=True)

    @classmethod
    def copy(cls, source_url: str, target_url: str):
        cls.copy_path(url=source_url, target_path=Path(target_url), force_overwrite=True)

    @classmethod
    def copy_path(cls, url: str, target_path: Path, force_overwrite: bool = True) -> Path:
        if target_path.exists() and not force_overwrite:
            return target_path
        if target_path.exists() and force_overwrite:
            cls.remove(url=target_path.as_posix())
        local_path = Path(url)
        if local_path.is_dir():
            shutil.copytree(local_path, target_path)
        else:
            shutil.copy(local_path, target_path)

    @classmethod
    def download_directory(cls, url: str, force_overwrite: bool, target_dir: Path, verbose: bool) -> \
            Optional[Tuple[Path, List[Path]]]:
        cls.copy_path(url=url, target_path=target_dir, force_overwrite=force_overwrite)
        return target_dir, [p for p in target_dir.rglob('*')]

    @classmethod
    def download_file(cls, url: str, target_path: Path, force_overwrite: bool = True) -> Path:
        return cls.copy_path(url=url, target_path=target_path, force_overwrite=force_overwrite)

    @classmethod
    def listdir(cls, url: str) -> List[str]:
        return [str(p) for p in Path(url).rglob('*')]

    @classmethod
    def relative_path(cls, url: str) -> str:
        return Path(url).relative_to(Path(url).anchor).as_posix()

    @classmethod
    def parent(cls, url: str) -> str:
        return Path(url).parent.as_posix()

    @classmethod
    def stem(cls, url: str) -> str:
        return Path(url).stem

    @classmethod
    def name(cls, url: str) -> str:
        return Path(url).name

    @classmethod
    def iterdir(cls, url: str) -> List[str]:
        return [str(p) for p in Path(url).iterdir()]

    @classmethod
    def glob(cls, url: str, pattern: str) -> List[str]:
        return [str(p) for p in Path(url).glob(pattern)]

    @classmethod
    def rglob(cls, url: str, pattern: str) -> List[str]:
        return [str(p) for p in Path(url).rglob(pattern)]

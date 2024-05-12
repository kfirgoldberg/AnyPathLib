from abc import abstractmethod, ABC
from pathlib import Path
from typing import List, Optional, Tuple


class BasePathHandler(ABC):
    @classmethod
    @abstractmethod
    def download_file(cls, url: str, target_path: Path, force_overwrite: bool = True) -> Path:
        pass

    @classmethod
    @abstractmethod
    def listdir(cls, url: str) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def remove(cls, url: str):
        pass

    @classmethod
    @abstractmethod
    def download_directory(cls, url: str, force_overwrite: bool, target_dir: Path,
                           verbose: bool) -> Optional[Tuple[Path, List[Path]]]:
        pass

    @classmethod
    @abstractmethod
    def upload_file(cls, local_path: str, target_url: str):
        pass

    @classmethod
    @abstractmethod
    def upload_directory(cls, local_dir: Path, target_url: str, verbose: bool):
        pass

    @classmethod
    @abstractmethod
    def copy(cls, source_url: str, target_url: str):
        pass

    @classmethod
    @abstractmethod
    def is_dir(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def is_file(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def exists(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def relative_path(cls, url: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def parent(cls, url: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def name(cls, url: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def stem(cls, url: str) -> str:
        pass

    @classmethod
    @abstractmethod
    def iterdir(cls, url: str) -> List[str]:
        """
        Lists all files and directories directly under the given directory
        """
        pass

    @classmethod
    @abstractmethod
    def glob(cls, url: str, pattern: str) -> List[str]:
        """
        Finds all the paths matching a specific pattern, which can include wildcards, but does not search recursively
        """
        pass

    @classmethod
    @abstractmethod
    def rglob(cls, url: str, pattern: str) -> List[str]:
        """
        Finds all the paths matching a specific pattern, including wildcards, and searches recursively in all subdirectories
        """
        pass

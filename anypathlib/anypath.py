import shutil
import tempfile
from pathlib import Path, PurePath
from typing import Union, Optional, List, Dict
from urllib.parse import urlparse

from anypathlib.path_handlers.azure_handler import AzureHandler
from anypathlib.path_handlers.base_path_handler import BasePathHandler
from anypathlib.path_handlers.local_handler import LocalPathHandler
from anypathlib.path_handlers.path_types import PathType
from anypathlib.path_handlers.s3_handler import S3Handler


class AnyPath:
    PATH_HANDLERS: Dict[PathType, BasePathHandler] = {PathType.local: LocalPathHandler,
                                                      PathType.s3: S3Handler,
                                                      PathType.azure: AzureHandler}
    LOCAL_CACHE_PATH = Path(tempfile.gettempdir()) / 'AnyPath'

    def __init__(self, base_path: Union[Path, str]):
        if type(base_path) is str:
            self._base_path = base_path
        elif issubclass(type(base_path), PurePath):
            self._base_path = base_path.absolute().as_posix()
        else:
            raise ValueError(f'base_path must be of type str or Path, got {type(base_path)}')
        self.path_type = self.get_path_type(self._base_path)
        self.path_handler = self.PATH_HANDLERS[self.path_type]

    @staticmethod
    def get_path_type(url: str) -> PathType:
        parsed_url = urlparse(url)
        if parsed_url.scheme in ['http', 'https']:
            if 'blob.core.windows.net' in parsed_url.netloc:
                return PathType.azure
            elif 'amazonaws.com' in parsed_url.netloc or 's3' in parsed_url.netloc:
                return PathType.s3
        elif parsed_url.scheme in ['s3']:
            return PathType.s3
        elif parsed_url.scheme in ['file', '']:
            return PathType.local
        else:
            # Assume local
            return PathType.local

    def __repr__(self):
        return self.base_path

    @property
    def is_s3(self) -> bool:
        return self.path_type == PathType.s3

    @property
    def is_local(self) -> bool:
        return self.path_type == PathType.local

    @property
    def is_azure(self) -> bool:
        return self.path_type == PathType.azure

    # define truediv to allow for concatenation
    def __truediv__(self, other: str) -> 'AnyPath':
        if self.is_local:
            return AnyPath(Path(self.base_path) / other)
        else:
            valid_other = other[1:] if other.startswith('/') else other
            valid_base = self.base_path if self.base_path.endswith('/') else self.base_path + '/'

            return AnyPath(f'{valid_base}{valid_other}')

    @property
    def base_path(self) -> str:
        if self.path_type == PathType.s3:
            base_path = self._base_path
            base_path = base_path.replace('//', '/')
            if base_path.startswith('s3:/') and not base_path.startswith('s3://'):
                base_path = base_path.replace('s3:/', 's3://')
            if base_path[-1] == '/':
                base_path = base_path[:-1]
        else:
            base_path = self._base_path
        return base_path

    def is_dir(self) -> bool:
        return self.path_handler.is_dir(self.base_path)

    def is_file(self) -> bool:
        return self.path_handler.is_file(self.base_path)

    def exists(self) -> bool:
        return self.path_handler.exists(self.base_path)

    def listdir(self) -> List['AnyPath']:
        return [AnyPath(p) for p in self.path_handler.listdir(self.base_path)]

    def remove(self):
        self.path_handler.remove(self.base_path)

    @property
    def parent(self) -> 'AnyPath':
        return AnyPath(self.path_handler.parent(self.base_path))

    @property
    def stem(self) -> str:
        return self.path_handler.stem(self.base_path)

    @property
    def name(self) -> str:
        return self.path_handler.name(self.base_path)

    def __get_local_path(self, target_path: Optional[Path] = None, force_overwrite: bool = False,
                         verbose: bool = True) -> Optional[Path]:
        if target_path is None:
            if self.is_dir():
                valid_target_path = Path(tempfile.mkdtemp())
            else:
                valid_target_path = Path(tempfile.mktemp())
        else:
            if target_path.exists():
                assert target_path.is_dir() == self.is_dir()
                assert target_path.is_file() == self.is_file()
            valid_target_path = target_path
        if self.path_type == PathType.local:
            if not target_path.exists() or force_overwrite:
                if self.is_dir():
                    shutil.copytree(self.base_path, valid_target_path, dirs_exist_ok=True)
                else:
                    Path(valid_target_path).parent.mkdir(exist_ok=True, parents=True)
                    shutil.copy(self.base_path, valid_target_path)
            return valid_target_path
        else:
            if self.is_dir():
                result = self.path_handler.download_directory(url=self.base_path,
                                                              force_overwrite=force_overwrite,
                                                              target_dir=valid_target_path,
                                                              verbose=verbose)
                if result is not None:
                    local_path, _ = result
                else:
                    return None

            else:
                local_path = self.path_handler.download_file(url=self.base_path, force_overwrite=force_overwrite,
                                                             target_path=valid_target_path)

        assert local_path == valid_target_path, \
            f'local_path {local_path} is not equal to valid_target_path {valid_target_path}'
        return Path(local_path)

    def __get_local_cache_path(self) -> 'AnyPath':
        handler_prefix = 's3' if self.is_s3 else 'azure' if self.is_azure else 'local'
        local_cache_path = self.LOCAL_CACHE_PATH / handler_prefix / self.path_handler.relative_path(self.base_path)
        if self.is_dir():
            local_cache_path.mkdir(exist_ok=True, parents=True)
        elif self.is_file():
            local_cache_path.parent.mkdir(exist_ok=True, parents=True)
        return AnyPath(local_cache_path)

    def copy(self, target: Optional['AnyPath'] = None, force_overwrite: bool = True, verbose: bool = True) -> 'AnyPath':
        assert self.exists(), f'source path: {self.base_path} does not exist'
        if target is None:
            valid_target = self.__get_local_cache_path()
        else:
            valid_target = target
        if valid_target.is_local:
            self.__get_local_path(target_path=Path(valid_target.base_path), force_overwrite=force_overwrite,
                                  verbose=verbose)
        else:
            if valid_target.is_s3 and self.is_s3:
                S3Handler.copy(source_url=self.base_path, target_url=valid_target.base_path)
            elif valid_target.is_azure and self.is_azure:
                AzureHandler.copy(source_url=self.base_path, target_url=valid_target.base_path)
            else:
                # valid_target and source are different,
                # so we need to download the source and upload it to the valid_target

                local_path = Path(self.base_path) if self.is_local else self.__get_local_path(
                    force_overwrite=force_overwrite, verbose=verbose)
                target_path_handler = valid_target.path_handler
                if self.is_dir():
                    target_path_handler.upload_directory(local_dir=local_path, target_url=valid_target.base_path,
                                                         verbose=verbose)
                else:
                    target_path_handler.upload_file(local_path=str(local_path), target_url=valid_target.base_path)
        return valid_target

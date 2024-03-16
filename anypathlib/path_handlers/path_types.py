from enum import Enum


class PathType(Enum):
    local = 'local'
    s3 = 's3'
    azure = 'azure'

# Version 0.2.0
 - Type `AnyPathLikeType` was added, which can be used to init an `AnyPath` instance or in `copy` target
 - `listdir` is now deprecated, replaced by `iterdir`, `rglob`, and `glob`
 - `copy` not supports the case where the source is a file and target is a directory
import sys
import setuptools
import codecs
import os
import re

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
packages = setuptools.find_namespace_packages(include=["anypathlib*"])
print("PACKAGES FOUND:", packages)
print(sys.version_info)


def find_version(*file_paths: str) -> str:
    with codecs.open(os.path.join(*file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="AnyPathLib",
    version=find_version("anypathlib", "__init__.py"),
    author="Kfir Goldberg @ WSC-Sports",
    description="A unified API for every storage resource",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=packages,
    package_data={"AnyPathLib": ["py.typed"]},
    license='Apache License 2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: Apache Software License',
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "azure-storage-blob>=12.14.0",
        "azure-identity>=1.15.0",
        "azure-mgmt-storage>=21.1.0",
        "boto3>=1.34.23",
        "loguru>=0.7.2",
        'Click'
    ],
    setup_requires=["pre-commit"],
    py_modules=["anypathlib"],
    entry_points={"console_scripts": ["anypathlib = anypathlib.cli:cli"]}
)

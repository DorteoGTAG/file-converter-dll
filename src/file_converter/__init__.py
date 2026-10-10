[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "file-converter"
version = "0.1.0"
description = "A small converter and inspector for raw binary, HEX, Base64, and Windows PE files"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "pefile>=2023.2.7",
]

[project.scripts]
file-converter = "file_converter.cli:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

""" setup.py """
from setuptools import setup
from Cython.Build import cythonize
from pathlib import Path

FILES_TO_CYTHONIZE = [str(i) for i in list(Path("src").glob("aihybridmodelworkflow/**/*.py"))]


setup(
    ext_modules=cythonize(
    FILES_TO_CYTHONIZE,
    build_dir="build",
    compiler_directives=dict(always_allow_keywords=True, language_level="3"),
    ),
)
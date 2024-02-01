""" setup.py """
import os
from pathlib import Path
import shutil
import stat

from setuptools import setup
from setuptools.command.build_py import build_py as build_py_original
from Cython.Build import cythonize

project_path = Path(__file__).parent
FILES_TO_CYTHONIZE = [str(i) for i in list(Path("src").glob("pkg_name/**/*.py"))]

# ------------------------------------------------------------------------------------
# To exclude source files (*.py) into the final *whl file
# ------------------------------------------------------------------------------------
class build_py(build_py_original):
    def build_packages(self):
        pass 

# ------------------------------------------------------------------------------------
# Versioning
# ------------------------------------------------------------------------------------
"""
Please use semantic versioning (https://semver.org/)
MAJOR.MINOR.PATCH-rc.PRERELEASE+build.BUILD
Increment criteria:
    MAJOR - when you make incompatible API changes
    MINOR - when you add functionality in a backwards compatible manner
    PATCH - when you make backwards compatible bug fixes
    PRELEASE - release candidates
    BUILD - (do not use)
"""
module_info = {}
with open(Path("src/pkg_name/__init__.py"), "r") as f:
    exec(f.read(), module_info)                         # exec() to execute code that comes as strings or compiled code objects
VERSION = module_info["__version__"]

# ------------------------------------------------------------------------------------
# Main setup( ) call
# ------------------------------------------------------------------------------------
setup(
    version=VERSION,
    ext_modules=cythonize(
    FILES_TO_CYTHONIZE,
    build_dir="build",
    compiler_directives=dict(always_allow_keywords=True, language_level="3"),
    ),
    cmdclass={"build_py": build_py},
)


# ------------------------------------------------------------------------------------
# For cleaning (after-build-mess) purpose
# Many files and directories will get build (some of them have very userful info)
# But we want to clean them. For the Debug purpsose we might want to keep these files
# ------------------------------------------------------------------------------------

def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def remove_dirs_and_files(rm_dist_folder=False):
    """
    Removing unnecessary files upon a build. For more insight, I can turn this call off, and then look at 
    all files created here.
    """
    remove_dirs = []
    remove_dirs = [Path(project_path, "build")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.exp")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.pyd")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.lib")]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("**/*.so")]
    if rm_dist_folder:
        remove_dirs += [str(f) for f in Path(project_path).glob(f"*{0}".format("dist"))]
    remove_dirs += [str(f) for f in Path(project_path, "src").glob("*{0}".format("egg-info"))]

    for d in remove_dirs:
        if os.path.isdir(d):
            shutil.rmtree(d, onerror=on_rm_error)
        elif os.path.isfile(d):
            os.remove(d)

remove_dirs_and_files(rm_dist_folder=False)

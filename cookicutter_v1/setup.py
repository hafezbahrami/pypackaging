""" setup.py """
import os
from pathlib import Path
import shutil
import stat

from setuptools import setup
from Cython.Build import cythonize

project_path = Path(__file__).parent
FILES_TO_CYTHONIZE = [str(i) for i in list(Path("src").glob("pkg_name/**/*.py"))]


setup(
    ext_modules=cythonize(
    FILES_TO_CYTHONIZE,
    build_dir="build",
    compiler_directives=dict(always_allow_keywords=True, language_level="3"),
    ),
)


# --------------------------------------------------------------------------------

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

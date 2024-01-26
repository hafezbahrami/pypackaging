import os, sys, shutil
from pathlib import Path
import re # Regular Expression
import invoke
from invoke.context import Context

# from setup import on_rm_error


@invoke.task
def validate(context: Context):
    """Validate the project from static-type checking, Linting the scripts, ...."""
    context.run("pyflakes .", echo=True)
    context.run("black --check --diff --verbose .", echo=True)

    def do_linting(path):
        """Run the PyLint for the given path, i.e. for the main project folder and test folder"""

        pylint_ret = context.run(f"pylint {path}", warn=True, echo=True).exited
        if pylint_ret and (1 & pylint_ret or 2 & pylint_ret or 32 & pylint_ret):
            print(f"pylint exit code: {pylint_ret}")
            sys.exit(pylint_ret)
    
    do_linting("./src")
    do_linting("./test")

    context.run("mypy --install-types --non-interactive ./src", echo=True)
    context.run("mypy --install-types --non-interactive ./test", echo=True)    


@invoke.task
def build(context: Context):
    """Build the wheel file of the package: Cythonizing the .py files and create *.so files and zip them into a wheel file"""
    print("*********************************************************************")
    context.run("python -m build . --wheel")


# -------------------------------------------------------------------------------------------------------------------
# More advanced stuff
# -------------------------------------------------------------------------------------------------------------------

# @invoke.task
# def clean(c, deps=False):
#     """
#     Clean task is used to clean up the repo and uninstall package.
#     """
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     for pattern in [
#         "dist/",
#         "build/",
#         ".mypy_cache",
#         ".pytest_cache/",
#         ".coverage",
#         "coverage.xml",
#         ".scannerwork",
#         ".idea",
#         ".vscode",
#         "src/modeling/__pycache__",
#         "test/__pycache__",
#         "temp_stub_project",
#     ]:
#         if os.path.isfile(os.path.join(current_dir, pattern)):
#             os.remove(os.path.join(current_dir, pattern))
#         elif os.path.isdir(os.path.join(current_dir, pattern)):
#             shutil.rmtree(os.path.join(current_dir, pattern), onerror=on_rm_error)

#     if deps:
#         c.run("pipenv clean")


# @invoke.task
# def setversion(context: Context):
#     """Sets __version__ in __init__.py files."""

#     # CI_COMMIT_TAG will be used to trigger release builds and specify version
#     __version__ = os.getenv("CI_COMMIT_TAG", "0.0.0rc0")

#     for dunderinitpy in Path("src").glob("**/__init__.py"):
#         dunderinitpy.write_text(
#             re.sub(
#                 r"__version__\ *=\ *\".+\"",
#                 f'__version__ = "{__version__}"',
#                 dunderinitpy.read_text(),
#             )
#         )

@invoke.task
def generatestubs(context: Context):
    # Publish a stubs package for development
    from publishstubs import StubProjectBuilder

    stub_project_builder = StubProjectBuilder(
        project_name="cookiecutter_v1",
        version="0.0.0rc0",             #os.getenv("CI_COMMIT_TAG", "0.0.0rc0"),
        package_names=["pkg_name"],
        project_root=Path.cwd(),
        package_directory=Path.cwd().joinpath("src"),
    )
    stub_whl = stub_project_builder.build_stubs_package()
    context.run("")


# @invoke.task
# def publish(context: Context, check_only=False):
#     """Publishes a release."""

#     # Set version
#     #setversion(context)
    
#     # Build
#     build(context)

#     # Install jfrog
#     # context.run("curl -fL https://getcli.jfrog.io/v2 | sh")
#     # context.run("export CI=True")

#     # Publish source package
#     publish = False
#     if publish:
#         repo_user = os.getenv("PKG_XXX_USERNAME")
#         repo_password = os.getenv("PKG_XXX_PASSWORD")
#         artifactory_url = f"https://{repo_user}:{repo_password}@artifactory.tools.XXX.YYY/artifactory"
#         artifactory_repo = "artifactory_name_XXXX/"
#         context.run(f"./jfrog rt ping --url={artifactory_url}")
#         for filepath in Path(Path(__file__).parent / "dist").glob("*.whl"):
#             context.run(f"./jfrog rt upload {filepath} {artifactory_repo} --url={artifactory_url}")

#     build_stubs(context)
#     #context.run(f"./jfrog rt upload {str(stub_whl)} {artifactory_repo} --url={artifactory_url}")


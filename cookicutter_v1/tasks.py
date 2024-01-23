import sys
import invoke
from invoke.context import Context

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
    context.run("python -m build . --wheel")
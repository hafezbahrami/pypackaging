"""
publishstubs.py

This script auto generates a separate stubs .whl file for a given project
"""
from __future__ import annotations
import sys, shutil
import subprocess
from pathlib import Path

from mypy import stubgen


class SetupTemplate:
    """
    Class to template setup.py information

    Attributes
    ----------
    name : `str`
    version : `str`
    description : `str`
    author : `str`
    author_email : `str`
    packages : `list[str]`
    package_dir : `dict[str, str]`
    install_requires : `str`
    python_requires : `str`
    include_package_data : `bool`
    zip_safe : `bool`
    """

    name: str
    version: str
    description: str
    author: str
    author_email: str
    packages: list[str]
    package_dir: dict[str, str]
    install_requires: str
    python_requires: str
    include_package_data: bool
    zip_safe: bool

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        author_email: str,
        packages: list[str],
        package_dir: dict[str, str],
        install_requires: str,
        python_requires: str,
        include_package_data: bool,
        zip_safe: bool,
    ) -> None:
        """
        Parameters
        ----------
        name : `str`
        version : `str`
        description : `str`
        author : `str`
        author_email : `str`
        packages : `list[str]`
        package_dir : `dict[str, str]`
        install_requires : `str`
        python_requires : `str`
        include_package_data : `bool`
        zip_safe : `bool`
        """
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.author_email = author_email
        self.packages = packages
        self.package_dir = package_dir
        self.install_requires = install_requires
        self.python_requires = python_requires
        self.include_package_data = include_package_data
        self.zip_safe = zip_safe

    @property
    def package_data(self) -> list[str]:
        """A list of the package contents"""
        return {p: ["*.pyi", "**/*.pyi"] for p in self.packages}

    @classmethod
    def from_project_information(
        cls,
        name: str,
        source_package_name: str,
        version: str,
        packages: list[str],
        package_dir: dict[str, str] = {"": "src"},
    ) -> "SetupTemplate":
        """
        Factory method to build from minimum project information needed. Aspen defults will be used
        to fill in less important package metadata.

        Parameters
        ----------
        name : `str`
            The name of the project.
        version : `str`
            Package version
        packages : `list[str]`
            The list of packages to generate stubs for
        package_dir : `dict[str, str]`
            The location of the packages source code. This has a default value for a src project layout, `{"": "src"}`

        Returns
        -------
        `SetupTemplate`
            Instance of a `SetupTemplate` class
        """

        _install_requires = f"{source_package_name}=={version}"

        return cls(
            name=name,
            version=version,
            description=f"Auto generated stubs for the {source_package_name} package.",
            author="Data Detector",
            author_email="esupport@gmail.com",
            packages=packages,
            package_dir=package_dir,
            install_requires=[_install_requires],
            python_requires=">=3.8",
            include_package_data=True,
            zip_safe=False,
        )

    def auto_generate_setup_script(self) -> str:
        """
        Converts class to setup.py file string

        Returns
        -------
        `str`
            string version of setup.py contents including new lines
        """

        s = "from setuptools import setup\n\n"
        s += "setup(\n"
        s += f"    name='{self.name}',\n"
        s += f"    version='{self.version}',\n"
        s += f"    description='{self.description}',\n"
        s += f"    author='{self.author}',\n"
        s += f"    author_email='{self.author_email}',\n"
        s += f"    packages={self.packages},\n"
        s += f"    package_dir={self.package_dir},\n"
        s += f"    install_requires={self.install_requires},\n"
        s += f"    python_requires='{self.python_requires}',\n"
        s += f"    include_package_data={self.include_package_data},\n"
        s += f"    package_data={self.package_data},\n"
        s += f"    zip_safe={self.zip_safe},\n"
        s += ")"

        return s


class StubProjectBuilder:
    """
    Class to autogenerate and package a stubs only project

    Attributes
    ----------
    project_name : `str`
        The name of the original source project without the "-stubs" suffix.
    version : `str`
        Current version of the source code.
    package_names : `list[str]`
        The list of packages to generate stubs for
    project_root : `Path`
        Path object representing the projects root directory.
    package_directory : `Path`
        Path object representing the directory containing the projects packages.
    """

    project_name: str
    version: str
    package_names: list[str]
    project_root: Path
    package_directory: Path

    def __init__(
        self,
        project_name: str,
        version: str,
        package_names: list[str],
        project_root: Path,
        package_directory: Path,
    ) -> None:
        """
        Parameters
        ----------
        project_name : `str`
            The name of the original source project. The "-stubs" suffix should not be included.
        version : `str`
            Current version of the source code.
        package_names : `list[str]`
            The list of packages to generate stubs for
        project_root : `Path`
            Path object representing the projects root directory.
        package_directory : `Path`
            Path object representing the directory containing the projects packages.
        """
        self.project_name = project_name
        self.version = version
        self.package_names = package_names
        self.project_root = project_root
        self.package_directory = package_directory

    def _bootstrap_stubs_project(self) -> Path:
        """
        Creats a stub packaging project inside the current project.

        Returns
        -------
        `Path`
            Path object representing the root of the new stubs project
        """
        # (a) Creating following directoris
        # Project Directory
        #    ├── temp_stub_project
        #       ├── src
        #       ├── stubs 
        stub_project_root = self.project_root.joinpath("temp_stub_project")
        stub_source = stub_project_root.joinpath("src")
        if not stub_project_root.exists():
            stub_project_root.mkdir()
        if not stub_source.exists():
            stub_source.mkdir()                 
        temp_stubs_directory = stub_project_root.joinpath("stubs").absolute()
        if not temp_stubs_directory.exists():
            temp_stubs_directory.mkdir()

        # (b) Generating the stub files (*.pyi), by inclusing the main src folder of the package into the parser
        #    ├── temp_stub_project
        #       ├── src
        #       ├── stubs
        #           ├── pkg_name
        #               ├── __init__.pyi
        #               ├── calculate.pyi
        parser_options = [
            str(self.package_directory.absolute()), # main location of *.py files to create stubs
            "--include-docstrings",
            "-o",
            str(temp_stubs_directory), # where to put the created *.pyi files
        ]
        stub_options = stubgen.parse_options(parser_options)
        stubgen.generate_stubs(stub_options)

        # (c) Convert above file-directory to below
        #    ├── temp_stub_project
        #       ├── src
        #           ├── pkg_name-stubs
        #               ├── __init__.pyi
        #               ├── calculate.pyi          
      
        for package in self.package_names:
            temp_stub_package = temp_stubs_directory.absolute().joinpath(package)
            stub_package = stub_source.joinpath(f"{package}-stubs")
            if stub_package.exists(): # making sure the stube folder (*.pyi) is not there from previous build
                shutil.rmtree(stub_package)
            temp_stub_package.rename(stub_package)
        shutil.rmtree(temp_stubs_directory)

        # (d) Create the setup.py file to build the *.whl file for the stube
        #    ├── temp_stub_project
        #       ├── src
        #           ├── pkg_name-stubs
        #               ├── __init__.pyi
        #               ├── calculate.pyi          
        #       ├── setup.py        
        stub_packages = [f"{package}-stubs" for package in self.package_names] # pkg_name-stubs folder, in above folder directory
        setup_template = SetupTemplate.from_project_information(
            name=f"{self.project_name}-stubs",      # 'cookiecutter_v1-stubs'
            source_package_name=self.project_name,  # 'cookiecutter_v1
            version=self.version,
            packages=stub_packages,                 # pkg_name-stubs
            package_dir={"": "src"},
        )

        setup_script = stub_project_root.joinpath("setup.py") # create empty setup.py
        with open(setup_script, "w") as f: # writing into the setup.py file
            f.write(setup_template.auto_generate_setup_script())

        return stub_project_root

    @staticmethod
    def _build_package(project_root: Path) -> Path:
        """
        subprocess wrapper for 'python -m build' to build the stubs project

        Parameters
        ----------
        project_root : `Path`
            Path object representing the root of the project to build

        Returns
        -------
        `Path`
            Path object representing the built .whl file
        """
        args = [sys.executable, "-m", "build", str(project_root), "--wheel"]
        _ = subprocess.run(args, capture_output=True)
        whl = next(project_root.joinpath("dist").glob("*.whl"))
        return whl.absolute()

    def build_stubs_package(self) -> Path:
        """
        Builds a "-stubs" package mirroring the current project.

        Returns
        -------
        `Path`
            Path object representing the built .whl file
        """
        
        # (1) Fiest create all *.pyi files and then create a setup.py to build the stub wheel file
        stub_project_root = self._bootstrap_stubs_project()
        print(f"building {stub_project_root}")

        # (2) run the "python -m build . --wheel" command
        built_whl = self._build_package(project_root=stub_project_root)
        return built_whl


if __name__ == "__main__":
    c = StubProjectBuilder(
        project_name="pkg_name",
        version="0.0.0rc0",
        package_names=["pkg_name"],
        project_root=Path.cwd(),
        package_directory=Path.cwd().joinpath("src"),
    )
    whl = c.build_stubs_package()
    print(f"Look what I found {whl}")

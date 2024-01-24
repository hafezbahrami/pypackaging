# Build Sysytem Table
We will be using pyproject.toml to specify the build system in a table formatted in a *.toml file. The build-front-end (e.g. build or pip) tuses build-backend (such as setuptools, setuptools-scm, wheel, ...) to build the package.

![pipeline](https://google.com)
![coverage](https://google.com)




## Quick Start

### Installation
### Building A Model
### Converting A Model
### Deploying A Model

## Development Guide

### 1. Dependencies
### 2. Environment Setup
### 3. Testing and Validation

## Roadmap
- [ ] 

## Basics of building a package
Python job requiring a build should start with the absolute minimum requirements:
- pip
- wheel
- setuptools (build backend)
- build (build front end)
- invoke (tasks.py)

### 1 create setup.py, task.py, and pyproject.toml
All stuff that we used to put in the setup.py (through the setup() call), which required setup.cfg, now are dumped simply into
the pyproject.toml file. It is easier, cleaner, and less confusing.

Just a note, tht Pipfile format is also a *.toml format

### Create a Pipfile
- (I) Look at the Pipfile for 3 different section of it: Source, Packages, and Dev-Packages 
- (II) Creating the Pipfile.lock: The lock file tries to create a comprehensive list of packages that can be installed in a virtual environment. For instance, considering the list of 11 3rd part libraries listed in our pipfile, what version of each of them can be constsent with the rest to install. It is kind of created a dependency-graph. Thus, pipfile.lock is nothing but a list of "what package and what version of it to be installed in: (a) the *whl package itself, when deployed to the user, and (b) all packages to be installed in the developer virtual env for development. Obviously, (a) is a subset of (b)

![pipfile_lock_image](./pics/pipfile_lock.png)

### Create a local virtual env
- Now, we couuld create a local virtual env, and try to install all the packages in the "dev-packages" section of the pipfile.lock file
- ```pipenv shell``` will create a shell (virtual env), in "~/.local/share/virtualenvs/Name_of_Venv_XXXX". This will only have 3 native python packages (setuptools, wheel, pip), otherwise it is like an empty env.
- ```pipenv sync --dev```: this will synv and install all the packages we have in "dev-packages" section of a pipfile.lock.
- ```pipenv grapg > dep_graph.json```: This will look at the installedpackages inside our virtual env, and will create a graph that shows all the dependencies between all the packages noted in the pipfile (more importantly with the version # in the pipfile.lock).

There are a couple of points in the screen-shot below for what we got from ```pipenv graph > dep_graph.json```:
- (I) All the packages noted in the pipfile (and with the version # in pipfile.lock) can be found here.
- (II) Look at the numpy as the only "package" to be shipped to the user (requires user machine to install it). It is under the package_name whell-file name.
- (III) Dependencies, such as toml package, in this screen shot emphasizes the importance of dependency-conflict-resolution by the pipfile.lock file, on what version of each package is consostent with all other (if needed).
- (IV) Also, note that a lot more than what we specified in our Pipfile will be installed in our env, due to dependency packages.

![pipenv_lock](./pics/pipenvgraph.png)

## References
- pythons docs on pyproject.toml https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- setuptools: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
- and as an example here is blacks config docs https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-via-a-file
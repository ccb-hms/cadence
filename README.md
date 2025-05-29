[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![pytest](https://github.com/ccb-hms/cadence/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/ccb-hms/cadence/actions/workflows/pytest.yml)
[![docker](https://github.com/ccb-hms/cadence/actions/workflows/docker.yml/badge.svg)](https://github.com/ccb-hms/cadence/actions/workflows/docker.yml)


<p float="left">
    <img style="vertical-align: top" src="./images/cadence01.jpeg" width="25%" />
</p>

## CCB Meeting Scheduling Repository ##

This repository contains the `Meetings` class, which is based on the Python [timeboard](https://pypi.org/project/timeboard/) project. Its primary purpose is to help create the CCB weekly meetings schedule. Additionally, it serves as a template repository for Python projects that require a Docker container with a complete Python development environment and testing capabilities. The repository is also configured to run tests using GitHub Actions.

## Installation Locally with Docker ##

1. Install [Docker](https://docs.docker.com/) on your machine.

2. Clone the GitHub project repository to create a local copy:
   ```bash
   git clone git@github.com:ccb-hms/cadence.git
   ```

3. Navigate to the repository's directory and build the Docker image:
   ```bash
   cd cadence && docker-compose build
   ```
   This image will include all specifications from the Dockerfile based on the official [Python 3.12](https://hub.docker.com/layers/library/python/3.12.10/images/sha256-2749d801aca0c7d0b0b2106dabe3a8bca138c597b273d18c4e497f61e703603c) Docker image, along with all dependencies described in the project's `pyproject.toml` file. The image is built locally and stored in the Docker cache. To rebuild the image, run `docker-compose build` again. To remove the image, run `docker-compose down --rmi all`.

4. Run the Docker container:
   ```bash
   docker-compose up
   ```
   This command creates a container and starts a Jupyter server, which can be accessed through a web browser.

5. Access the Jupyter Lab server from your browser by visiting the link that begins with `localhost:8888`.

## Installation without Docker ##

For installation in a local programming environment, we use [uv](https://github.com/astral-sh/uv) to create a pure, repeatable application environment. Mac and Windows users should install uv as described in the [installation instructions](https://github.com/astral-sh/uv#installation). UV is a fast Python package installer and resolver, written in Rust. It serves as a drop-in replacement for pip and pip-tools, offering significant performance improvements and a more efficient workflow.

UV manages dependencies on a per-project basis. To install this package, change to your project directory and run:

```bash
# Install the package. This assumes that Python version 3.12 is set as the current global Python interpreter. 
uv venv --python=3.12.10

# Activate the environment
source .venv/bin/activate 
# On Windows use: .venv\Scripts\activate uv pip install -e .

# Next, install the dependencies
uv sync

# Lastly, run the Jupyter Lab server in the new environment
uv run jupyter lab
```

### Install with Other Python Versions ###

The package was tested with Python 3.12.10, as defined within the project's configuration. However, it comes with compatibility libraries to ensure that it can be used with lower Python versions. To install this package with a different version of Python, such as Python 3.10, first create a virtual environment with the desired version:

```bash
uv venv --python=3.10 
source .venv/bin/activate 
# On Windows use: .venv\Scripts\activate uv pip install -e .
```

It is also possible to install the package using a local Python interpreter that is installed in a specific directory, for example, within a virtual environment created with [Miniconda](https://docs.anaconda.com/miniconda/):

```bash
uv venv --python=/home/.../miniconda3/envs/uv-test/bin/python
source .venv/bin/activate 
# On Windows use: .venv\Scripts\activate uv pip install -e .
```
Here, `uv-test` is the directory that contains the executable Python interpreter created by Miniconda.

## Create a Meeting Schedule ##

For a detailed example, refer to the [scheduling_example](notebooks/scheduling_example.ipynb) notebook. This example demonstrates how easy it is to create a meeting schedule with just a list of names:

```python
from cadence.mscheduler import Meetings

# Let's start with a list of some names
name_list = ['Andreas', 'Eva', 'Matthias', 'Manuela']

# Define the start and end dates for the meeting schedule
start_date = '2024-11-13'
end_date = '2025-01-30'

# Specify that the group will meet once per week on Wednesdays
meeting_day = 2

# Now we create the meeting schedule
meeting = Meetings(name_list=name_list)
schedule = meeting.create_timeboard(start_date=start_date, end_date=end_date, meeting_day=meeting_day)
```

The output of the `create_timeboard` method is a DataFrame that can be saved and imported into other applications, such as calendars.

<p float="left">
    <img style="vertical-align: top" src="./images/example_schedule.png" width="50%" />
</p>

## Run Tests ##

[Pytest](https://docs.pytest.org/en/stable/) is a popular testing framework that makes it easy to write small, readable tests. 

The pytest framework scales to support complex functional testing for applications and libraries. Pytest will automatically discover and run all the test files in the `./tests` directory that follow the naming conventions (i.e., files starting with test_ or ending with _test.py). You can also specify the test directory explicitly by running `pytest tests/` if your test directory is named tests. Pytest will execute all the discovered test cases and provide a detailed report.


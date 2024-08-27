<p float="left">
    <img style="vertical-align: top" src="./images/cadence01.jpeg" width="25%" />
</p>

## The CCB Meeting Scheduling Repository ##
This repository contains the `Meetings` class based 
on the python [timeboard](https://pypi.org/project/timeboard/) project to 
create the CCB weekly meetings schedule. 
It also serves as a template repository for python projects that need 
a docker container complete with a python development environment and tests.
This repository is also set up to run tests via GitHub actions.
## Install locally with docker ##
1. Install [Docker](https://docs.docker.com/) on your machine.
2. Clone the GitHub project repository to create a local copy of the repository:
```bash
git clone git@github.com:ccb-hms/cadence.git
```
3. Navigate to the repository's directory and build the docker image:
```bash
cd cadence && docker compose build
````
This image will include all the specifications from the Dockerfile based on 
the official [python 3.11](https://hub.docker.com/_/python/tags) docker image and all 
dependencies described in the project's `Pipfile`.
4. Run the docker container:
```bash
docker compose up
``` 
This creates a container and starts a jupyter server which can be accessed through a web browser.
5. Access Jupyter Lab: Click on the link that starts with `localhost:8888` provided by the 
output of the last command.

## Create a meeting schedule ##



## Run tests ##
[Pytest](https://docs.pytest.org/en/stable/) is a popular testing framework that makes it easy to write small, 
readable tests. It can scale to support complex functional testing for applications and libraries. Pytest will 
automatically discover and run all the test files in the `./tests` directory that follow the naming conventions 
(i.e., files starting with test_ or ending with _test.py). You can also specify the test directory 
explicitly by running pytest tests/ if your test directory is named tests. 
Pytest will execute all the discovered test cases and provide a detailed summary of passing and failing tests.
To run the tests for this project, simply run pytest inside the docker container:
```bash
docker compose run app python -m pytest
```


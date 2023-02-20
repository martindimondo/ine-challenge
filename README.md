# Challenge INE

## Installation

In order to install, previously you need to install Docker.
After you can run on the project root folder

```
$ docker-compose build
$ docker-compose up
```

## Authentication

This project uses OAuth, after installation you need to create the app
on django admin. 

To support backend-to-backend, you need to create an app for client credential grant type,
To support frontend-to-backend, I recommend to create an app for auth code grant type.

## LINT

To run pylint

```
$ poetry run pylint **/*.py
```

## Runing test

The project uses Pytest, to run

```
$ poetry run pytest .
```

## Code coverage

To view the coverage
```
$ poetry run coverage run -m --source=users pytest .
$ poetry run coverage report
```

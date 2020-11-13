ml-hub-demo
===========

Example Python SDK for interacting with Radiant Earth's [ML Hub API](http://docs.mlhub.earth/#radiant-mlhub-api).

## Installation

This project uses [`poetry`](https://python-poetry.org/) for managing virtual environments and packaging.

1. Clone the repo:
   ```console
   $ git clone git@github.com:duckontheweb/ml-hub-demo.git
   $ cd ml-hub-demo
   ```
2. Install using [`poetry`](https://python-poetry.org/):
   ```console
   $ poetry install
   ```

## Documentation

You can find the documentation on GitHub Pages [here](https://duckontheweb.github.io/ml-hub-demo).

## Tests

Run unit tests:

```console
$ poetry run pytest
```

Run against all supported Python versions (>=3.6,<3.9):

```console
$ poetry run tox -p
```

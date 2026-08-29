<div align="center">
<a href="https://github.com/gerlero/multicollections"><img src="https://github.com/gerlero/multicollections/raw/main/logo.png" height="200"></a>

A fully generic `MultiDict` implementation for Python

---

[![Documentation](https://img.shields.io/readthedocs/multicollections)](https://multicollections.readthedocs.io/)
[![CI](https://github.com/gerlero/multicollections/actions/workflows/ci.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/gerlero/multicollections/branch/main/graph/badge.svg)](https://codecov.io/gh/gerlero/multicollections)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Publish](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml)
[![PyPI](https://img.shields.io/pypi/v/multicollections)](https://pypi.org/project/multicollections/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/multicollections)](https://pypi.org/project/multicollections/)

---

</div>

[`multicollections.MultiDict`]((https://multicollections.readthedocs.io/en/stable/api/multicollections/) ) stores multiple values for the same key while preserving insertion order. Its API follows [`multidict`](https://github.com/aio-libs/multidict), but keys can be of arbitrary [hashable](https://docs.python.org/3/glossary.html#term-hashable) types.



## Installation

With pip:

```bash
pip install multicollections
```

or conda:

```bash
conda install -c conda-forge multicollections
```

## Usage

```python
from multicollections import MultiDict

d = MultiDict([("a", 1), ("b", 2), ("a", 3)])

d["a"]
# 1

d.getall("a")
# [1, 3]

list(d.items())
# [("a", 1), ("b", 2), ("a", 3)]

d.add("a", 4)
```

The [`multicollections.abc`](https://multicollections.readthedocs.io/en/stable/api/abc/) module provides abstract base classes for implementing other multi-value collections.

See the [documentation](https://multicollections.readthedocs.io/) for the full API.

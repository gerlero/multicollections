# multicollections

A fully generic `MultiDict` class that allows multiple values for the same key while preserving insertion order.

[![Documentation](https://img.shields.io/readthedocs/multicollections)](https://multicollections.readthedocs.io/)
[![CI](https://github.com/gerlero/multicollections/actions/workflows/ci.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/gerlero/multicollections/branch/main/graph/badge.svg)](https://codecov.io/gh/gerlero/multicollections)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Publish](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml)
[![PyPI](https://img.shields.io/pypi/v/multicollections)](https://pypi.org/project/multicollections/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/multicollections)](https://pypi.org/project/multicollections/)

## ✨ Features

- **🔑 Multiple values per key**: Store multiple values for the same key, perfect for handling data like HTTP headers, form data, or configuration files
- **📝 Insertion order preserved**: Maintains the order in which items were added
- **🔄 Full compatibility**: Implements the `MutableMultiMapping` abstract base class with rich multi-value support
- **⚡ Type-safe**: Fully typed with generics for excellent IDE support
- **🪶 Lightweight**: Zero dependencies, pure Python implementation
- **🎯 Rich API**: Includes `getall()`, `popall()`, `popone()`, `add()`, and more specialized methods

## 📦 Installation

### pip

```bash
pip install multicollections
```

### conda

```bash
# Install from PyPI using conda's pip
conda install pip
pip install multicollections
```

> **Note**: This package is not yet available on conda-forge. The above method installs from PyPI using conda's pip.

## 🚀 Quick Start

```python
from multicollections import MultiDict

# Create a MultiDict with duplicate keys
headers = MultiDict([
    ('Accept', 'text/html'),
    ('Accept-Encoding', 'gzip'),
    ('Accept', 'application/json'),  # Same key, different value
    ('User-Agent', 'MyApp/1.0')
])

# Access the first value for a key
print(headers['Accept'])  # 'text/html'

# Get ALL values for a key
print(headers.getall('Accept'))  # ['text/html', 'application/json']

# See all key-value pairs (duplicates preserved)
print(list(headers.items()))
# [('Accept', 'text/html'), ('Accept-Encoding', 'gzip'), 
#  ('Accept', 'application/json'), ('User-Agent', 'MyApp/1.0')]

# Add more values for existing keys
headers.add('Accept', 'text/xml')
print(headers.getall('Accept'))  # ['text/html', 'application/json', 'text/xml']
print(len(headers))  # 5 items total

# Remove and return the first value
first_accept = headers.popone('Accept')
print(first_accept)  # 'text/html'
print(headers.getall('Accept'))  # ['application/json', 'text/xml']

# Remove and return all values for a key
all_accepts = headers.popall('Accept')
print(all_accepts)  # ['application/json', 'text/xml']
print('Accept' in headers)  # False

# Create from keyword arguments
config = MultiDict(host='localhost', port=8080, debug=True)

# Mix iterable and keyword arguments
mixed = MultiDict([('a', 1), ('b', 2)], c=3, d=4)
```

## ⚡ Advanced Features

`MultiDict` implements the `MutableMultiMapping` abstract base class, providing powerful methods for handling multiple values:

```python
from multicollections import MultiDict

data = MultiDict([('tags', 'python'), ('tags', 'web'), ('category', 'tutorial')])

# Get all values for a key
all_tags = data.getall('tags')
print(all_tags)  # ['python', 'web']

# Safe get with default for missing keys
missing_tags = data.getall('missing', default=[])
print(missing_tags)  # []

# Get one value with default
lang = data.getone('language', default='unknown')
print(lang)  # 'unknown'

# Remove and return one value
first_tag = data.popone('tags')
print(first_tag)  # 'python'
print(data.getall('tags'))  # ['web']

# Remove and return all values
remaining_tags = data.popall('tags')
print(remaining_tags)  # ['web']

# Extend with multiple items
data.extend([('tags', 'api'), ('tags', 'flask')])
print(data.getall('tags'))  # ['api', 'flask']

# Update vs extend: update replaces, extend adds
data.update([('category', 'advanced')])  # Replaces 'tutorial'
data.extend([('category', 'guide')])     # Adds alongside 'advanced'
print(data.getall('category'))  # ['advanced', 'guide']
```

## 📖 Why MultiDict?

Standard Python dictionaries can only hold one value per key. When you need to handle data formats that naturally allow multiple values for the same key, `MultiDict` is the perfect solution:

- **HTTP headers**: Multiple `Accept` or `Set-Cookie` headers
- **URL query parameters**: `?tag=python&tag=web&tag=api`
- **Form data**: Multiple form fields with the same name
- **Configuration files**: Multiple values for the same configuration key

## 🔗 Documentation

For detailed documentation, examples, and API reference, visit: https://multicollections.readthedocs.io/

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

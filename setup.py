"""Setup script for building C extensions."""

from setuptools import Extension, setup

# Define the C extension
c_ext = Extension(
    "multicollections._cmultidict",
    sources=["src/multicollections/_cmultidict.c"],
    optional=True,  # Make it optional so installation doesn't fail if compilation fails
)

setup(
    ext_modules=[c_ext],
)

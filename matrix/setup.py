from distutils.core import setup, Extension

setup(
    name='matrix',
    version='0.1',
    ext_modules=[
        Extension('matrix', ['matrix.c'])
    ]
)

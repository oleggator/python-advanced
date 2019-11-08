# C extension matrix implementation

[Usage example](main.py)

## Supported operations
- sum of matrices
- multiplication by matrix, by integer
- division by integer
- transpose
- `in` operator

## Installation
Create venv and install module
```bash
python3 -m venv venv
source venv/bin/activate
pip install .
```

## Speed comparison
C:
```bash
python3 -m timeit 'from matrix import Matrix as CMatrix' 'from main import test' 'test(CMatrix, 3, 2)'
100000 loops, best of 5: 3.06 usec per loop
```
```bash
python3 -m timeit 'from matrix import Matrix as CMatrix' 'from main import test' 'test(CMatrix, 30, 20)'
5000 loops, best of 5: 74.3 usec per loop
```
```bash
python3 -m timeit 'from matrix import Matrix as CMatrix' 'from main import test' 'test(CMatrix, 300, 200)'
10 loops, best of 5: 31.5 msec per loop
```

Python:
```bash
python3 -m timeit 'from py_matrix import PyMatrix' 'from main import test' 'test(PyMatrix, 3, 2)'
10000 loops, best of 5: 36.6 usec per loop
```
```bash
python3 -m timeit 'from py_matrix import PyMatrix' 'from main import test' 'test(PyMatrix, 30, 20)'
20 loops, best of 5: 13.2 msec per loop
```
```bash
python3 -m timeit 'from py_matrix import PyMatrix' 'from main import test' 'test(PyMatrix, 300, 200)'
1 loop, best of 5: 13 sec per loop
```

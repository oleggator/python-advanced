## Speed comparison
C:
```
python3 -m timeit 'from matrix import Matrix as CMatrix' 'from main import test' 'test(CMatrix)'
100000 loops, best of 5: 3.06 usec per loop
```

Python:
```
python3 -m timeit 'from py_matrix import PyMatrix' 'from main import test' 'test(PyMatrix)'
10000 loops, best of 5: 36.6 usec per loop
```

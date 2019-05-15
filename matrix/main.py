from matrix import Matrix as CMatrix
from py_matrix import PyMatrix

def test(matrix_class):
    m = matrix_class([
        [1, 2],
        [3, 4],
        [5, 6],
    ])

    n = 2 * m # multiply matrix by integer
    o = m + m # sum matrices
    p = m.transpose() # transpose
    q = m @ p # multiply matrices
    r = 2 in m

def main():
    test(CMatrix)
    test(PyMatrix)

if __name__ == '__main__':
    main()

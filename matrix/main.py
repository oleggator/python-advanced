from matrix import Matrix as CMatrix
from py_matrix import PyMatrix

def test(matrix_class, rows=3, columns=2):
    m = matrix_class([
        [column for column in range(row * columns, row * columns + columns)]
        for row in range(rows)
    ])

    # # or
    # m = matrix_class([
    #     [1, 2],
    #     [3, 4],
    #     [5, 6],
    # ])

    n = 2 * m # multiply matrix by integer
    n = n / 2 # divide matrix by integer
    o = m + m # sum matrices
    p = m.transpose() # transpose
    q = m @ p # multiply matrices
    r = 2 in m

def main():
    test(CMatrix)
    test(PyMatrix)

if __name__ == '__main__':
    main()

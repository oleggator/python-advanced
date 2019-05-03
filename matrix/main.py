from matrix import Matrix


def main():
    print(Matrix)
    m = Matrix([
        [0, 0],
        [0, 0],
    ])

    for i in range(2):
        for j in range(2):
            m[(i,j)] = i * 2 + j

    n = 2 * m
    for i in range(2):
        for j in range(2):
            print(n[(i,j)])

    o = n + m
    for i in range(2):
        for j in range(2):
            print(o[(i,j)])

    p = m @ n
    for i in range(2):
        for j in range(2):
            print(p[(i,j)])

    print(p)

if __name__ == '__main__':
    main()

import copy

class PyMatrix:
    def __init__(self, init_matrix):
        self._matrix = [item for row in init_matrix for item in row]
        self._rows = len(init_matrix)
        self._columns = len(init_matrix[0])

    def __matmul__(self, other):
        new_matrix = [None] * self._rows
        for i in range(self._rows):
            new_matrix[i] = [0] * other._columns

        for i in range(self._rows):
            for j in range(other._columns):
                for k in range(self._columns):
                    new_matrix[i][j] += self[(i, k)] * other[(k, j)]

        return self.__class__(new_matrix)

    def __add__(self, other):
        new_matrix = copy.copy(self)
        for i in range(self._rows * self._columns):
            new_matrix._matrix[i] += other._matrix[i]

        return new_matrix

    def __rmul__(self, other):
        new_matrix = copy.copy(self)
        for i in range(self._rows * self._columns):
            new_matrix._matrix[i] *= other

        return new_matrix

    def __contains__(self, other):
        for item in self._matrix:
            if item == other:
                return True

        return False

    def transpose(self):
        new_matrix = [None] * self._columns
        for i in range(self._columns):
            new_matrix[i] = [None] * self._rows
            for j in range(self._rows):
                new_matrix[i][j] = self[(j, i)]

        return self.__class__(new_matrix)

    def __getitem__(self, key: tuple):
        i, j = key
        return self._matrix[i * self._columns + j]

    def __str__(self):
        return str(self._matrix)

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyTypeObject matrix_Type;

typedef struct {
    PyObject_HEAD
    long int *matrix;
    Py_ssize_t rows, columns;
} matrix_t;

static void matrix_dealloc(matrix_t *o) {
    free(o->matrix);
    Py_TYPE(o)->tp_free((PyObject *)o);
}

static PyObject *matrix_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    matrix_t *self = (matrix_t *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return PyErr_NoMemory();
    }

    PyObject *list = NULL;
    if (!PyArg_ParseTuple(args, "O", &list)) {
        return NULL;
    }

    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "object must be tuple");
        return NULL;
    }

    self->rows = PyList_Size(list);
    if (self->rows == 0) {
        PyErr_SetString(PyExc_TypeError, "list is empty");
        return NULL;
    }
    self->columns = PyList_Size(PyList_GetItem(list, 0));
    self->matrix = calloc(self->rows * self->columns, sizeof(long int));

    for (Py_ssize_t i = 0; i < self->rows; ++i) {
        PyObject *row = PyList_GetItem(list, i);
        Py_INCREF(row);
        if (!PyList_Check(row)) {
            PyErr_SetString(PyExc_TypeError, "object must be tuple");
            return NULL;
        }

        if (PyList_Size(row) != self->columns) {
            PyErr_SetString(PyExc_ValueError, "wrong row columns count");
            return NULL;
        }

        for (Py_ssize_t j = 0; j < self->columns; ++j) {
            PyObject *num_obj = PyList_GetItem(row, j);
            Py_INCREF(num_obj);
            if (!PyLong_Check(num_obj)) {
                PyErr_SetString(PyExc_TypeError, "object must be number");
                return NULL;
            }

            self->matrix[i * self->columns + j] = PyLong_AsLong(num_obj);
            Py_DECREF(num_obj);
        }
        Py_DECREF(row);
    }

    return (PyObject *)self;
}

static int matrix_init(matrix_t *self, PyObject *args, PyObject *kwds) {
    return 0;
}

static Py_ssize_t matrix_length(matrix_t *self) {
    return (Py_ssize_t)(self->rows * self->columns);
}

static PyObject *matrix_get(matrix_t *self, PyObject *key) {
    if (!PyTuple_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "object must be tuple");
        return NULL;
    }

    PyObject *i_obj = PyTuple_GetItem(key, 0);
    Py_INCREF(i_obj);
    if (!PyLong_Check(i_obj)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return NULL;
    }
    Py_ssize_t i = PyLong_AsLong(i_obj);
    Py_DECREF(i_obj);

    PyObject *j_obj = PyTuple_GetItem(key, 1);
    Py_INCREF(j_obj);
    if (!PyLong_Check(j_obj)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return NULL;
    }    
    Py_ssize_t j = PyLong_AsLong(j_obj);
    Py_DECREF(j_obj);

    if (i * self->columns + j < 0 || i * self->columns + j > self->rows * self->columns) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return NULL;
    }

    return PyLong_FromLong(self->matrix[i * self->columns + j]);
}

static int matrix_set(matrix_t *self, PyObject *key, PyObject *item) {
    if (!PyTuple_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "object must be tuple");
        return -1;
    }
    PyObject *i_obj = PyTuple_GetItem(key, 0);
    Py_INCREF(i_obj);
    if (!PyLong_Check(i_obj)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return -1;
    }
    Py_ssize_t i = PyLong_AsLong(i_obj);
    Py_DECREF(i_obj);

    PyObject *j_obj = PyTuple_GetItem(key, 1);
    Py_INCREF(j_obj);
    if (!PyLong_Check(j_obj)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return -1;
    }
    Py_ssize_t j = PyLong_AsLong(j_obj);
    Py_DECREF(j_obj);

    if (i * self->columns + j < 0 || i * self->columns + j > self->rows * self->columns) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return -1;
    }

    if (!PyLong_Check(item)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return -1;
    }

    self->matrix[i * self->columns + j] = PyLong_AsLong(item);

    return 0;
}

static int matrix_contains(matrix_t *self, PyObject *arg) {
    if (!PyLong_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "object must be number");
        return -1;
    }

    long int item = PyLong_AsLong(arg);
    for (Py_ssize_t i = 0; i < self->rows * self->columns; ++i) {
        if (self->matrix[i] == item) {
            return 1;
        }
    }

    return 0;
}

PyObject* matrix_repeat(matrix_t *self, Py_ssize_t n) {
    matrix_t *new_matrix = PyObject_New(matrix_t, &matrix_Type);

    new_matrix->rows = self->rows;
    new_matrix->columns = self->columns;
    new_matrix->matrix = malloc(sizeof(long int) * self->rows * self->columns);

    for (Py_ssize_t i = 0; i < self->rows * self->columns; ++i) {
        new_matrix->matrix[i] = n * self->matrix[i];
    }

    return (PyObject *)new_matrix;
}

PyObject* matrix_concat(matrix_t *matrix1, matrix_t *matrix2) {
    if (matrix1->rows != matrix2->rows|| matrix1->columns != matrix2->columns) {
        PyErr_SetString(PyExc_TypeError, "matrix must be the same size");
        return NULL;
    }

    matrix_t *new_matrix = PyObject_New(matrix_t, &matrix_Type);

    new_matrix->rows = matrix1->rows;
    new_matrix->columns = matrix1->columns;
    new_matrix->matrix = malloc(sizeof(long int) * matrix1->rows * matrix1->columns);

    for (Py_ssize_t i = 0; i < matrix1->rows * matrix1->columns; ++i) {
        new_matrix->matrix[i] = matrix1->matrix[i] + matrix2->matrix[i];
    }

    return (PyObject *)new_matrix;
}

PyObject* matrix_multiply(matrix_t *matrix1, matrix_t *matrix2) {
    if (matrix1->columns != matrix2->rows) {
        PyErr_SetString(PyExc_TypeError, "matrix must be the same size");
        return NULL;
    }

    matrix_t *new_matrix = PyObject_New(matrix_t, &matrix_Type);
    new_matrix->rows = matrix1->rows;
    new_matrix->columns = matrix2->columns;
    new_matrix->matrix = calloc(new_matrix->rows * new_matrix->columns, sizeof(long int));

    for (Py_ssize_t i = 0; i < matrix1->rows; ++i) {
        for (Py_ssize_t j = 0; j < matrix2->columns; ++j) {
            for (Py_ssize_t k = 0; k < matrix1->columns; ++k) {
                new_matrix->matrix[i * new_matrix->columns + j]
                    += matrix1->matrix[i * matrix1->columns + k]
                    * matrix2->matrix[k * matrix2->columns + j];
            }
        }
    }

    return (PyObject *)new_matrix;
}

PyObject* matrix_transpose(matrix_t *self) {
    matrix_t *new_matrix = PyObject_New(matrix_t, &matrix_Type);

    new_matrix->rows = self->columns;
    new_matrix->columns = self->rows;
    new_matrix->matrix = malloc(sizeof(long int) * self->rows * self->columns);

    for (Py_ssize_t i = 0; i < new_matrix->rows; ++i) {
        for (Py_ssize_t j = 0; j < new_matrix->columns; ++j) {
            new_matrix->matrix[i * new_matrix->columns + j]
                = self->matrix[j * self->columns + i];
        }
    }

    return (PyObject *)new_matrix;
}

static PyObject *matrix_repr(matrix_t *self) {    
    if (!self->rows || !self->columns) {
        return PyUnicode_FromString("<Matrix {}>");
    }

    _PyUnicodeWriter writer;
    _PyUnicodeWriter_Init(&writer);
    writer.overallocate = 1;
    writer.min_length = 10;
    PyObject *el_str = NULL;

    if (_PyUnicodeWriter_WriteASCIIString(&writer, "<Matrix {\n", 10) < 0) {
        goto error;
    }

    for (Py_ssize_t i = 0; i < self->rows * self->columns; ++i) {
        el_str = PyUnicode_FromFormat((i + 1) % self->columns ? "%d " : "%d\n",
            self->matrix[i]);

        if (_PyUnicodeWriter_WriteStr(&writer, el_str)) {
            Py_DECREF(el_str);
            goto error;
        }

        Py_DECREF(el_str);
    }

    writer.overallocate = 0;
    if (_PyUnicodeWriter_WriteASCIIString(&writer, "}>", 2) < 0) {
        goto error;
    }

    return _PyUnicodeWriter_Finish(&writer);

error:
    Py_XDECREF(el_str);
    _PyUnicodeWriter_Dealloc(&writer);
    return NULL;
}

static PyObject *matrix_str(matrix_t *self) {
    return matrix_repr(self);
}

static PySequenceMethods matrix_as_sequence = {
    .sq_length      = (lenfunc)matrix_length,
    .sq_concat      = (binaryfunc)matrix_concat,
    .sq_repeat      = (ssizeargfunc)matrix_repeat,
    .sq_contains    = (objobjproc)matrix_contains,
};

static PyMethodDef matrix_methods[] = {
    {"transpose", (PyCFunction)matrix_transpose, METH_NOARGS},
    { NULL, NULL, 0, NULL }
};

static PyNumberMethods matris_as_number = {
    .nb_add             = (binaryfunc)matrix_concat,
    .nb_matrix_multiply = (binaryfunc)matrix_multiply,
};

static PyMappingMethods matrix_as_mapping = {
    .mp_subscript       = (binaryfunc)matrix_get,
    .mp_ass_subscript   = (objobjargproc)matrix_set,
};

PyTypeObject matrix_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "matrix.Matrix",                                 /* tp_name */
    sizeof(matrix_t),                                /* tp_basic_size */
    0,                                               /* tp_itemsize */
    (destructor)matrix_dealloc,                      /* tp_dealloc */
    0,                                               /* tp_print */
    0,                                               /* tp_getattr */
    0,                                               /* tp_setattr */
    0,                                               /* tp_reserved */
    (reprfunc)matrix_repr,                           /* tp_repr */
    &matris_as_number,                               /* tp_as_number */
    &matrix_as_sequence,                             /* tp_as_sequence */
    &matrix_as_mapping,                              /* tp_as_mapping */
    0,                                               /* tp_hash */
    0,                                               /* tp_call */
    (reprfunc)matrix_str,                            /* tp_str */
    0,                                               /* tp_getattro */
    0,                                               /* tp_setattro */
    0,                                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /* tp_flags */
    0,                                               /* tp_doc */
    0,                                               /* tp_traverse */
    0,                                               /* tp_clear */
    0,                                               /* tp_richcompare */
    0,                                               /* tp_weaklistoffset */
    0,                                               /* tp_iter */
    0,                                               /* tp_iternext */
    matrix_methods,                                  /* tp_methods */
    0,                                               /* tp_members */
    0,                                               /* tp_getset */
    0,                                               /* tp_base */
    0,                                               /* tp_dict */
    0,                                               /* tp_descr_get */
    0,                                               /* tp_descr_set */
    0,                                               /* tp_dictoffset */
    (initproc)matrix_init,                           /* tp_init */
    0,                                               /* tp_alloc */
    matrix_new,                                      /* tp_new */
    0,                                               /* tp_free */
};

static struct PyModuleDef matrix_module = {
    PyModuleDef_HEAD_INIT,
    "matrix",   /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
};


PyMODINIT_FUNC PyInit_matrix(void) {
    if (PyType_Ready(&matrix_Type) < 0) {
        return NULL;
    }

    PyObject *module = PyModule_Create(&matrix_module);
    if (module == NULL) {
        return NULL;
    }

    Py_INCREF(&matrix_Type);
    PyModule_AddObject(module, "Matrix", (PyObject *)&matrix_Type);
    return module;
}

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* C extension module providing optimized helper functions for MultiDict */

/* 
 * rebuild_indices_c(items_list) -> dict
 * 
 * Fast C implementation of index rebuilding for MultiDict.
 * Takes a list of (key, value) tuples and returns a dict mapping
 * key -> list of indices where that key appears in items_list.
 */
static PyObject *
rebuild_indices_c(PyObject *self, PyObject *args)
{
    PyObject *items_list;
    
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &items_list)) {
        return NULL;
    }

    PyObject *indices_dict = PyDict_New();
    if (indices_dict == NULL) {
        return NULL;
    }

    Py_ssize_t len = PyList_GET_SIZE(items_list);
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PyList_GET_ITEM(items_list, i);  /* Borrowed ref */
        
        if (!PyTuple_Check(item) || PyTuple_GET_SIZE(item) != 2) {
            Py_DECREF(indices_dict);
            PyErr_SetString(PyExc_ValueError, "Expected list of 2-tuples");
            return NULL;
        }

        PyObject *key = PyTuple_GET_ITEM(item, 0);  /* Borrowed ref */
        
        /* Get or create the indices list for this key */
        PyObject *indices_list = PyDict_GetItem(indices_dict, key);  /* Borrowed ref */
        if (indices_list == NULL) {
            indices_list = PyList_New(0);
            if (indices_list == NULL) {
                Py_DECREF(indices_dict);
                return NULL;
            }
            if (PyDict_SetItem(indices_dict, key, indices_list) < 0) {
                Py_DECREF(indices_list);
                Py_DECREF(indices_dict);
                return NULL;
            }
            Py_DECREF(indices_list);
            indices_list = PyDict_GetItem(indices_dict, key);  /* Get borrowed ref */
        }

        PyObject *index_obj = PyLong_FromSsize_t(i);
        if (index_obj == NULL) {
            Py_DECREF(indices_dict);
            return NULL;
        }
        
        if (PyList_Append(indices_list, index_obj) < 0) {
            Py_DECREF(index_obj);
            Py_DECREF(indices_dict);
            return NULL;
        }
        Py_DECREF(index_obj);
    }

    return indices_dict;
}

/* Module method definitions */
static PyMethodDef module_methods[] = {
    {"rebuild_indices", rebuild_indices_c, METH_VARARGS,
     "Rebuild key indices from items list (optimized C implementation)"},
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static PyModuleDef cmultidict_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_cmultidict",
    .m_doc = "C extension module for optimized MultiDict operations",
    .m_size = -1,
    .m_methods = module_methods,
};

/* Module initialization function */
PyMODINIT_FUNC
PyInit__cmultidict(void)
{
    return PyModule_Create(&cmultidict_module);
}

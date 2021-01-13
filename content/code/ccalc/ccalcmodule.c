#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef enum {
    AST_LITERAL,
    AST_PLUS,
    AST_MULTIPLY,
} AstNodeType;

typedef struct _ast {
    /* The type of node this represents e.g.
       a literal, an operator etc. */
    AstNodeType type;

    /* In the case of a literal value, this field
       holds the actual value */
    double value;

    /* In the case of an operator, this pointer
       refers to the left child node */
    struct _ast *left;

    /* In the case of an operator, this pointer
       refers to the right child node */
    struct _ast *right;
} AstNode;

void
ast_print(AstNode *ast, int level)
{
    for (int i = 0; i < level; i++) {
        printf("  ");
    }

    switch(ast->type) {
    case AST_LITERAL:
        printf("%.2f\n", ast->value);
        break;

    case AST_PLUS:
        printf("+\n");
        ast_print(ast->left, level + 1);
        ast_print(ast->right, level + 1);
        break;

    case AST_MULTIPLY:
        printf("*\n");
        ast_print(ast->left, level + 1);
        ast_print(ast->right, level + 1);
        break;
    }
}

double
ast_evaluate(AstNode *ast)
{
    switch(ast->type) {
    case AST_LITERAL:
        return ast->value;

    case AST_PLUS: {
        double a = ast_evaluate(ast->left);
        double b = ast_evaluate(ast->right);

        return a + b;
    }

    case AST_MULTIPLY: {
        double a = ast_evaluate(ast->left);
        double b = ast_evaluate(ast->right);

        return a * b;
    }
    default:
        assert(0); // Unknown node type!
        return -1;
    }
}

static int
AstNode_FromPyObject(PyObject* obj, AstNode *ast, Py_ssize_t *index)
{
    PyObject* type = PyObject_GetAttrString(obj, "type");
    if (type == NULL) {
        return 0;
    }

    long node_type = PyLong_AsLong(type);
    Py_DECREF(type);

    // Get a pointer to the current node.
    AstNode *node = &ast[*index];

    switch(node_type) {
    case AST_LITERAL: {

        PyObject* value = PyObject_GetAttrString(obj, "value");
        if (value == NULL) {
            return 0;
        }

        double v = PyFloat_AsDouble(value);
        Py_DECREF(value);

        node->type = AST_LITERAL;
        node->value = v;
        node->left = NULL;
        node->right = NULL;

        // No need to recurse so return early.
        return 1;
    }
    case AST_PLUS: {
        node->type = AST_PLUS;
        break;
    }

    case AST_MULTIPLY: {
        node->type = AST_MULTIPLY;
        break;
    }

    default:
        // TODO: Raise exception
        printf("Error! Field 'type' was not a valid node type.\n");
        return 0;
    }


    PyObject *left = PyObject_GetAttrString(obj, "left");
    if (left == NULL) {
        return 0;
    }

    PyObject *right = PyObject_GetAttrString(obj, "right");
    if (right == NULL) {
        return 0;
    }

    // Increment the index to get pointers to the next array cells.
    (*index)++;
    node->left = &ast[*index];

    if (!AstNode_FromPyObject(left, ast, index)) {
        return 0;
    }

    (*index)++;
    node->right = &ast[*index];

    if (!AstNode_FromPyObject(right, ast, index)) {
        return 0;
    }

    return 1;
}

static AstNode*
AstTree_FromPyObject(PyObject* obj)
{
    // Allocate enough memory to store the resulting AST.
    Py_ssize_t num_nodes = PyObject_Length(obj);
    if (num_nodes == -1) {
        return NULL;
    }

    AstNode *ast = malloc(num_nodes * sizeof(AstNode));
    if (ast == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for the AST.") ;
        return NULL;
    }

    Py_ssize_t index = 0;
    if (!AstNode_FromPyObject(obj, ast, &index)) {
        free(ast);
        return NULL;
    }

    return ast;
}

static PyObject*
method_eval_ast(PyObject *self, PyObject *args)
{
    PyObject *obj = NULL;

    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    AstNode *ast = AstTree_FromPyObject(obj);
    if (ast == NULL) {
        return NULL;
    };

    double result = ast_evaluate(ast);
    free(ast);
    return PyFloat_FromDouble(result);
}

static PyObject*
method_hello_world(PyObject *self, PyObject *args)
{
    printf("Hello, World!\n");
    Py_RETURN_NONE;
}

static PyMethodDef ccalc_methods[] = {
    {"hello_world", method_hello_world, METH_VARARGS, "Print 'Hello, World!'."},
    {"eval_ast", method_eval_ast, METH_VARARGS, "Evaluate the given ast."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ccalcmodule = {
    PyModuleDef_HEAD_INIT,
    "_ccalc",
    "Simple calculator implemented in C",
    -1,
    ccalc_methods
};

PyMODINIT_FUNC
PyInit__ccalc()
{
    return PyModule_Create(&ccalcmodule);
}

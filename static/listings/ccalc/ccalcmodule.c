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
    float value;

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

float
ast_evaluate(AstNode *ast)
{
    switch(ast->type) {
    case AST_LITERAL:
        return ast->value;

    case AST_PLUS: {
        float a = ast_evaluate(ast->left);
        float b = ast_evaluate(ast->right);

        return a + b;
    }

    case AST_MULTIPLY: {
        float a = ast_evaluate(ast->left);
        float b = ast_evaluate(ast->right);

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
        // TODO: Raise Exception?
        printf("Unable to get field 'type'\n");
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
            // TODO: Raise Exception?
            printf("Unable to get field 'value'\n");
            return 0;
        }

        double v = PyFloat_AsDouble(value);
        Py_DECREF(value);

        node->type = AST_LITERAL;
        node->value = (float)v;
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
        // TODO: Raise Exception
        printf("Unable to get field 'left'\n");
        return 0;
    }

    PyObject *right = PyObject_GetAttrString(obj, "right");
    if (right == NULL) {
        // TODO: Raise Exception
        printf("Unable to get field 'right'\n");
        return 0;
    }

    // Increment the index to get pointers to the next array cells.
    (*index)++;
    node->left = &ast[*index];

    if (!AstNode_FromPyObject(left, ast, index)) {
        // TODO: Raise Exception, conditionally
        return 0;
    }

    (*index)++;
    node->right = &ast[*index];

    if (!AstNode_FromPyObject(right, ast, index)) {
        // TODO: Raise exception, conditionally
        return 0;
    }

    return 1;
}

static AstNode*
AstTree_FromPyObject(PyObject* obj)
{
    // TODO: Better checks to ensure we've been given a valid AST?

    // Allocate enough memory to store the resulting AST.
    Py_ssize_t num_nodes = PyObject_Length(obj);
    if (num_nodes == -1) {
        // TODO: Raise Exception
        printf("Unable to get number of nodes.\n");
        return NULL;
    }


    AstNode *ast = malloc(num_nodes * sizeof(AstNode));
    if (ast == NULL) {
        // TODO: Raise Exception
        printf("Unable to allocate memory for AST.\n");
        return NULL;
    }

    Py_ssize_t index = 0;
    if (!AstNode_FromPyObject(obj, ast, &index)) {
        // TODO: Raise Exception
        printf("Unable to convert PyAst into CAst\n");
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
        printf("Unable to parse function arguments\n");
        return NULL;
    }

    AstNode *ast = AstTree_FromPyObject(obj);
    if (ast == NULL) {
        printf("Unable to construct AST\n");
        return NULL;
    };

    double result = (double) ast_evaluate(ast);
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

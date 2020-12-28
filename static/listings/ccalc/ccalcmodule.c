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
    }
}

static int
AstNode_FromPyObject(PyObject* obj, AstNode* ast)
{
    PyObject* type = PyObject_GetAttrString(obj, "type");
    if (type == NULL) {
        return -1;
    }

    long node_type = PyLong_AsLong(type);
    Py_DECREF(type);

    switch(node_type) {
    case AST_LITERAL: {

        PyObject* value = PyObject_GetAttrString(obj, "value");
        if (value == NULL) {
            return -1;
        }

        double v = PyFloat_AsDouble(value);
        Py_DECREF(value);

        ast->type = AST_LITERAL;
        ast->value = (float)v;

        return 0;
    }

    default:
        printf("Error! Field 'type' was not a valid node type.");
        return -1;
    }

}

static PyObject*
method_eval_ast(PyObject *self, PyObject *args)
{
    PyObject *obj = NULL;

    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    AstNode ast = {};

    if(!AstNode_FromPyObject(obj, &ast)) {
        return NULL;
    };

    float result = ast_evaluate(&ast);
    PyFloat_FromDouble(result);
}

static PyMethodDef FputsMethods[] = {
    {"eval_ast", method_eval_ast, METH_VARARGS, "Evaluate the given ast."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ccalcmodule = {
    PyModuleDef_HEAD_INIT,
    "_ccalc",
    "Simple calculator implemented in C",
    -1,
    FputsMethods
};

PyMODINIT_FUNC
PyInit__ccalc()
{
    return PyModule_Create(&ccalcmodule);
}

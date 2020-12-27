#include <stdio.h>

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

int
main()
{
    AstNode one = { .type = AST_LITERAL, .value = 1.0f };
    AstNode two = { .type = AST_LITERAL, .value = 2.0f };
    AstNode three = { .type = AST_LITERAL, .value = 3.0f };

    AstNode plus1 = { .type = AST_PLUS, .left = &one, .right = &two};
    AstNode example1 = { .type = AST_MULTIPLY, .left = &plus1, .right = &three};

    AstNode mul1 = { .type = AST_MULTIPLY, .left = &two, .right = &three};
    AstNode example2 = { .type = AST_PLUS, .left = &one, .right = &mul1};

    float result1 = ast_evaluate(&example1);
    float result2 = ast_evaluate(&example2);

    printf("Example 1: %.2f\n", result1);
    printf("Example 2: %.2f\n", result2);

    return 0;
}

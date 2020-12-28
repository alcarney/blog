import enum
import _ccalc

eval_ast = _ccalc.eval_ast

class AstNode:
    """Base AstNode class."""

    LITERAL = 0
    PLUS = 1
    MULTIPLY = 2

    def __init__(self, type=None, value=None, left=None, right=None):

        if left is not None and not isinstance(left, AstNode):
            left = Literal(left)

        if right is not None and not isinstance(right, AstNode):
            right = Literal(right)

        self.type = type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):

        name = self.__class__.__name__
        detail = ""

        if self.value is not None:
            detail = str(self.value)
        else:
            detail = f"{self.left}, {self.right}"

        return f"{name}<{detail}>"

    def __len__(self):
        left = 0 if self.left is None else len(self.left)
        right = 0 if self.right is None else len(self.right)

        return 1 + left + right

    def __add__(self, other):
        return Plus(self, other)

    def __radd__(self, other):
        return Plus(other, self)

    def __mul__(self, other):
        return Multiply(self, other)

    def __rmul__(self, other):
        return Multiply(other, self)


class Literal(AstNode):

    def __init__(self, value):
        if not isinstance(value, (int, float)):
            message = "Type '{}' is not a valid literal"
            raise TypeError(message.format(type(value)))

        super().__init__(type=AstNode.LITERAL, value=float(value))


class Plus(AstNode):

    def __init__(self, left, right):
        super().__init__(type=AstNode.PLUS, left=left, right=right)


class Multiply(AstNode):

    def __init__(self, left, right):
        super().__init__(type=AstNode.MULTIPLY, left=left, right=right)

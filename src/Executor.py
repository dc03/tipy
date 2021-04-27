from enum import Enum, auto, unique
from typing import *

from Error import *
from Parser import ASTNode, NodeType
from Token import TokenType


@unique
class IdentifierType(Enum):
    VARIABLE = auto()
    FUNCTION = auto()


class ReturnValue(BaseException):
    def __init__(self, value: ASTNode):
        self.value = value


class Executor:
    def __init__(self):
        self.environments = [dict()]

    def block_stmt(self, block: ASTNode) -> None:
        self.environments.append(dict())
        for stmt in block.children:
            self.exec_stmt(stmt)
        self.environments.pop()

    def if_stmt(self, stmt: ASTNode) -> None:
        cond = self.exec_expr(stmt.children[0])
        if (cond.type == NodeType.STRING and cond.children[0] != '') or \
                (cond.type == NodeType.NUMBER and cond.children[0] != 0.0):
            self.exec_stmt(stmt.children[1])
        elif stmt.children[2] != None:
            self.exec_stmt(stmt.children[2])

    def while_stmt(self, stmt: ASTNode) -> None:
        cond = self.exec_expr(stmt.children[0])
        while cond.children[0]:
            self.exec_stmt(stmt.children[1])
            cond = self.exec_expr(stmt.children[0])

    def var_decl(self, stmt: ASTNode) -> None:
        init = self.exec_expr(stmt.children[1])
        for environment in self.environments[::-1]:
            if any(name == stmt.children[0].lexeme for name in environment.keys()):
                environment[stmt.children[0].lexeme] = (
                    IdentifierType.VARIABLE, init)
        else:
            self.environments[-1][stmt.children[0].lexeme] = (
                IdentifierType.VARIABLE, init)

    def fun_decl(self, stmt: ASTNode) -> None:
        for environment in self.environments[::-1]:
            if any(name == stmt.children[0].lexeme for name in environment.keys()):
                environment[stmt.children[0].lexeme] = (
                    IdentifierType.FUNCTION, [stmt.children[1], stmt.children[2]])
        else:
            self.environments[-1][stmt.children[0].lexeme] = (
                IdentifierType.FUNCTION, [stmt.children[1], stmt.children[2]])

    def exec_stmt(self, stmt: ASTNode) -> None:
        if stmt.type == NodeType.BLOCK:
            self.block_stmt(stmt)
        elif stmt.type == NodeType.FUN:
            self.fun_decl(stmt)
        elif stmt.type == NodeType.IF:
            self.if_stmt(stmt)
        elif stmt.type == NodeType.RETURN:
            value = self.exec_expr(stmt.children[0])
            raise ReturnValue(value)
        elif stmt.type == NodeType.VAR:
            self.var_decl(stmt)
        elif stmt.type == NodeType.WHILE:
            self.while_stmt(stmt)
        elif stmt.type == NodeType.EXPR:
            self.exec_expr(stmt.children[0])

    def exec_expr(self, expr: ASTNode) -> ASTNode:
        if expr.type == NodeType.STRING or expr.type == NodeType.NUMBER:
            return expr
        elif expr.type == NodeType.ADDITION:
            left = self.exec_expr(expr.children[1])
            right = self.exec_expr(expr.children[2])
            if expr.children[0].type == TokenType.MODULO and (left.type != NodeType.NUMBER or right.type != NodeType.NUMBER):
                error('can only calculate remainders of numbers')
            if left.type != right.type:
                error(
                    f'cannot {"add" if expr.children[0].type == TokenType.PLUS else "subtract"} instances of {left.type} and {right.type}')
            elif left.type != NodeType.FUNCTION:
                if expr.children[0].type == TokenType.PLUS:
                    return ASTNode(NodeType.NUMBER, [left.children[0] + right.children[0]])
                elif expr.children[0].type == TokenType.MINUS:
                    return ASTNode(NodeType.NUMBER, [left.children[0] - right.children[0]])
                else:
                    return ASTNode(NodeType.NUMBER, [left.children[0] % right.children[0]])
            else:
                error('cannot do arithmetic on functions')
        elif expr.type == NodeType.MULTIPLICATION:
            left = self.exec_expr(expr.children[1])
            right = self.exec_expr(expr.children[2])
            if left.type != NodeType.NUMBER or right.type != NodeType.NUMBER:
                error('can only multiply or divide numbers')
            elif expr.children[0].type == TokenType.STAR:
                return ASTNode(NodeType.NUMBER, [left.children[0] * right.children[0]])
            elif right.children[1] == 0.0:
                error('cannot divide by zero')
            else:
                return ASTNode(NodeType.NUMBER, [left.children[0] / right.children[0]])
        elif expr.type == NodeType.EQUALITY:
            left = self.exec_expr(expr.children[1])
            right = self.exec_expr(expr.children[2])
            if left.type == NodeType.FUNCTION or right.type == NodeType.FUNCTION:
                error('cannot compare functions')

            if left.type != right.type:
                error('cannot compare unequal types')
            elif expr.children[0].type == TokenType.EQUALS_EQUALS:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] == right.children[0])])
            else:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] != right.children[0])])
        elif expr.type == NodeType.COMPARISION:
            left = self.exec_expr(expr.children[1])
            right = self.exec_expr(expr.children[2])
            if left.type == NodeType.FUNCTION or right.type == NodeType.FUNCTION:
                error('cannot compare functions')

            if left.type != right.type:
                error('cannot compare unequal types')
            elif expr.children[0].type == TokenType.GREATER:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] > right.children[0])])
            elif expr.children[0].type == TokenType.GREATER_EQUALS:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] >= right.children[0])])
            elif expr.children[0].type == TokenType.LESSER:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] < right.children[0])])
            elif expr.children[0].type == TokenType.LESSER_EQUALS:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] <= right.children[0])])
        elif expr.type == NodeType.BITSHIFT:
            left = self.exec_expr(expr.children[1])
            right = self.exec_expr(expr.children[2])
            if left.type == NodeType.FUNCTION or right.type == NodeType.FUNCTION:
                error('cannot bitshift functions')

            if left.type != NodeType.NUMBER or right.type != NodeType.NUMBER:
                error('can only bitshift numbers')
            elif expr.children[0].type == TokenType.LEFT_SHIFT:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] << right.children[0])])
            else:
                return ASTNode(NodeType.NUMBER, [int(left.children[0] >> right.children[0])])
        elif expr.type == NodeType.UNARY:
            left = self.exec_expr(expr.children[1])
            if left.type == NodeType.FUNCTION:
                error(f'cannot use "{expr.children[0].lexeme}" on functions')

            if expr.children[0].type == TokenType.BANG:
                return ASTNode(NodeType.NUMBER, [not left.children[0]])
            elif left.type != NodeType.NUMBER:
                error(f'can only use "{expr.children[0].lexeme}" on numbers')
            elif expr.children[0].type == TokenType.MINUS:
                return ASTNode(NodeType.NUMBER, [-left.children[0]])
            else:
                return ASTNode(NodeType.NUMBER, [~left.children[0]])
        elif expr.type == NodeType.LOGOR:
            left = self.exec_expr(expr.children[0])
            if left.children[0]:
                return ASTNode(NodeType.NUMBER, [1.0])
            else:
                return self.exec_expr(expr.children[1])
        elif expr.type == NodeType.LOGAND:
            left = self.exec_expr(expr.children[0])
            if not left.children[0]:
                return ASTNode(NodeType.NUMBER, [0.0])
            else:
                return self.exec_expr(expr.children[1])
        elif expr.type == NodeType.BITOR:
            left = self.exec_expr(expr.children[0])
            right = self.exec_expr(expr.children[1])
            if left.type != NodeType.NUMBER or right.type != NodeType.NUMBER:
                error('can only perform bitwise or on numbers')
            else:
                return ASTNode(NodeType.NUMBER, [left.children[0] | right.children[0]])
        elif expr.type == NodeType.BITXOR:
            left = self.exec_expr(expr.children[0])
            right = self.exec_expr(expr.children[1])
            if left.type != NodeType.NUMBER or right.type != NodeType.NUMBER:
                error('can only perform bitwise xor on numbers')
            else:
                return ASTNode(NodeType.NUMBER, [left.children[0] ^ right.children[0]])
        elif expr.type == NodeType.BITAND:
            left = self.exec_expr(expr.children[0])
            right = self.exec_expr(expr.children[1])
            if left.type != NodeType.NUMBER or right.type != NodeType.NUMBER:
                error('can only perform bitwise and on numbers')
            else:
                return ASTNode(NodeType.NUMBER, [left.children[0] ^ right.children[0]])
        elif expr.type == NodeType.IDENTIFIER:
            for environment in self.environments[::-1]:
                if any(name == expr.children[0] for name in environment):
                    var = environment[expr.children[0]]
                    if var[0] == IdentifierType.VARIABLE:
                        return var[1]
                    else:
                        return ASTNode(NodeType.FUNCTION, var[1])
            else:
                error(f'{expr.children[0]}: no such variable in scope')
        elif expr.type == NodeType.CALL:
            if expr.children[0].type == NodeType.IDENTIFIER and expr.children[0].children[0] == 'print':
                for arg in expr.children[1:]:
                    arg = self.exec_expr(arg)
                    print(arg.children[0])
                return ASTNode(NodeType.NUMBER, [1.0])
            function = self.exec_expr(expr.children[0])
            if function.type != NodeType.FUNCTION:
                error('cannot call a non-function')
            elif len(function.children[0]) != len(expr.children[1:]):
                error(
                    f'arity mismatch, expected {len(function.children[0])} arguments, got {len(expr.children[1:])}')
            else:
                self.environments.append(dict())
                for (param, arg) in zip(function.children[0], expr.children[1:]):
                    arg = self.exec_expr(arg)
                    if arg.type == NodeType.FUNCTION:
                        self.environments[-1][param.lexeme] = (
                            IdentifierType.FUNCTION, arg.children)
                    else:
                        self.environments[-1][param.lexeme] = (
                            IdentifierType.VARIABLE, arg)
                try:
                    for stmt in function.children[1].children:
                        self.exec_stmt(stmt)
                except ReturnValue as value:
                    return value.value
                self.environments.pop()

    def execute(self, stmts: List[ASTNode]) -> int:
        self.environments.append(dict())
        for stmt in stmts:
            self.exec_stmt(stmt)
        self.environments.pop()
        return 0

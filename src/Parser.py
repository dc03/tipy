from enum import Enum, auto, unique
from typing import *

from Error import *
from Token import Token, TokenType


@unique
class NodeType(Enum):
    STRING = auto()
    NUMBER = auto()
    FUNCTION = auto()
    IDENTIFIER = auto()

    LOGOR = auto()
    LOGAND = auto()
    BITOR = auto()
    BITXOR = auto()
    BITAND = auto()
    EQUALITY = auto()
    COMPARISION = auto()
    BITSHIFT = auto()
    ADDITION = auto()
    MULTIPLICATION = auto()
    UNARY = auto()
    CALL = auto()

    BLOCK = auto()
    IF = auto()
    WHILE = auto()
    RETURN = auto()
    EXPR = auto()

    VAR = auto()
    FUN = auto()


class ASTNode:
    def __init__(self, node_type: NodeType, children: List[Any]):
        self.type = node_type
        self.children = children


class Parser:
    def __init__(self):
        self.ast = []
        self.tokens = []
        self.current = 0
        self.in_function = False

    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens)

    def peek(self) -> Token:
        if self.is_at_end():
            print('bruh')
            return None
        else:
            return self.tokens[self.current]

    def previous(self) -> Token:
        if self.current == 0:
            error("No previous token at beginning")
        else:
            return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if self.is_at_end():
            error('EOF has been reached (parser)')
        else:
            self.current += 1
            return self.tokens[self.current - 1]

    def match(self, token_type: List[TokenType]) -> bool:
        if self.peek().type in token_type:
            self.advance()
            return True
        else:
            return False

    def unmatch(self) -> None:
        self.current -= 1

    def consume(self, token_type: TokenType, msg: str) -> Token:
        if self.match([token_type]):
            return self.previous()
        else:
            error(f'[line {self.previous().line}] {msg}')

    def expression(self) -> ASTNode:
        return self.logor()

    def logor(self) -> ASTNode:
        left = self.logand()

        while self.match([TokenType.OR]):
            right = self.logand()
            left = ASTNode(NodeType.LOGOR, [left, right])

        return left

    def logand(self) -> ASTNode:
        left = self.bitor()

        while self.match([TokenType.AND]):
            right = self.bitor()
            left = ASTNode(NodeType.LOGAND, [left, right])

        return left

    def bitor(self) -> ASTNode:
        left = self.bitxor()

        while self.match([TokenType.BITOR]):
            right = self.bitxor()
            left = ASTNode(NodeType.BITOR, [left, right])

        return left

    def bitxor(self) -> ASTNode:
        left = self.bitand()

        while self.match([TokenType.BITXOR]):
            right = self.bitand()
            left = ASTNode(NodeType.BITXOR, [left, right])

        return left

    def bitand(self) -> ASTNode:
        left = self.equality()

        while self.match([TokenType.BITAND]):
            right = self.equality()
            left = ASTNode(NodeType.BITAND, [left, right])

        return left

    def equality(self) -> ASTNode:
        left = self.comparison()

        while self.match([TokenType.BANG_EQUALS, TokenType.EQUALS_EQUALS]):
            op = self.previous()
            right = self.comparison()
            left = ASTNode(NodeType.EQUALITY, [op, left, right])

        return left

    def comparison(self) -> ASTNode:
        left = self.bitshift()

        while self.match([TokenType.GREATER, TokenType.GREATER_EQUALS, TokenType.LESSER, TokenType.LESSER_EQUALS]):
            op = self.previous()
            right = self.bitshift()
            left = ASTNode(NodeType.COMPARISION, [op, left, right])

        return left

    def bitshift(self) -> ASTNode:
        left = self.addition()

        while self.match([TokenType.LEFT_SHIFT, TokenType.RIGHT_SHIFT]):
            op = self.previous()
            right = self.addition()
            left = ASTNode(NodeType.BITSHIFT, [op, left, right])

        return left

    def addition(self) -> ASTNode:
        left = self.multiplication()

        while self.match([TokenType.PLUS, TokenType.MINUS, TokenType.MODULO]):
            op = self.previous()
            right = self.multiplication()
            left = ASTNode(NodeType.ADDITION, [op, left, right])

        return left

    def multiplication(self) -> ASTNode:
        left = self.unary()

        while self.match([TokenType.STAR, TokenType.SLASH]):
            op = self.previous()
            right = self.unary()
            left = ASTNode(NodeType.MULTIPLICATION, [op, left, right])

        return left

    def unary(self) -> ASTNode:
        if self.match([TokenType.BANG, TokenType.MINUS, TokenType.BITNOT]):
            op = self.previous()
            return ASTNode(NodeType.UNARY, [op, self.unary()])
        else:
            return self.call()

    def call(self) -> ASTNode:
        left = self.primary()

        if self.match([TokenType.LEFT_PAREN]):
            left = ASTNode(NodeType.CALL, [left])
            if self.peek().type != TokenType.RIGHT_PAREN:
                left.children.append(self.expression())
                while self.peek().type != TokenType.RIGHT_PAREN:
                    self.consume(TokenType.COMMA,
                                 "expect ',' after function argument")
                    left.children.append(self.expression())
            self.consume(TokenType.RIGHT_PAREN,
                         "expect ')' after function call")

        return left

    def primary(self) -> ASTNode:
        if self.match([TokenType.IDENTIFIER]):
            return ASTNode(NodeType.IDENTIFIER, [self.previous().lexeme])
        elif self.match([TokenType.NUMBER]):
            return ASTNode(NodeType.NUMBER, [float(self.previous().lexeme)])
        elif self.match([TokenType.STRING]):
            return ASTNode(NodeType.STRING, [self.previous().lexeme])
        elif self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN,
                         "expect ')' after grouping expression")
            return expr
        else:
            error(
                f"[line {self.peek().line}] Unexpected token '{self.peek().lexeme}' in expression")

    def expr_stmt(self) -> ASTNode:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "expect ';' after expression")
        return ASTNode(NodeType.EXPR, [expr])

    def block_stmt(self) -> ASTNode:
        block = []
        if self.peek().type != TokenType.RIGHT_BRACE:
            while self.peek().type != TokenType.RIGHT_BRACE:
                block.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "expect '}' after block statement")
        return ASTNode(NodeType.BLOCK, block)

    def if_stmt(self) -> ASTNode:
        cond = self.expression()
        self.consume(TokenType.LEFT_BRACE, "expect '{' after if statement")
        then_body = self.blockstmt()
        else_stmt = None
        if self.match([TokenType.ELSE]):
            if self.match([TokenType.IF]):
                else_stmt = self.if_stmt()
            else:
                self.consume(TokenType.LEFT_BRACE,
                             "expect '{' after else keyword")
                else_stmt = self.block_stmt()
        return ASTNode(NodeType.IF, [cond, then_body, else_stmt])

    def return_stmt(self) -> ASTNode:
        if not self.in_function:
            error(
                f"[line {self.previous().line}] cannot use 'return' outside a function")

        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "expect ';' after return statement")
        return ASTNode(NodeType.RETURN, [expr])

    def while_stmt(self) -> ASTNode:
        cond = self.expression()
        self.consume(TokenType.LEFT_BRACE, "expect '{' after while header")
        body = self.block_stmt()
        return ASTNode(NodeType.WHILE, [cond, body])

    def var_decl(self) -> ASTNode:
        name = self.previous()
        if self.match([TokenType.EQUALS]):
            init = self.expression()
            self.consume(TokenType.SEMICOLON,
                         "expect ';' after variable initializer")
            return ASTNode(NodeType.VAR, [name, init])
        else:
            self.unmatch()
            return self.expr_stmt()

    def fun_decl(self) -> ASTNode:
        name = self.consume(TokenType.IDENTIFIER,
                            "expect function  name after 'fun'")
        self.consume(TokenType.LEFT_PAREN, "expect '(' after function name")
        parameters = []
        if self.peek().type != TokenType.RIGHT_PAREN:
            parameters.append(self.consume(
                TokenType.IDENTIFIER, "expect parameter name"))
            while self.peek().type != TokenType.RIGHT_PAREN:
                self.consume(TokenType.COMMA,
                             "expect ',' after parameter name")
                parameters.append(self.consume(
                    TokenType.IDENTIFIER, "expect parameter name"))
        self.consume(TokenType.RIGHT_PAREN, "expect ')' after parameter names")
        self.consume(TokenType.LEFT_BRACE, "expect '{' after function header")
        prev = self.in_function
        self.in_function = True
        body = self.block_stmt()
        self.in_function = prev
        return ASTNode(NodeType.FUN, [name, parameters, body])

    def declaration(self) -> ASTNode:
        if self.is_at_end():
            return None

        if self.match([TokenType.IDENTIFIER]):
            return self.var_decl()
        elif self.match([TokenType.FUN]):
            return self.fun_decl()
        else:
            return self.statement()

    def statement(self) -> ASTNode:
        if self.match([TokenType.LEFT_BRACE]):
            return self.block_stmt()
        elif self.match([TokenType.IF]):
            return self.if_stmt()
        elif self.match([TokenType.RETURN]):
            return self.return_stmt()
        elif self.match([TokenType.WHILE]):
            return self.while_stmt()
        else:
            return self.expr_stmt()

    def parse(self, tokens: List[Token]) -> List[ASTNode]:
        self.tokens = tokens
        while not self.is_at_end():
            decl = self.declaration()
            if decl is not None:
                self.ast.append(decl)

        return self.ast

from enum import Enum, unique, auto
from typing import *


def escape(string: str) -> str:
    return string.replace('\n', '\\n').replace('\t', '\\t')


@unique
class TokenType(Enum):
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()

    LOGOR = auto()
    LOGAND = auto()
    BITOR = auto()
    BITXOR = auto()
    BITAND = auto()

    BANG_EQUALS = auto()
    EQUALS_EQUALS = auto()
    GREATER = auto()
    GREATER_EQUALS = auto()
    LESSER = auto()
    LESSER_EQUALS = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()

    PLUS = auto()
    MINUS = auto()
    MODULO = auto()
    STAR = auto()
    SLASH = auto()

    BANG = auto()
    BITNOT = auto()

    COMMA = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    AND = auto()
    OR = auto()
    RETURN = auto()

    SEMICOLON = auto()
    EQUALS = auto()
    FUN = auto()

    NEWLINE = auto()  # Ignored by the scanner
    WHITESPACE = auto()


class Token:
    def __init__(self, lexeme: str, token_type: TokenType, where: int):
        self.lexeme = lexeme
        self.type = token_type
        self.line = where

    def __str__(self) -> str:
        return f'\'{escape(self.lexeme)}\' {self.type}, line: {self.line}'

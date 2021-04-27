from io import TextIOWrapper
from typing import *

from Error import *
from Token import Token, TokenType


class Scanner:
    def __init__(self):
        self.tokens = []
        self.file = None
        self.next = ''
        self.line_number = 1
        self.current = -1

    def is_at_end(self) -> bool:
        return self.current >= len(self.file)

    def peek(self) -> str:
        return self.next

    def advance(self) -> str:
        if self.is_at_end():
            error('EOF has been reached')

        previous = self.next
        self.current += 1
        if (self.current >= len(self.file)):
            return previous
        else:
            self.next = self.file[self.current]
        return previous

    def match(self, what: str) -> bool:
        if self.peek() == what:
            self.advance()
            return True

        return False

    def scan_token(self) -> Token:
        if self.is_at_end():
            return None
        else:
            ch = self.advance()
            if ch == '\n':
                self.line_number += 1
                return Token('\n', TokenType.NEWLINE, self.line_number)
            elif ch == '|':
                if self.match('|'):
                    return Token('||', TokenType.LOGOR, self.line_number)
                else:
                    return Token('|', TokenType.BITOR, self.line_number)
            elif ch == '&':
                if self.match('&'):
                    return Token('&&', TokenType.LOGAND, self.line_number)
                else:
                    return Token('&', TokenType.BITAND, self.line_number)
            elif ch == '^':
                return Token('^', TokenType.BITXOR, self.line_number)
            elif ch == '!':
                if self.match('='):
                    return Token('!=', TokenType.BANG_EQUALS, self.line_number)
                else:
                    return Token('!', TokenType.BANG, self.line_number)
            elif ch == '=':
                if self.match('='):
                    return Token('==', TokenType.EQUALS_EQUALS, self.line_number)
                else:
                    return Token('=', TokenType.EQUALS, self.line_number)
            elif ch == '>':
                if self.match('='):
                    return Token('>=', TokenType.GREATER_EQUALS, self.line_number)
                elif self.match('>'):
                    return Token('>>', TokenType.RIGHT_SHIFT, self.line_number)
                else:
                    return Token('>', TokenType.GREATER, self.line_number)
            elif ch == '<':
                if self.match('='):
                    return Token('<=', TokenType.LESSER_EQUALS, self.line_number)
                elif self.match('<'):
                    return Token('<<', TokenType.LEFT_SHIFT, self.line_number)
                else:
                    return Token('<', TokenType.LESSER, self.line_number)
            elif ch == '+':
                return Token('+', TokenType.PLUS, self.line_number)
            elif ch == '-':
                return Token('-', TokenType.MINUS, self.line_number)
            elif ch == '%':
                return Token('%', TokenType.MODULO, self.line_number)
            elif ch == '*':
                return Token('*', TokenType.STAR, self.line_number)
            elif ch == '/':
                return Token('/', TokenType.SLASH, self.line_number)
            elif ch == '~':
                return Token('~', TokenType.BITNOT, self.line_number)
            elif ch == '(':
                return Token('(', TokenType.LEFT_PAREN, self.line_number)
            elif ch == ')':
                return Token(')', TokenType.RIGHT_PAREN, self.line_number)
            elif ch == '{':
                return Token('{', TokenType.LEFT_BRACE, self.line_number)
            elif ch == '}':
                return Token('}', TokenType.RIGHT_BRACE, self.line_number)
            elif ch == ';':
                return Token(';', TokenType.SEMICOLON, self.line_number)
            elif ch == ',':
                return Token(',', TokenType.COMMA, self.line_number)
            elif ch == '#':
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
                return Token('#', TokenType.WHITESPACE, self.line_number)
            elif ch.isalpha() or ch == '_':
                ident = ch
                while self.peek().isalnum() or self.peek() == '_':
                    ident += self.advance()

                if ident == 'and':
                    return Token('and', TokenType.AND, self.line_number)
                elif ident == 'or':
                    return Token('or', TokenType.OR, self.line_number)
                elif ident == 'else':
                    return Token('else', TokenType.ELSE, self.line_number)
                elif ident == 'fun':
                    return Token('fun', TokenType.FUN, self.line_number)
                elif ident == 'if':
                    return Token('if', TokenType.IF, self.line_number)
                elif ident == 'return':
                    return Token('return', TokenType.RETURN, self.line_number)
                elif ident == 'while':
                    return Token('while', TokenType.WHILE, self.line_number)
                else:
                    return Token(ident, TokenType.IDENTIFIER, self.line_number)
            elif ch.isdigit():
                num = ch
                while self.peek().isdigit():
                    num += self.advance()

                if self.match('.') and self.peek().isdigit():
                    num += '.'
                    while self.peek().isdigit():
                        num += self.advance()

                return Token(num, TokenType.NUMBER, self.line_number)
            elif ch == '\'':
                string = ''
                escapes = {'\\': '\\', 'b': '\b', 'f': '\f', 'n': '\n',
                           'r': '\r', 't': '\t', '"': '\"', '\'': '\''}
                while self.peek() != '\'':
                    next_ch = self.advance()
                    if next_ch == '\\':
                        next_ch = self.advance()
                        if next_ch in escapes.keys():
                            string += escapes[next_ch]
                        else:
                            print('Warning: unknown escape sequence \'\\',
                                  next_ch, '\'')
                    else:
                        string += next_ch

                self.advance()  # consume "'"
                return Token(string, TokenType.STRING, self.line_number)
            else:
                return Token(ch, TokenType.WHITESPACE, self.line_number)

    def scan(self, file: TextIOWrapper) -> List[Token]:
        self.file = file.read()
        while (tok := self.scan_token()) is not None:
            if tok.type not in [TokenType.NEWLINE, TokenType.WHITESPACE]:
                self.tokens.append(tok)

        return self.tokens

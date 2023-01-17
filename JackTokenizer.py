"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        full_input = input_stream.read()

        # Removes multi-lines comments from the code
        i = 1
        # Cannot use a for loop because len(full_input) isn't constant
        while i < len(full_input):
            if full_input[i - 1] == '/' and full_input[i] == '*':
                found = False
                for j in range(i, len(full_input)):
                    if full_input[j - 1] == '*' and full_input[j] == '/':
                        full_input = full_input[:i - 1] + full_input[j + 1:]
                        i -= 1
                        found = True
                        break
                if not found:
                    full_input = full_input[:i - 1]
                    break
            i += 1

        input_lines = full_input.splitlines()
        self.words = []
        self.i = -1
        # Splits the code to words (texts separated by whitespace)
        for line in input_lines:
            in_string = False  # Keeps track of whether we are in a string
            # Removes single-line comments from the code
            for i in range(len(line) - 1):
                if line[i] == '"':
                    in_string = not in_string
                if line[i] == '/' and line[i + 1] == '/' and not in_string:
                    line = line[:i]
                    break
            if not line == '':
                self.words.append(line)

        # Remove whitespaces for the end of the code
        has_code = False
        for i in range(len(self.words)-1, -1, -1):
            line = self.words[-1]
            for j in range(len(line) - 1, -1, -1):
                if not (line[j] == ' ' or line[j] == '\t'):
                    has_code = True
                    line = line[:j+1]
                    self.words = self.words[:i+1]
                    break
            if has_code:
                break

        self.current_token = None
        self.word_index = 0

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # We are not done with the current words
        if self.current_token and self.word_index + 1 < len(self.words[self.i]):
            return True

        # We have more words
        if self.i + 1 < len(self.words):
            return True

        # We are at the end of the last word
        return False
        pass

    def advance(self) -> bool:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if not self.has_more_tokens():
            return False

        # # We are not done with the current words
        # if self.current_token and self.word_index + 1 < len(self.words[self.i]):
        #     self.word_index += 1

        # We are not done with the current words
        if self.word_index + 1 < len(self.words[self.i]):
            self.word_index += 1

        # We have more words
        else:
            self.i += 1
            self.word_index = 0

        # Continue until passed all whitespaces
        while self.words[self.i][self.word_index] == ' ' or self.words[self.i][self.word_index] == '\t':
            self.word_index += 1
            if self.word_index == len(self.words[self.i]):
                self.i += 1
                self.word_index = 0

        if self.words[self.i][self.word_index] == '_' or self.words[self.i][self.word_index].isalpha():
            start = self.word_index
            # Increase the index in the word until the end of the word
            while self.word_index < len(self.words[self.i]) and (self.words[self.i][self.word_index].isalnum() or
                                                                 self.words[self.i][self.word_index] == '_'):
                self.word_index += 1
            self.current_token = self.words[self.i][start:self.word_index]
            self.word_index -= 1

        elif self.words[self.i][self.word_index].isnumeric():
            start = self.word_index
            # Increase the index in the word until the end of the number
            while self.word_index < len(self.words[self.i]) and self.words[self.i][self.word_index].isnumeric():
                self.word_index += 1
            self.current_token = int(self.words[self.i][start:self.word_index])
            self.word_index -= 1

        elif self.words[self.i][self.word_index] == '"':
            start = self.word_index
            self.word_index += 1
            # Check if it is an empty string
            if self.word_index == len(self.words[self.i]) or self.words[self.i][self.word_index] == '"':
                self.current_token = '""'
            else:
                # Increase the index in the word until the end of the string
                while self.word_index + 1 < len(self.words[self.i]) and not self.words[self.i][self.word_index] == '"':
                    self.word_index += 1
                self.current_token = self.words[self.i][start:self.word_index + 1]

        elif self.words[self.i][self.word_index] \
                in ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^',
                    '#']:
            self.current_token = self.words[self.i][self.word_index]

        return True

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if type(self.current_token) is int:
            return "INT_CONST"

        if self.current_token[0] == '"':
            return "STRING_CONST"

        if self.current_token \
                in ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^',
                    '#']:
            return "SYMBOL"

        if self.current_token \
                in ['class', 'constructor', 'function', 'method', 'field',
                    'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                    'false', 'null', 'this', 'let', 'do', 'if', 'else',
                    'while', 'return']:
            return "KEYWORD"

        return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return self.current_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        return self.current_token[1:-1]


if __name__ == '__main__':
    inp = open("Square/Main.jack", "r")
    a = JackTokenizer(inp)
    while a.advance():
        print(a.token_type())
        if a.token_type() == "STRING_CONST":
            print(a.string_val())
        else:
            print(a.symbol(), a.int_val(), a.keyword(), a.keyword())
        print()

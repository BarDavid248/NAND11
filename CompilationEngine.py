"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer
from SymbolTable import *
from VMWriter import VMWriter
from Constants import *

KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"

xml_element_names = {KEYWORD: 'keyword',
                     SYMBOL: 'symbol',
                     IDENTIFIER: 'identifier',
                     INT_CONST: 'integerConstant',
                     STRING_CONST: 'stringConstant'}

statement_comp_funcs = {"let": lambda self: self.compile_let(),
                        "do": lambda self: self.compile_do(),
                        "while": lambda self: self.compile_while(),
                        "if": lambda self: self.compile_if(),
                        "return": lambda self: self.compile_return()}

tokenizer_value_funcs = {KEYWORD: lambda tokenizer: tokenizer.keyword(),
                         SYMBOL: lambda tokenizer: tokenizer.symbol(),
                         IDENTIFIER: lambda tokenizer: tokenizer.identifier(),
                         INT_CONST: lambda tokenizer: tokenizer.int_val(),
                         STRING_CONST: lambda tokenizer: tokenizer.string_val()}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")

        self.tokenizer = input_stream
        self.output_stream = output_stream
        self.writer = VMWriter(output_stream)

        self.symbol_table = SymbolTable()

        self.class_name = ''
        self.label_num = 1

    # added
    def compare(self, token_type, value=None):
        return self.tokenizer.token_type() == token_type and (value is None or self.current_token() == value)

    # added
    def start_root(self, name):
        pass
        # self.output_stream.write(self.indent_count * '\t' + f"<{name}>\n")
        # self.indent_count += 1

    # added
    def end_root(self, name):
        pass
        # self.indent_count -= 1
        # self.output_stream.write(self.indent_count * '\t' + f"</{name}>\n")

    # added
    def add_element(self, _name=None, _value=None):
        value = self.current_token() if _value is None else _value
        if self.tokenizer.token_type() != IDENTIFIER or not self.symbol_table.is_symbol(value):
            name = xml_element_names[self.tokenizer.token_type()] if _name is None else _name
        else:
            name = f"{xml_element_names[IDENTIFIER]}_{self.symbol_table.type_of(value)}_{self.symbol_table.kind_of(value)}_{self.symbol_table.index_of(value)}"

        #self.output_stream.write(self.indent_count * '\t' + f"<{name}> {value} </{name}>\n")

    # added
    def compile_token(self, condition=True, advance=True):
        if condition:
            # self.add_element()
            pass
        else:
            raise Exception(f"got type:{self.tokenizer.token_type()}, value:{self.current_token()}")

        if advance:
            self.tokenizer.advance()

    # added
    def is_type(self):
        return (self.compare(KEYWORD) and self.current_token() in ("int", "char", "boolean")) \
               or self.compare(IDENTIFIER)

    # added
    def current_token(self):
        token = tokenizer_value_funcs[self.tokenizer.token_type()](self.tokenizer)
        return token

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # 'class'
        if self.tokenizer.advance() and self.compare(KEYWORD, "class"):
            self.start_root('class')
            self.compile_token()

            # className
            self.class_name = self.current_token()
            self.compile_token(self.compare(IDENTIFIER))

            # '{'
            self.compile_token(self.compare(SYMBOL, '{'))

            # classVarDec*
            while self.current_token() in ("static", "field"):
                self.compile_class_var_dec()

            # subroutineDec*
            while self.current_token() in ("constructor", "function", "method"):
                self.compile_subroutine()

            # '}'
            self.compile_token(self.compare(SYMBOL, '}'))

            self.end_root('class')

            self.symbol_table.print()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.start_root('classVarDec')

        # 'static' | 'field'
        kind = self.current_token()
        if kind not in ("static", "field"):
            raise Exception
        self.compile_token()

        # type
        _type = self.current_token()
        self.compile_token(self.is_type())

        has_more = True
        while has_more:
            # varName
            name = self.current_token()
            self.symbol_table.define(name, _type, kind)
            self.compile_token(self.compare(IDENTIFIER))

            # ','
            if self.compare(SYMBOL, ','):
                self.compile_token()
            else:
                has_more = False

        # ';'
        self.compile_token(self.compare(SYMBOL, ';'))

        self.end_root('classVarDec')

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """

        self.start_root('subroutineDec')

        self.symbol_table.start_subroutine()

        # 'constructor' | 'function' | 'method'
        subroutine_type = self.current_token()
        self.compile_token()

        # ('void' | type)
        self.compile_token(self.compare(KEYWORD, 'void') or self.is_type())

        # subroutineName
        subroutine_name = self.current_token()
        self.compile_token(self.compare(IDENTIFIER))

        # '('
        self.compile_token(self.compare(SYMBOL, '('))

        # parameterList
        n = self.compile_parameter_list()

        # ')'
        self.compile_token(self.compare(SYMBOL, ')'))

        self.writer.write_function(f"{self.class_name}.{subroutine_name}", n+1 if subroutine_type == 'method' else n)

        # subroutineBody
        self.start_root('subroutineBody')

        # '{'
        self.compile_token(self.compare(SYMBOL, '{'))

        # varDec*
        while self.compare(KEYWORD, 'var'):
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self.compile_token(self.compare(SYMBOL, '}'))

        self.end_root('subroutineBody')

        self.end_root('subroutineDec')

    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        self.start_root('parameterList')

        count = 0

        has_more = self.is_type()
        while has_more:
            # type
            _type = self.current_token()
            self.compile_token()

            # varName
            name = self.current_token()
            self.symbol_table.define(name, _type, ARG)
            self.compile_token(self.compare(IDENTIFIER))

            count += 1

            # ','
            if self.compare(SYMBOL, ','):
                self.compile_token()
            else:
                has_more = False

        self.end_root('parameterList')

        return count

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.start_root('varDec')

        # 'var'
        self.compile_token()

        # type
        _type = self.current_token()
        self.compile_token(self.is_type())

        has_more = True
        while has_more:
            # varName
            name = self.current_token()
            self.symbol_table.define(name, _type, VAR)
            self.compile_token(self.compare(IDENTIFIER))

            # ','
            if self.compare(SYMBOL, ','):
                self.compile_token()
            else:
                has_more = False

        # ';'
        self.compile_token(self.compare(SYMBOL, ';'))

        self.end_root('varDec')

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # Your code goes here!
        self.start_root('statements')

        while self.tokenizer.token_type() == KEYWORD and self.current_token() in statement_comp_funcs.keys():
            statement_comp_funcs[self.current_token()](self)

        self.end_root('statements')

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.start_root('doStatement')

        # 'do'
        self.compile_token()

        # subroutineName | className | varName
        identifier = self.current_token()
        subroutine = identifier
        self.compile_token(self.compare(IDENTIFIER))

        # ('.' subroutineName)?
        if self.compare(SYMBOL, '.'):
            # '.'
            self.compile_token()
            # subroutineName
            subroutine += f".{self.current_token()}"
            self.compile_token(self.compare(IDENTIFIER))

        if self.symbol_table.is_symbol(identifier):  # if method
            self.symbol_table.define('this', self.symbol_table.type_of(identifier), ARG)
            # TODO: self.writer.write_push(this)

        # '('
        self.compile_token(self.compare(SYMBOL, '('))
        # expressionList
        n = self.compile_expression_list()
        # ')'
        self.compile_token(self.compare(SYMBOL, ')'))

        # ';'
        self.compile_token(self.compare(SYMBOL, ';'))

        self.writer.write_call(subroutine, n)
        self.writer.write_pop(TEMP, 0)

        self.end_root('doStatement')

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.start_root('letStatement')

        is_arr = False

        # 'let'
        self.compile_token()

        # varName
        variable = self.current_token()
        self.compile_token(self.compare(IDENTIFIER))

        # ('[' expression ']')?
        if self.compare(SYMBOL, '['):
            # '['
            self.compile_token()
            self.writer.write_push(self.symbol_table.segment_of(variable), self.symbol_table.index_of(variable))
            # expression
            self.compile_expression()

            self.writer.write_arithmetic(biop_dict['+'])

            # ']'
            self.compile_token(self.compare(SYMBOL, ']'))

            is_arr = True

        # '='
        self.compile_token(self.compare(SYMBOL, '='))

        # expression
        self.compile_expression()

        if is_arr:
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
        else:
            self.writer.write_pop(self.symbol_table.segment_of(variable), self.symbol_table.index_of(variable))

        # ';'
        self.compile_token(self.compare(SYMBOL, ';'))

        self.end_root('letStatement')

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.start_root('whileStatement')

        # 'while'
        self.compile_token()

        self.writer.write_label(f"L{self.label_num}")

        # '('
        self.compile_token(self.compare(SYMBOL, '('))

        # expression
        self.compile_expression()

        # ')'
        self.compile_token(self.compare(SYMBOL, ')'))

        self.writer.write_arithmetic(unop_dict['-'])
        self.writer.write_if(f"L{self.label_num+1}")

        # '{'
        self.compile_token(self.compare(SYMBOL, '{'))

        # statements
        self.compile_statements()

        # '}'
        self.compile_token(self.compare(SYMBOL, '}'))

        self.writer.write_goto(f"L{self.label_num}")

        self.writer.write_label(f"L{self.label_num+1}")

        self.label_num += 1

        self.end_root('whileStatement')

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.start_root('returnStatement')

        # 'return'
        self.compile_token()

        # expression?
        if not self.compare(SYMBOL, ';'):
            self.compile_expression()

        # ';'
        self.compile_token(self.compare(SYMBOL, ';'))

        self.end_root('returnStatement')

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.start_root('ifStatement')

        # 'if'
        self.compile_token()

        # '('
        self.compile_token(self.compare(SYMBOL, '('))

        # expression
        self.compile_expression()

        # ')'
        self.compile_token(self.compare(SYMBOL, ')'))

        self.writer.write_arithmetic(unop_dict['-'])
        self.writer.write_if(f"L{self.label_num}")

        # '{'
        self.compile_token(self.compare(SYMBOL, '{'))

        # statements
        self.compile_statements()

        # '}'
        self.compile_token(self.compare(SYMBOL, '}'))

        # ('else' '{' statements '}')?
        if self.compare(KEYWORD, 'else'):
            self.writer.write_goto(f"L{self.label_num + 1}")

            # 'else'
            self.compile_token()
            self.writer.write_label(f"L{self.label_num}")

            # '{'
            self.compile_token(self.compare(SYMBOL, '{'))

            # statements
            self.compile_statements()

            # '}'
            self.compile_token(self.compare(SYMBOL, '}'))
            self.writer.write_label(f"L{self.label_num + 1}")

            self.label_num += 2
        else:
            self.writer.write_label(f"L{self.label_num}")
            self.label_num += 1

        self.end_root('ifStatement')

    def compile_expression(self) -> None:
        """Compiles an expression."""

        self.start_root('expression')

        # term
        self.compile_term()

        # (op term)*
        while self.compare(SYMBOL) and self.current_token() in ('+', '-', '*', '/', '=', '>', '<', '&', '|'):
            # op
            op = self.current_token()
            self.compile_token()

            # term
            self.compile_term()

            # compile op
            if op in biop_dict.keys():
                self.writer.write_arithmetic(biop_dict[op])
            elif op == '*':
                self.writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.writer.write_call('Math.divide', 2)

        self.end_root('expression')

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        self.start_root('term')

        # integerConstant | stringConstant | keywordConstant
        if self.tokenizer.token_type() == INT_CONST:
            self.writer.write_push(CONST, self.current_token())
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == STRING_CONST:
            # TODO: implement string
            self.tokenizer.advance()
        elif self.compare(KEYWORD) and self.current_token() in ('true', 'false', 'null', 'this'):
            # TODO: implement true, false, null and this
            self.tokenizer.advance()

        # '(' expression ')'
        elif self.compare(SYMBOL, '('):
            # '('
            self.compile_token()
            # expression
            self.compile_expression()
            # ')'
            self.compile_token(self.compare(SYMBOL, ')'))

        # unaryOp term
        elif self.compare(SYMBOL) and self.current_token() in "-~^#":
            # unaryOp
            self.compile_token()
            # term
            self.compile_term()

        # varName | varName '[' expression ']' | subroutineCall
        elif self.compare(IDENTIFIER):
            prev_name = xml_element_names[self.tokenizer.token_type()]
            prev_value = self.current_token()

            self.tokenizer.advance()

            # varName '[' expression ']'
            if self.compare(SYMBOL, '['):
                # varName
                self.add_element(prev_name, prev_value)
                self.writer.write_push(self.symbol_table.segment_of(prev_value), self.symbol_table.index_of(prev_value))
                # '['
                self.compile_token()
                # expression
                self.compile_expression()
                # ']'
                self.compile_token(self.compare(SYMBOL, ']'))

                self.writer.write_arithmetic(biop_dict['+'])
                self.writer.write_pop("POINTER", 1)
                self.writer.write_push("THAT", 0)

            # subroutineCall
            elif self.compare(SYMBOL, '(') or self.compare(SYMBOL, '.'):
                # subroutineName | className | varName
                self.add_element(prev_name, prev_value)

                # ('.' subroutineName)?
                if self.compare(SYMBOL, '.'):
                    # '.'
                    self.compile_token()
                    # subroutineName
                    self.compile_token(self.compare(IDENTIFIER))

                # '('
                self.compile_token(self.compare(SYMBOL, '('))
                # expressionList
                self.compile_expression_list()
                # ')'
                self.compile_token(self.compare(SYMBOL, ')'))

            # varName
            else:
                self.writer.write_push(self.symbol_table.segment_of(prev_value), self.symbol_table.index_of(prev_value))

        else:
            raise Exception(f'Invalid Expression. curr_token: {self.current_token()}')

        self.end_root('term')

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.start_root('expressionList')

        count = 0

        # ( expression (',' expression)* )?
        if not self.compare(SYMBOL, ')'):
            # expression
            self.compile_expression()
            count += 1

            # (',' expression)*
            while self.compare(SYMBOL, ','):
                # ','
                self.compile_token()

                # expression
                self.compile_expression()
                count += 1

        self.end_root('expressionList')

        return count

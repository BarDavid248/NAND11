"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from Constants import *

kind_to_segment = {
    FIELD: THIS,
    STATIC: STATIC,
    VAR: LOCAL,
    ARG: ARG
}

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # {name : (type, kind, index)}
        self._class_table = dict()
        self._subroutine_table = dict()

        self._indices = {FIELD: 0, STATIC: 0, VAR: 0, ARG: 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self._subroutine_table = dict()
        self._indices[VAR] = 0
        self._indices[ARG] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        self._table_kind(kind)[name] = (type, kind, self._indices[kind])
        self._indices[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self._indices[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        return self._table_name(name)[name][1]

    # added
    def segment_of(self, name: str) -> str:
        return kind_to_segment[self._table_name(name)[name][1]]

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        return self._table_name(name)[name][0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        return self._table_name(name)[name][2]

    # added
    def _table_kind(self, kind):
        if kind in (FIELD, STATIC):
            return self._class_table
        elif kind in (VAR, ARG):
            return self._subroutine_table
        else:
            raise Exception

    # added
    def _table_name(self, name):
        if name in self._subroutine_table.keys():
            return self._subroutine_table
        elif name in self._class_table.keys():
            return self._class_table
        else:
            Exception(f'Tried referencing a variable the doesn\'t exist: {name}')

    # added
    def is_symbol(self, name):
        value = (name in self._class_table.keys()) or (name in self._subroutine_table.keys())
        print(f"checking symbol {name}: {value}")
        return value

    def print(self):
        print('Subroutine table:')
        for item in self._subroutine_table.items():
            print(f"{item[0]}: {item[1]}")
        print('Class table:')
        for item in self._class_table.items():
            print(f"{item[0]}: {item[1]}")

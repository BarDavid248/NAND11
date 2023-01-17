CONST = 'constant'
ARG = 'argument'
VAR = 'var'
LOCAL = 'local'
STATIC = 'static'
FIELD = 'field'
THIS = 'this'
THAT = 'that'
POINTER = 'pointer'
TEMP = 'temp'

biop_dict = {'+': 'add',
             '-': 'sub',
             '=': 'eq',
             '>': 'gt',
             '<': 'lt',
             '&': 'and',
             '|': 'or'}

unop_dict = {'-': 'neg',
             '~': 'not',
             '^': 'shiftleft',
             '#': 'shiftright'}

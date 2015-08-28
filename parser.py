# coding: utf-8
import sys
from pprint import pprint
from datetime import datetime

from funcparserlib.parser import some, a, many, skip, forward_decl
from funcparserlib.lexer import make_tokenizer, Token


__classes = {}


def register(cls):
    __classes[cls.value] = cls

    def init(*args, **kwargs):
        return cls(*args, **kwargs)
    return init


def choose_class(token):
    return __classes[token.value]


class AST:
    children = ()


class Operator(AST):
    value = None
    operator = None

    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return self.value
        return "%s %s %s" % (self.__class__.__name__, self.value, map(repr, self.children))


class LogicalOperator(Operator):
    def compile(self):
        lft, right = self.children
        return {self.operator: [lft.compile(), right.compile()]}


class CmpOperator(Operator):
    def compile(self):
        lft, right = self.children
        return {lft.compile(): {self.operator: right.compile()}}


class Function(AST):
    func_map = {
        'me': lambda: 'zubchick',
        'today': lambda: int(datetime.today().strftime('%s')),
    }

    def __init__(self, text):
        self.name = text.text

    def __repr__(self):
        return "%s()" % (self.name)

    def compile(self):
        return self.func_map[self.name]()


class Text(AST):
    def __init__(self, tok):
        self.text = tok.value

    def __repr__(self):
        return "Text(%s)" % self.text

    def compile(self):
        return self.text


@register
class AndOp(LogicalOperator):
    value = 'AND'
    operator = '$and'


@register
class OrOp(LogicalOperator):
    value = 'OR'
    operator = '$or'


@register
class GtOp(CmpOperator):
    value = '>'
    operator = '$gt'


@register
class LtOp(CmpOperator):
    value = '<'
    operator = '$lt'


@register
class GteOp(CmpOperator):
    value = '<='
    operator = '$lte'


@register
class LteOp(CmpOperator):
    value = '>='
    operator = '$gte'


@register
class RegexpOp(CmpOperator):
    value = '~='
    operator = '$regex'


@register
class ContainsOp(CmpOperator):
    value = '@='
    operator = '$in'


@register
class EqOp(CmpOperator):
    value = '='
    operator = '$eq'


from funcparserlib.lexer import make_tokenizer, Token

SPECS = [
    ('CMP', (r'~=|>=|<=|<|>|=',)),
    ('BR', (r'\(|\)',)),
    ('OP', (r'AND|OR',)),
    ('SPACE', (r'[ \t\r\n]+',)),
    ('STRING', (r'"(?:[^"\\]|\\.)*"',)),
    ('WORD', ('\w+',)),
]

tokenizer = make_tokenizer(SPECS)


def tokenize(query):
    return [tok for tok in tokenizer(query) if tok.type != 'SPACE']

# operator: '~=' | '>=' | '<=' | '<' | '>' | '='
operator = some(lambda tok: tok.type == 'CMP') >> choose_class

# value: STRING | WORD
string = some(lambda tok: tok.type == 'STRING') >> Text
word = some(lambda tok: tok.type == 'WORD') >> Text
value = string | word

# function: WORD '(' ')'
open_brace = skip(a(Token('BR', '(')))
close_brace = skip(a(Token('BR', ')')))
function = word + open_brace + close_brace >> Function

# field_expr: WORD operator value
field_expr = (word + operator + (function | value)) >> (lambda x: x[1]([x[0], x[2]]))

OR = a(Token('OP', 'OR')) >> choose_class
AND = a(Token('OP', 'AND')) >> choose_class


def eval(data):
    lft, args = data
    import ipdb; ipdb.set_trace()
    return reduce(lambda arg1, (f, arg2): f([arg1, arg2]), args, lft)


expr = forward_decl()
base_expr = field_expr | open_brace + expr + close_brace
and_expr = (base_expr + many(AND + base_expr)) >> eval
or_expr = (and_expr + many(OR + and_expr)) >> eval

expr.define(or_expr)
expr.parse(tokenize('author=zubchick AND title~=qwe AND a=3 AND b=4'))
import ipdb; ipdb.set_trace()
# проверяем
from funcparserlib.util import pretty_tree as pretty

query = 'author=zubchick AND title~=test AND pub_date>=today()'
query = sys.argv[1] if len(sys.argv) > 1 else query
res = expr.parse(tokenize(query))

print "Original query:"
print query
print
print "AST:"
print pretty(res, lambda x: getattr(x, 'children', []), lambda x: x.__class__.__name__)
print
print "Mongo request:"
print pprint(res.compile())

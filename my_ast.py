from enum import Enum, auto
from typing import List, Union, Optional

class Loc:
    def __init__(self, start: int, end_pos: int, filename: str):
        self.start = start
        self.end_pos = end_pos
        self.filename = filename

class BinaryOp(Enum):
    Add = "Add"
    Sub = "Sub"
    Mul = "Mul"
    Div = "Div"
    Rem = "Rem"
    Eq  = "Eq"
    Neq = "Neq"
    Lt  = "Lt"
    Gt  = "Gt"
    Lte = "Lte"
    Gte = "Gte"
    And = "And"
    Or  = "Or"

class Parameter:
    def __init__(self, text: str, location: Loc):
        self.text = text
        self.location = location

class Term:
    pass

class Int(Term):
    def __init__(self, value: int, location: Loc):
        self.value = value
        self.location = location

class Str(Term):
    def __init__(self, value: str, location: Loc):
        self.value = value
        self.location = location

class Bool(Term):
    def __init__(self, value: bool, location: Loc):
        self.value = value
        self.location = location

class Binary(Term):
    def __init__(self, lhs: Term, rhs: Term, op: BinaryOp, location: Loc):
        self.lhs = lhs
        self.rhs = rhs
        self.op = op
        self.location = location

class Var(Term):
    def __init__(self, text: str, location: Loc):
        self.text = text
        self.location = location

class If(Term):
    def __init__(self, condition: Term, then: Term, otherwise: Term, location: Loc):
        self.condition = condition
        self.then = then
        self.otherwise = otherwise
        self.location = location

class Let(Term):
    def __init__(self, name: Parameter, value: Term, next: Term, location: Loc):
        self.name = name
        self.value = value
        self.next = next
        self.location = location

class Call(Term):
    def __init__(self, callee: Term, arguments: List[Term], location: Loc):
        self.callee = callee
        self.arguments = arguments
        self.location = location

class Function(Term):
    def __init__(self, parameters: List[Parameter], value: Term, location: Loc, name: Optional[str]):
        self.parameters = parameters
        self.value = value
        self.location = location
        self.name = name

class Print(Term):
    def __init__(self, value: Term, location: Loc):
        self.value = value
        self.location = location

class First(Term):
    def __init__(self, value: Term, location: Loc):
        self.value = value
        self.location = location

class Second(Term):
    def __init__(self, value: Term, location: Loc):
        self.value = value
        self.location = location

class Tuple(Term):
    def __init__(self, first: Term, second: Term, location: Loc):
        self.first = first
        self.second = second
        self.location = location

class File:
    def __init__(self, name: str, expression: Term, location: Loc):
        self.name = name
        self.expression = expression
        self.location = location

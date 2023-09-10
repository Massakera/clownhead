type
  Loc* = object
    start, end: int
    filename: string

  BinaryOp* = enum
    Add, Sub, Mul, Div, Rem, Eq, Neq, Lt, Gt, Lte, Gte, And, Or

  Parameter* = object
    text: string
    location: Loc

  Term* = ref object of RootObj
    case kind*: string
    of "Int":
      value: int
      location: Loc
    of "Str":
      value: string
      location: Loc
    of "Bool":
      value: bool
      location: Loc
    of "Binary":
      lhs, rhs: Term
      op: BinaryOp
      location: Loc
    of "Var":
      text: string
      location: Loc
    of "If":
      condition: Term
      then: Term
      otherwise: Term
      location: Loc
    of "Let":
      name: Parameter
      value: Term
      next: Term
      location: Loc
    of "Call":
      callee: Term
      arguments: seq[Term]
      location: Loc
    of "Function":
      parameters: seq[Parameter]
      value: Term
    of "Print":
      value: Term
      location: Loc
    of "First":
      value: Term
      location: Loc
    of "Second":
      value: Term
      location: Loc
    of "Tuple":
      first: Term
      second: Term
      location: Loc

  File* = object
    name: string
    expression: Term
    location: Loc


type
  ASTNode = object of RootObj
  IntNode = object of ASTNode
    value: int
  BinaryNode = object of ASTNode
    lhs, rhs: ASTNode
    op: char  # For simplicity

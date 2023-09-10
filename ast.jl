mutable struct Loc
    start::Int
    end::Int
    filename::String
end

@enum BinaryOp Add Sub Mul Div Rem Eq Neq Lt Gt Lte Gte And Or

mutable struct Parameter
    text::String
    location::Loc
end

abstract type Term end

mutable struct IntTerm <: Term
    value::Int
    location::Loc
end

mutable struct StrTerm <: Term
    value::String
    location::Loc
end

mutable struct BoolTerm <: Term
    value::Bool
    location::Loc
end

mutable struct BinaryTerm <: Term
    lhs::Term
    rhs::Term
    op::BinaryOp
    location::Loc
end

mutable struct VarTerm <: Term
    text::String
    location::Loc
end

mutable struct IfTerm <: Term
    condition::Term
    then::Term
    otherwise::Term
    location::Loc
end

mutable struct LetTerm <: Term
    name::Parameter
    value::Term
    next::Term
    location::Loc
end

mutable struct CallTerm <: Term
    callee::Term
    arguments::Vector{Term}
    location::Loc
end

mutable struct FunctionTerm <: Term
    parameters::Vector{Parameter}
    value::Term
    location::Loc
end

mutable struct PrintTerm <: Term
    value::Term
    location::Loc
end

mutable struct FirstTerm <: Term
    value::Term
    location::Loc
end

mutable struct SecondTerm <: Term
    value::Term
    location::Loc
end

mutable struct TupleTerm <: Term
    first::Term
    second::Term
    location::Loc
end

mutable struct File
    name::String
    expression::Term
    location::Loc
end

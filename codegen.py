from llvmlite import ir
from llvmlite.ir import values
from typing import Dict, Tuple, Union
from enum import Enum

class SymbolTable:
    def __init__(self):
        self.variables: Dict[str, values.Value] = {}
        self.functions: Dict[str, ir.Function] = {}

    def insert_variable(self, name: str, value: values.Value):
        self.variables[name] = value

    def insert_function(self, name: str, func: ir.Function):
        self.functions[name] = func

    def lookup(self, name: str) -> Tuple[str, Union[values.Value, None]]:
        if name in self.variables:
            return ("variable", self.variables[name])
        elif name in self.functions:
            return ("function", self.functions[name])
        else:
            return ("none", None)
        
class SymbolType(Enum):
    Function = 1
    Variable = 2

def emit_add(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    if lhs.type.is_integer:
        return builder.add(lhs, rhs, name="addtmp")
    else:
        raise CodeGenError("Unsupported operand type for addition")

def emit_sub(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    if lhs.type.is_integer:
        return builder.sub(lhs, rhs, name="subtmp")
    else:
        raise CodeGenError("Unsupported operand type for subtraction")

def emit_mul(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    return builder.mul(lhs, rhs, name="mul_tmp")

def emit_div(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.sdiv(lhs, rhs, name="div_tmp")
    else:
        raise CodeGenError("Unsupported type for division")

def emit_rem(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.srem(lhs, rhs, name="rem_tmp")
    else:
        raise CodeGenError("Unsupported type for remainder")

def emit_eq(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('==', lhs, rhs, name="eq_tmp")
    else:
        raise CodeGenError("Unsupported type for equality check")

def emit_neq(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('!=', lhs, rhs, name="neq_tmp")
    else:
        raise CodeGenError("Unsupported type for not-equal check")

def emit_lt(builder: ir.IRBuilder, lhs: values.Value, rhs: values.Value) -> values.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('<', lhs, rhs, name="lt_tmp")
    else:
        raise CodeGenError("Unsupported type for less-than check")

class CodeGenError(Exception):
    pass

class BinaryOp(Enum):
    Add = 1
    Sub = 2
    Mul = 3
    Div = 4
    Rem = 5
    Eq = 6
    Neq = 7
    Lt = 8
    Gt = 9
    Lte = 10
    Gte = 11
    And = 12
    Or = 13

def emit_gt(builder: ir.IRBuilder, lhs: ir.Value, rhs: ir.Value) -> ir.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('>', lhs, rhs, name="gt_tmp")
    else:
        raise CodeGenError("Unsupported type for greater-than check")

def emit_lte(builder: ir.IRBuilder, lhs: ir.Value, rhs: ir.Value) -> ir.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('<=', lhs, rhs, name="lte_tmp")
    else:
        raise CodeGenError("Unsupported type for less-than or equal-to check")

def emit_gte(builder: ir.IRBuilder, lhs: ir.Value, rhs: ir.Value) -> ir.Value:
    int32_type = ir.IntType(32)
    if lhs.type == int32_type and rhs.type == int32_type:
        return builder.icmp_signed('>=', lhs, rhs, name="gte_tmp")
    else:
        raise CodeGenError("Unsupported type for greater-than or equal-to check")

def emit_and(builder: ir.IRBuilder, lhs: ir.Value, rhs: ir.Value) -> ir.Value:
    int1_type = ir.IntType(1)
    if lhs.type == int1_type and rhs.type == int1_type:
        return builder.and_(lhs, rhs, name="and_tmp")
    else:
        raise CodeGenError("Unsupported type for logical AND")

def emit_or(builder: ir.IRBuilder, lhs: ir.Value, rhs: ir.Value) -> ir.Value:
    int1_type = ir.IntType(1)
    if lhs.type == int1_type and rhs.type == int1_type:
        return builder.or_(lhs, rhs, name="or_tmp")
    else:
        raise CodeGenError("Unsupported type for logical OR")

BINARY_OP_DISPATCH = {
    BinaryOp.Add: emit_add,
    BinaryOp.Sub: emit_sub,
    BinaryOp.Mul: emit_mul,
    BinaryOp.Div: emit_div,
    BinaryOp.Rem: emit_rem,
    BinaryOp.Eq: emit_eq,
    BinaryOp.Neq: emit_neq,
    BinaryOp.Lt: emit_lt,
    BinaryOp.Gt: emit_gt,
    BinaryOp.Lte: emit_lte,
    BinaryOp.Gte: emit_gte,
    BinaryOp.And: emit_and,
    BinaryOp.Or: emit_or
}

# Assuming Binary is a class you have that represents a binary expression node
def codegen(node, module, symtab):
    builder = ir.IRBuilder(module.context)
    
    # Note: You will need a codegen function for node.lhs and node.rhs 
    # For now, I will assume such a function exists and takes the same arguments
    lhs_val = codegen(node.lhs, module, symtab)
    rhs_val = codegen(node.rhs, module, symtab)
    
    # Type conversion logic
    if isinstance(lhs_val, ir.Argument) and isinstance(rhs_val, ir.ConstantInt):
        lhs_val = builder.bitcast(lhs_val, rhs_val.type, name="cast_lhs")
    elif isinstance(rhs_val, ir.Argument) and isinstance(lhs_val, ir.ConstantInt):
        rhs_val = builder.bitcast(rhs_val, lhs_val.type, name="cast_rhs")

    if lhs_val.type != rhs_val.type:
        raise CodeGenError("Type mismatch in binary operation")

    emit_func = BINARY_OP_DISPATCH.get(node.op)
    if emit_func:
        return emit_func(builder, lhs_val, rhs_val)
    else:
        raise CodeGenError("Unsupported binary operation")


def codegen_int(node, module, symtab):
    int_type = ir.IntType(32)
    return ir.Constant(int_type, node.value)

def codegen_call(node, module, symtab):
    func_type, func = symtab.lookup(node.callee.text)
    if func_type == SymbolType.Function:
        if not func:
            raise CodeGenError(f"Undefined function: {node.callee.text}")
        
        callee_value = codegen(node.callee, module, symtab)
        if not isinstance(callee_value, ir.Function):
            raise CodeGenError(f"Callee is not a callable entity: {node.callee.text}")
        
        # Argument Code Generation
        arg_values = [codegen(arg, module, symtab) for arg in node.arguments]
        
        builder = ir.IRBuilder(module.context)
        return builder.call(callee_value, arg_values)
    else:
        raise CodeGenError(f"Expected function but found variable or undefined reference: {node.callee.text}")

def codegen_let(let_expr, module, symtab):
    value = codegen(let_expr.value, module, symtab)
    symtab[let_expr.name.text] = value
    return codegen(let_expr.next_expr, module, symtab)

def codegen_function(node, module, symtab):
    int_type = ir.IntType(32)
    param_types = [int_type for _ in node.parameters]
    func_type = ir.FunctionType(int_type, param_types)
    
    # For now, let's assume the function is always named "anonymous_function"
    func = ir.Function(module, func_type, name="anonymous_function")
    
    entry_block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_block)
    
    # Map parameters to their corresponding LLVM values
    for arg, param in zip(func.args, node.parameters):
        arg.name = param.text
        symtab[param.text] = arg

    ret_val = codegen(node.value, module, symtab)
    builder.ret(ret_val)

    # Insert the function into the symbol table
    symtab["anonymous_function"] = func
    return func


def codegen_if(node, module, symtab):
    cond_val = codegen(node.condition, module, symtab)
    func = builder.block.function

    then_bb = func.append_basic_block(name="then")
    else_bb = func.append_basic_block(name="else")
    merge_bb = func.append_basic_block(name="ifcont")

    builder.cbranch(cond_val, then_bb, else_bb)

    builder.position_at_end(then_bb)
    then_val = codegen(node.thenBranch, module, symtab)
    builder.branch(merge_bb)
    then_bb = builder.block

    builder.position_at_end(else_bb)
    else_val = codegen(node.elseBranch, module, symtab)
    builder.branch(merge_bb)
    else_bb = builder.block

    builder.position_at_end(merge_bb)
    int_type = ir.IntType(32)
    phi = builder.phi(int_type, name="iftmp")
    phi.add_incoming(then_val, then_bb)
    phi.add_incoming(else_val, else_bb)

    return phi

def codegen_var(node, module, symtab):
    var_type, value = symtab.lookup(node.text)
    if var_type == SymbolType.Variable:
        if not value:
            raise CodeGenError(f"Undefined variable: {node.text}")
        return value
    elif var_type == SymbolType.Function:
        raise CodeGenError(f"Expected variable but found function: {node.text}")
    else:
        raise CodeGenError(f"Undefined reference: {node.text}")

def declare_printf(module):
    int_type = ir.IntType(32)
    printf_arg_types = [ir.PointerType(ir.IntType(8))]
    printf_type = ir.FunctionType(int_type, printf_arg_types, var_arg=True)
    printf_func = ir.Function(module, printf_type, name="printf")
    return printf_func

def codegen_print(node, module, symtab):
    printf_func = declare_printf(module)
    value = codegen(node.value, module, symtab)

    if isinstance(value.type, ir.IntType) and value.type.width == 32:
        format_str = "%d\n"
    elif isinstance(value.type, ir.PointerType) and isinstance(value.type.pointee, ir.IntType) and value.type.pointee.width == 8:
        format_str = "%s\n"
    else:
        raise CodeGenError("Unsupported type for print operation")

    format_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode("utf8")))
    format_global = ir.GlobalVariable(module, format_const.type, name=".str")
    format_global.linkage = 'private'
    format_global.global_constant = True
    format_global.initializer = format_const

    zero = ir.Constant(ir.IntType(32), 0)
    var_ref = format_global.gep([zero, zero])

    return builder.call(printf_func, [var_ref, value])

def generate_code(ast):
    context = ir.Context()
    module = ir.Module(name="rinha", context=context)
    entry = function.append_basic_block("entry")
    global builder
    builder = ir.IRBuilder(entry)
    symtab = SymbolTable()
    codegen(ast.expression, module, symtab, builder)
    return module

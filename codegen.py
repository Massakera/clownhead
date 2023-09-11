from llvmlite import ir
from llvmlite.ir import values
from typing import Dict, Tuple, Union, Optional
from enum import Enum

from my_ast import Binary, Call, Function, If, Print, Var, Let, Int, BinaryOp

context = ir.Context()
module = ir.Module(name="rinha")
        
class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.parent = parent
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
        elif self.parent:  # If the symbol was not found in the current scope, check the parent scope.
            print(f"searching parent: {self.parent.functions}")
            return self.parent.lookup(name)
        else:
            return ("none", None)

class SymbolType(str, Enum):
    Function = "function"
    Variable = "variable"


class CodeGenError(Exception):
    pass


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
        print(f"lhs type: {lhs.type}, rhs type: {rhs.type}")
        raise CodeGenError("Unsupported type for less-than check")

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

def codegen(node, module, current_symtab, builder):
    if isinstance(node, Let):
        return codegen_let(node, module, current_symtab, builder)
    elif isinstance(node, Binary):
        return codegen_binary(node, module, current_symtab, builder)
    elif isinstance(node, Var):
        return codegen_var(node, module, current_symtab, builder)
    elif isinstance(node, Function):
        return codegen_function(node, module, current_symtab, builder)
    elif isinstance(node, If):
        return codegen_if(node, module, current_symtab, builder)
    elif isinstance(node, Call):
        return codegen_call(node, module, current_symtab, builder)
    elif isinstance(node, Print):
        return codegen_print(node, module, current_symtab, builder)
    elif isinstance(node, Int):
        return codegen_int(node, module, current_symtab)
    else:
        raise CodeGenError(f"Unsupported node type: {type(node)}")

def codegen_binary(node, module, current_symtab, builder):
    print("inside codegen_binary")
    lhs_val = codegen(node.lhs, module, current_symtab, builder)
    rhs_val = codegen(node.rhs, module, current_symtab, builder)

    # Type conversion logic
    if isinstance(lhs_val, ir.Argument) and isinstance(rhs_val, ir.Constant) and isinstance(rhs_val.type, ir.IntType):
        lhs_val = builder.bitcast(lhs_val, rhs_val.type, name="cast_lhs")
    elif isinstance(rhs_val, ir.Argument) and isinstance(lhs_val, ir.Constant) and isinstance(lhs_val.type, ir.IntType):
        rhs_val = builder.bitcast(rhs_val, lhs_val.type, name="cast_rhs")

    if lhs_val.type != rhs_val.type:
        raise CodeGenError(f"Type mismatch in binary operation. lhs: {lhs_val.type}, rhs: {rhs_val.type}")

    emit_func = None
    if node.op in BINARY_OP_DISPATCH.keys():
        emit_func = BINARY_OP_DISPATCH[node.op]
    else:
        raise CodeGenError(f"Unsupported binary operation: {node.op}. Available operations: {BINARY_OP_DISPATCH.keys()}")

    return emit_func(builder, lhs_val, rhs_val)


def codegen_int(node, module, current_symtab):
    print("inside codegen_int")
    int_type = ir.IntType(32)
    return ir.Constant(int_type, node.value)

def codegen_call(node, module, current_symtab, builder):
    print("inside codegen_call")
    func_type, func = current_symtab.lookup(node.callee.text)
    print(f"Looking up {node.callee.text} in symtab:", current_symtab.lookup(node.callee.text))
    if func_type == SymbolType.Function:
        if not func:
            raise CodeGenError(f"Undefined function: {node.callee.text}")
        
        callee_value = func
        if not isinstance(callee_value, ir.Function):
            raise CodeGenError(f"Callee is not a callable entity: {node.callee.text}")
        
        # Argument Code Generation
        arg_values = [codegen(arg, module, builder, current_symtab) for arg in node.arguments]
    
        return builder.call(callee_value, arg_values)
    else:
        print(f"symtab in else {current_symtab.functions}")  # Adjust based on how your symbol table represents data.
        raise CodeGenError(f"Expected function but found variable or undefined reference: {node.callee.text}")

def codegen_let(let_expr, module, current_symtab, builder):
    print("inside codegen_let")
    value = codegen(let_expr.value, module, current_symtab, builder)
    current_symtab.insert_variable(let_expr.name.text, value)   # using insert_variable method
    return codegen(let_expr.next_expr, module, current_symtab, builder)

ANONYMOUS_FUNCTION_COUNT = 0

def codegen_function(node, module, current_symtab, builder):
    global ANONYMOUS_FUNCTION_COUNT

    print("inside codegen_function")
    int_type = ir.IntType(32)
    param_types = [int_type for _ in node.parameters]
    func_type = ir.FunctionType(int_type, param_types)
    function_symtab = SymbolTable(parent=current_symtab)    
    func_name = node.name if node.name else f"anonymous_function_{ANONYMOUS_FUNCTION_COUNT}"

    ANONYMOUS_FUNCTION_COUNT += 1  # increment the counter for next anonymous function

    func = ir.Function(module, func_type, name=func_name)    

    # Insert the function into the current symbol table BEFORE processing the function body.
    current_symtab.insert_function(func_name, func)
    print(f"Inserted function {func_name} into symtab. Current functions: {current_symtab.functions}")

    entry_block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_block)
    
    # Map parameters to their corresponding LLVM values
    for arg, param in zip(func.args, node.parameters):
        arg.name = param.text
        function_symtab.insert_variable(param.text, arg)

    print(function_symtab.variables)
    print(function_symtab.functions)
    print(current_symtab.variables)
    print(current_symtab.functions)

    ret_val = codegen(node.value, module, function_symtab, builder)
    print("ret_val was triggered")
    builder.ret(ret_val)
    print("Current symtab:", function_symtab.functions)

    return func


def codegen_if(node, module, current_symtab, builder):
    print("inside codegen_if")
    cond_val = codegen(node.condition, module, current_symtab, builder)
    func = builder.block.function

    then_bb = func.append_basic_block(name="then")
    else_bb = func.append_basic_block(name="else")
    merge_bb = func.append_basic_block(name="ifcont")

    builder.cbranch(cond_val, then_bb, else_bb)

    builder.position_at_end(then_bb)
    then_val = codegen(node.then, module, current_symtab, builder)
    builder.branch(merge_bb)
    then_bb = builder.block

    builder.position_at_end(else_bb)
    else_val = codegen(node.otherwise, module, current_symtab, builder)
    builder.branch(merge_bb)
    else_bb = builder.block

    builder.position_at_end(merge_bb)
    int_type = ir.IntType(32)
    phi = builder.phi(int_type, name="iftmp")
    phi.add_incoming(then_val, then_bb)
    phi.add_incoming(else_val, else_bb)

    return phi

def codegen_var(node, module, current_symtab, builder):
    print("inside codegen_var")
    var_type, value = current_symtab.lookup(node.text)
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

def codegen_print(node, module, current_symtab, builder):
    print("inside codegen_print")
    printf_func = declare_printf(module)
    value = codegen(node.value, module, builder, current_symtab)

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
    current_symtab = SymbolTable()
    
    # Create the main function or the starting point of your code
    # Assuming a function type of void() for simplicity
    func_type = ir.FunctionType(ir.VoidType(), [])
    main_func = ir.Function(module, func_type, name="main")
    entry_block = main_func.append_basic_block(name="entry")
    
    # Position the builder at the entry block
    builder = ir.IRBuilder(entry_block)
    
    # Now, pass the builder to your codegen function
    codegen(ast.expression, module, current_symtab, builder)
    
    return module

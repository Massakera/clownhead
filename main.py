import json
from my_ast import File, Loc, Parameter, Function, If, Print, Let, Binary, Var, Call, Int, BinaryOp
from codegen import generate_code
from typing import Dict, Any

def parse_ast_from_json(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        return json.load(f)

def convert_operator(op_str: str) -> BinaryOp:
    op_mapping = {
        "Add": BinaryOp.Add,
        "Sub": BinaryOp.Sub,
        "Mul": BinaryOp.Mul,
        "Div": BinaryOp.Div,
        "Rem": BinaryOp.Rem,
        "Eq":  BinaryOp.Eq,
        "Neq": BinaryOp.Neq,
        "Lt":  BinaryOp.Lt,
        "Gt":  BinaryOp.Gt,
        "Lte": BinaryOp.Lte,
        "Gte": BinaryOp.Gte,
        "And": BinaryOp.And,
        "Or":  BinaryOp.Or
    }

    if op_str not in op_mapping:
        raise ValueError(f"Unknown operator: {op_str}")
    
    return op_mapping[op_str]

def convert_expression(data: Dict[str, Any]) -> Any:
    kind = data["kind"]
    location = convert_location(data["location"])

    if kind == "Let":
        name_text = data["name"]["text"]
        name = Parameter(name_text, convert_location(data["name"]["location"]))
        value_data = data["value"]
        if value_data["kind"] == "Function":
            parameters = [Parameter(param["text"], convert_location(param["location"])) for param in value_data["parameters"]]
            value_expr = convert_expression(value_data["value"])
            value = Function(parameters, value_expr, location, name=name_text)
        else:
            value = convert_expression(value_data)
        next_expr = convert_expression(data["next"])
        return Let(name, value, next_expr, location)

    elif kind == "Function":
        # Since we handle named functions in the Let node, this block will now only deal with anonymous functions
        parameters = [Parameter(param["text"], convert_location(param["location"])) for param in data["parameters"]]
        value = convert_expression(data["value"])
        return Function(parameters, value, location, None)

    elif kind == "If":
        condition = convert_expression(data["condition"])
        then_expr = convert_expression(data["then"])
        otherwise_expr = convert_expression(data["otherwise"])
        return If(condition, then_expr, otherwise_expr, location)

    elif kind == "Binary":
        lhs = convert_expression(data["lhs"])
        rhs = convert_expression(data["rhs"])
        op = convert_operator(data["op"])
        return Binary(lhs, rhs, op, location)

    elif kind == "Call":
        callee = convert_expression(data["callee"])
        arguments = [convert_expression(arg) for arg in data["arguments"]]
        return Call(callee, arguments, location)

    elif kind == "Var":
        return Var(data["text"], location)


    elif kind == "Int":
        return Int(data["value"], location)

    elif kind == "Print":
        value = convert_expression(data["value"])
        return Print(value, location)

    else:
        raise ValueError(f"Unknown node type: {kind}")

def convert_location(data: Dict[str, Any]) -> Loc:
    return Loc(data["start"], data["end"], data["filename"])

def dict_to_ast(data: Dict[str, Any]) -> File:
    expression = convert_expression(data["expression"])
    
    # Assuming the location data is at the top level of the JSON data:
    location = convert_location(data["location"])

    # Extract the filename from the location data or use a placeholder
    filename = location.filename if location and hasattr(location, "filename") else "unknown_file"

    return File(filename, expression, location)

def main():
    try:
        data = parse_ast_from_json("example.json")
        ast = dict_to_ast(data)
        print(f"this is the ast: {ast}")
        mod = generate_code(ast)

        # Print the generated code
        print(mod)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()  # Print the stack trace for more information

if __name__ == "__main__":
    main()
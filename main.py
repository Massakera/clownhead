import json
from my_ast import File, Loc, Parameter, Function, If, Print, Let, Binary, Var, Call, Int
from codegen import generate_code
from typing import Dict, Any

def parse_ast_from_json(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        return json.load(f)

def convert_operator(op_str: str) -> str:
    op_mapping = {
        "Add": "Add",
        "Sub": "Sub",
        "Mul": "Mul",
        "Div": "Div",
        "Rem": "Rem",
        "Eq":  "Eq",
        "Neq": "Neq",
        "Lt":  "Lt",
        "Gt":  "Gt",
        "Lte": "Lte",
        "Gte": "Gte",
        "And": "And",
        "Or":  "Or"
    }

    return op_mapping.get(op_str, None)

def convert_expression(data: Dict[str, Any]) -> Any:
    kind = data["kind"]
    location = convert_location(data["location"])

    if kind == "Let":
        name = Parameter(data["name"]["text"], convert_location(data["name"]["location"]))
        value = convert_expression(data["value"])
        next_expr = convert_expression(data["next"])
        return Let(name, value, next_expr, location)

    elif kind == "Function":
        parameters = [Parameter(param["text"], convert_location(param["location"])) for param in data["parameters"]]
        value = convert_expression(data["value"])
        return Function(parameters, value, location)

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
        return Int(data["value"].get<int>(), location)

    elif kind == "Print":
        value = convert_expression(data["value"])
        return Print(value, location)

    else:
        raise ValueError(f"Unknown node type: {kind}")

def convert_location(data: Dict[str, Any]) -> Loc:
    return Loc(data["start"], data["end"], data["filename"])

def dict_to_ast(data: Dict[str, Any]) -> File:
    expression = convert_expression(data["expression"])
    return File(expression)


def main():
    try:
        data = parse_ast_from_json("example.json")
        ast = dict_to_ast(data)  # Assuming you have this function, as it wasn't provided in the code

        mod = generate_code(ast)

        # Print the generated code
        print(mod)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

# clownhead
## Only god knows what is inside the clown head

This project demonstrates a process of converting a high-level representation of a program, for ex the Fibonacci sequence calculation, into LLVM Intermediate Representation (IR), then compiling and executing the generated assembly.

This is specially made for [Rinha de Compiladores](https://github.com/aripiprazole/rinha-de-compiler).

## Contents
- ``main.py``: The main driver script that parses an abstract syntax tree (AST) from a JSON file, then converts this AST into a high-level IR and eventually into LLVM IR.
- ``my_ast.py``: Defines the data structures and classes for the abstract syntax tree representation.
- ``codegen.py``: Contains the code generation logic that translates our high-level IR to LLVM IR.

## Workflow example

- The ``main.py`` script reads the example.json to get a JSON representation of the AST.
- The script then converts this JSON AST into our high-level IR using the structures defined in ``my_ast.py``.
- This high-level IR is then converted to LLVM IR using the ``codegen.py`` module.
- External LLVM tools (llvm-as, llc) and the Clang compiler are used to compile the LLVM IR into an executable.
- Running the fib executable calculates the 10th Fibonacci number, resulting in 55.

## How to run? 

1. Build the Docker Image
```bash
docker build -t clownhead .
```
2. To compile the JSON-based AST and generate an executable, place your input file at /var/rinha/source.rinha.json in your project directory. Then, run the following command:
```bash
docker run -v <local_path_to_project_directory>:/app clownhead
```
Replace <local_path_to_project_directory> with the path to your project directory on your local machine. For example, if your project is located in ~/Proj/clownhead, you would run:

```bash
docker run -v ~/Proj/clownhead:/app clownhead
```

3. After running the above command, an LLVM-IR file with the .ll extension and an executable will be generated in your project directory.

For the example above, you would get **comb.ll** and **comb** (the executable).

4. To run the generated executable:

```bash
./<output_name>
```



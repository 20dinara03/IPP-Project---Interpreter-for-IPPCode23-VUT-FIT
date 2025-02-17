# **IPP Project - Interpreter for IPPCode23**

### **Author**
**Name:** Dinara Garipova  
**Login:** xgarip00  

## **Project Overview**
This project implements an **interpreter** for **IPPCode23**, a language represented in XML format. The interpreter reads and executes the instructions provided in an XML source file, while also supporting input handling and extended statistics.

## **Script Structure**
The program consists of four main classes:
1. **`Args`** - Handles input arguments and program execution parameters.
2. **`ProgramXMLReader`** - Parses and validates the XML file.
3. **`Instructions`** - Processes and categorizes instructions.
4. **`Interpret`** - The main execution engine that interprets the instructions.

## **Execution**
To run the interpreter, use the following command:

```bash
python3 interpret.py --source=source.xml --input=input.txt
```
where:
- source.xml is the input file containing the XML representation of the code.
- input.txt is an optional input file for program execution.

## Command-Line Arguments
The script supports the following options:

- --help → Displays usage information.
- --source=file → Specifies the XML source file.
- --input=file → Specifies the input file.
- --stats=file → Enables statistical tracking and outputs results.

## Program Workflow
### 1. Argument Parsing:

- The Args class processes command-line arguments and checks for errors.
- Ensures that either --source or --input (or both) are provided.
  
### 2. XML Processing:

- The ProgramXMLReader class loads and verifies the structure of the XML file.
- Ensures proper instruction ordering and valid attributes.

### 3. Instruction Processing:

- The Instructions class extracts operations from XML and prepares them for execution.
- Categorizes instructions and creates a dictionary-based instruction set.

### 4. Interpretation:

- The Interpret class executes instructions sequentially.
- Implements a stack-based approach for variables and memory management.
- Handles various operations like arithmetic, comparisons, jumps, and I/O.

## Error Handling
The script detects:

- Invalid XML format (error code 31)
- Incorrect syntax or missing attributes (error code 32)
- Invalid instruction ordering or duplicate labels (error code 52)
- Undefined variables or memory issues (error code 54)
- Invalid type operations (error code 53)
- Division by zero or out-of-bounds memory access (error code 57, 58)
  
##Project Structure
```bash
.
├── tests/                # Test cases for the interpreter
├── interpret.py          # Main Python interpreter
├── readme2.pdf           # Implementation documentation
├── rozsireni             # Additional features or extensions
```
## Example XML Code
A sample IPPCode23 program in XML format:
```xml
<program language="IPPcode23">
    <instruction order="1" opcode="DEFVAR">
        <arg1 type="var">GF@var1</arg1>
    </instruction>
    <instruction order="2" opcode="MOVE">
        <arg1 type="var">GF@var1</arg1>
        <arg2 type="int">10</arg2>
    </instruction>
    <instruction order="3" opcode="WRITE">
        <arg1 type="var">GF@var1</arg1>
    </instruction>
</program>
```
##License
This project was developed as part of the IPP 2022/2023 course and is intended for educational use.


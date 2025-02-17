import sys
import xml.etree.ElementTree as ET
import os
import re
class Args:
    def __init__(self):
        # Initialize all arguments to None or False
        self.soursefile = None
        self.inputfile = None
        self.statsOutputFile = None
        self.insts = False
        self.vars = False
        self.hot = False
        self.frequent = False
        self.printString = None
        self.eol = False
        self.sourceBool = False
        self.inputBool = False
        self.anyStats = False
    # Method to execute program parameters
    def execute_program_params(self):
        # Call helper methods to parse, check, and validate program arguments
        self.ParseProgramsArgumets()
        self.CheckProgramArguments()
        self.CheckProgramsArgumentsPath()
    # Method to parse program arguments from the command line
    def ParseProgramsArgumets(self):
        # Split arguments with "=" and concatenate them into a list of arguments
        new_args = []
        for arg in sys.argv:
            parts = arg.split('=')
            if len(parts) > 1:
                new_args.extend([parts[0], '=', parts[1]])
            else:
                new_args.append(arg)
         # Replace sys.argv with the new list of arguments
        sys.argv = new_args
        # If "--help" argument is present, print out help and exit
        if "--help" in sys.argv:
            if len(sys.argv) != 2:
                exit(10)
            self.printHelp()
        # Otherwise, check for other program arguments
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "--source" and i+2 < len(sys.argv) and self.soursefile == None:
                self.soursefile = sys.argv[i+2]
                self.sourceBool = True
            elif sys.argv[i] == "--input" and i+2 < len(sys.argv) and self.inputfile == None:
                self.inputfile = sys.argv[i+2]
                self.inputBool = True
            elif sys.argv[i] == "--stats" and i+2 < len(sys.argv) and sys.argv[0] != sys.argv[i+2]:
                self.statsOutputFile = sys.argv[i+2]
    # Method to check program arguments for correctness
    def CheckProgramArguments(self):
        # If both sourcefile and inputfile are None, exit program
        if (self.soursefile is None) and (self.inputfile is None):
            exit(10)
         # If only sourcefile is given, set inputfile to sys.stdin
        elif self.soursefile != None and self.inputfile == None:
            self.sourceBool = True
            self.inputfile = sys.stdin
         # If only inputfile is given, set sourcefile to sys.stdin
        elif self.soursefile == None and self.inputfile != None:
            self.inputfile = open(self.inputfile, "r")
            self.inputBool = True
            self.soursefile = sys.stdin
        # If both sourcefile and inputfile are given, open inputfile for reading and set sourceBool and inputBool to True
        elif self.soursefile != None and self.inputfile != None:
            self.inputfile = open(self.inputfile, "r")
            self.sourceBool, self.inputBool = True, True
    # Method to check if given paths for sourcefile and inputfile are valid
    def CheckProgramsArgumentsPath(self):
        # If sourcefile path is invalid, exit program
        if self.sourceBool and not os.path.exists(self.soursefile):
            exit(11)
        # Check if inputfile path is invalid, exit program
        if self.inputBool and not os.path.exists(self.inputfile.name):
            exit(11)
    def printHelp(self):
        # Print information about the script and its usage
        print("\nThe script interprets XML representations of programs,")
        print("executes them according to command line parameters, and generates output.\n")
        print("Usage:")
        print(" --help print out basic info about this script\n")
        print(" --source=file specify input file with XML representation of source code\n")
        print(" --input=file specify input file for interpretation of source code\n")
        exit(0)
class ProgramXMLReader:
    def __init__(self, sourcefile):
        # Initialize instance variables
        self._root = None
        self._tree = None
        self._instruction_order = 0
         # If sourcefile is provided, parse the file. Otherwise, parse standard input
        if sourcefile:
            self._parse_file(sourcefile)
        else:
            self._parse_stdin()
    def _parse_file(self, sourcefile):
        # Parse XML file
        try:
            self._tree = ET.parse(sourcefile)
        except ET.ParseError:
            # If there's a parsing error, exit with code 31
            exit(31)
        # Get root element of the XML tree
        self._root = self._tree.getroot()
    def _parse_stdin(self):
        # Parse XML from standard input
        try:
            tree = input()
            self._root = ET.fromstring(tree)
        except:
            # If there's an error, exit with code 31
            exit(31)
    def execute_program(self):
        # Check the structure of the XML tree and order the instructions
        self._check_structure_of_xml_tree()
        self._order_instructions()
    def _check_structure_of_xml_tree(self):
        # Check the structure of the XML tree
        for ins in self._root:
            if ins.tag != 'instruction':
                exit(32)
            if not ins.attrib.get('opcode') or not ins.attrib.get('order'):
                exit(32)
            for arg in ins:
                if arg.tag not in ['arg1', 'arg2', 'arg3'] or not arg.attrib.get('type'):
                    exit(32)
        if self._root.tag != 'program' or self._root.attrib.get('language').upper() != 'IPPCODE23':
            exit(32)
        for atrb in self._root.attrib:
            if(atrb not in ["name", "description"]):
                exit(32)
    def _order_instructions(self):
        # Order the instructions based on their order attribute
        try:
            instructions = self._root.findall('instruction')
            instructions.sort(key=lambda instruction: int(instruction.get('order')))
            for instruction in instructions:
                if self._check_instruction_order(instruction.get('order')):
                    if instruction.get('order') in self._instruction_order:
                        exit(32)
                    self._instruction_order = int(instruction.get('order').upper())
            if len(instructions) != len(set(instructions)):
                exit(32)
        except:
            exit(32)
    def _check_instruction_order(self, external_order):
        # Check that the order of the instruction is valid
        if external_order is None:
            exit(32)
        try:
            control_var = int(external_order)
        except ValueError:
            exit(32)
        return self._instruction_order < control_var
class Instructions:
    def __init__(self, xmlinstr):
        self.xmlinst = xmlinstr # initializes the xmlinstr attribute
        self.opcode = None
        self.instr = None
        self.instr_dict = {}
        self.label_dict = {}
        self.order_dict = {}
        for instr in xmlinstr:
             # extracts the opcode and order number of each instruction from xmlinstr
            self.opcode = instr.attrib["opcode"].upper()
            self.order = instr.attrib["opcode"]
            order = int(instr.attrib["order"])
            # checks if the order number is greater than zero, if not, exits with code 32
            if int(order) <=  0 :
                exit(32)
            # checks if the opcode is valid, if not, exits with code 32
            if self.opcode not in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "NOTS", "INT2CHARS", "STRI2INTS","DEFVAR", "POPS","CALL", "LABEL", "JUMP", "JUMPIFEQS", "JUMPIFNEQS", "PUSHS", "WRITE", "EXIT", "DPRINT","MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE", "READ","ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"]:
                exit(32)
            # adds the instruction to instr_dict attribute with order number as key
            self.instr_dict[str(order)] = {
                "opcode": self.opcode,
                "args": [arg.text for arg in instr],
                "type": [arg.attrib['type'] for arg in instr]
            }
            self.args = [arg.text for arg in instr]
            self.types = [arg.attrib['type'] for arg in instr]
            # if the opcode is LABEL, adds the label to label_dict attribute with label name as key and order number minus 1 as value
            if self.opcode == "LABEL":
                if self.args[0] in self.label_dict:
                    exit(52)
                else:
                    self.label_dict[self.args[0]] = int(order) - 1
            self.check_num_of_args()
            self.check_instr_args()
    # checks if the number of arguments for the instruction is valid
    def check_num_of_args(self):
        if self.opcode in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK", "CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "NOTS", "INT2CHARS", "STRI2INTS"] and len(self.args) != 0:
            exit(32)
        elif self.opcode in ["DEFVAR", "POPS","CALL", "LABEL", "JUMP", "JUMPIFEQS", "JUMPIFNEQS", "PUSHS", "WRITE", "EXIT", "DPRINT"] and len(self.args) != 1:
            exit(32)
        elif self.opcode in ["MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE", "READ"] and len(self.args) != 2:
            exit(32)
        elif self.opcode in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"] and len(self.args) != 3:
            exit(32)
     # checks if the type of arguments for the instruction is valid
    def check_instr_args(self):
        if self.opcode in ["DEFVAR", "POPS"] and self.types[0] != "var":
                exit(53)
        elif self.opcode in ["CALL", "LABEL", "JUMP", "JUMPIFEQS", "JUMPIFNEQS"] and self.types[0] != "label":
                exit(53)
        elif self.opcode in ["PUSHS", "WRITE", "EXIT", "DPRINT"]:
            if self.types[0] != "string" and self.types[0] != "bool" and self.types[0] != "nil" and self.types[0] != "int" and self.types[0] != "var":
                exit(53)
        elif self.opcode in ["MOVE", "NOT", "INT2CHAR", "STRLEN", "TYPE"]:
            if self.types[0] != "var" and self.types[1] not in ["string", "bool", "nil", "int", "var"]:
                exit(53)
        elif self.opcode == "READ":
            if self.types[0] != "var" and self.types[1] != "type":
                exit(53)
        elif self.opcode in ["ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR"]:
            if self.types[0] != "var" and self.types[1] not in ["string", "bool", "nil", "int", "var"] and self.types[2] not in ["string", "bool", "nil", "int", "var"]:
                exit(53)
        elif self.opcode in ["JUMPIFEQ", "JUMPIFNEQ"]:
            if self.types[0] != "label" and self.types[1] not in ["string", "bool", "nil", "int", "var"] and self.types[2] not in ["string", "bool", "nil", "int", "var"]:
                exit(53)
class Interpret:
    def __init__(self, instr_dict, label_dict,inputfile):
        # Initialize dictionaries for the frames and check if the local and temp frames exist
        self.global_frame = {}
        self.local_frame = {}
        self.temp_frame = {}
        self.lf_exists = False
        self.tf_exists = False
        # Initialize the call stack and the main stack
        self.call_stack = []
        self.stack = []
        # Assign values to the instruction dictionary, label dictionary, and input file
        self.instr_dict = instr_dict
        self.label_dict = label_dict
        self.input_file = inputfile
        # Call the "interpret" method to execute instructions
        self.interpret()
        # Initialize the opcode and scope values to None and 0 respectively
        self.opcode = None
        self.scope = 0
    
    # A method to convert HTML entities and Unicode characters to their corresponding symbols.
    def rewrite_string(self,args):
        # Convert HTML entities to symbols
        args = re.sub('&lt;', '<', args)
        args = re.sub('&gt;', '>', args)
        args = re.sub('&amp;', '&', args)
        args = re.sub('&quot;', '"', args)
        args = re.sub('&apos;', '\'', args)
        # Convert Unicode characters to symbols
        pattern = r'\\\d{3}'
        match = re.search(pattern, args)
        input_to_read = args
        while match:
            num = int(match.group()[1:])
            char = chr(num)
            input_to_read = re.sub(pattern, char, input_to_read, count=1)
            match = re.search(pattern, input_to_read)
        # Return the converted string
        return input_to_read
            

    def getfromvar(self, args, type, i,typ,value):
        # Split the variable name to get the frame name and variable name
        name = args[i].split('@')
        # If the frame is global frame (GF)
        if name[0] == "GF":
            # Check if variable exists in global frame
            if name[1] not in self.global_frame:
                exit(54)
            else:
                # Save current variable value and type to value and typ lists
                value[i] = args[i]
                typ[i] = type[i]
                 # Get the type and value of the variable from global frame
                type[i] = self.global_frame[name[1]][0]
                args[i] = self.global_frame[name[1]][1]
        # If the frame is local frame (LF)
        if name[0] == "LF":
            # Check if local frame exists
            if not self.lf_exists:
                exit(55)
            elif self.scope in self.local_frame:
                if name[1] not in self.local_frame[self.scope]:
                    exit(54)
            else:
                exit(54)
            value[i] = args[i]
            typ[i] = type[i]
            type[i] = self.local_frame[self.scope][name[1]][0]
            args[i] = self.local_frame[self.scope][name[1]][1]
         # If the frame is temporary frame (TF)
        if name[0] == "TF":
            if not self.tf_exists:
                exit(55)
            elif name[1] not in self.temp_frame:
                exit(54)
            else:
                value[i] = args[i]
                typ[i] = type[i]
                type[i] = self.temp_frame[name[1]][0]
                args[i] = self.temp_frame[name[1]][1]
        # Return updated typ and value lists
        return typ,value

    def interpret(self):
        # initialize the scope and count
        self.scope = None
        count = 1
        # iterate through each instruction
        while  (count < len(self.instr_dict) + 1):
            # retrieve the opcode, arguments, and type of the current instruction
            self.opcode = self.instr_dict[str(count)]["opcode"]
            args = self.instr_dict[str(count)]["args"]
            type = self.instr_dict[str(count)]["type"]
            #CREATEFRAME
            if self.opcode == "CREATEFRAME":
                self.tf_exists = True
                self.temp_frame = {}
            #PUSHFRAME
            elif self.opcode == "PUSHFRAME":
                if not self.tf_exists:
                    exit(55)
                self.lf_exists = True
                if self.scope == None:
                    self.scope = 0
                self.scope +=1
                self.local_frame[self.scope] = {}
                self.local_frame[self.scope].update(self.temp_frame)
                self.temp_frame = {}
                self.tf_exists = False
            #POPFRAME
            elif self.opcode == "POPFRAME":
                if not self.lf_exists:
                    exit(55)
                if len(self.local_frame[self.scope]) != 0:
                    key, value = self.local_frame[self.scope].popitem()
                    self.local_frame.popitem()
                    self.scope -=1
                    self.temp_frame = {key: value}
                    self.tf_exists = True
                else:
                    exit(56)
                if not self.local_frame:
                    self.lf_exists = False
            #RETURN
            elif self.opcode == "RETURN":
                if len(self.call_stack) == 0:
                    exit(56)
                count = self.call_stack[-1]
                self.call_stack = self.call_stack[:-1]
            elif self.opcode == "BREAK":
                print('The position in the code : {}'.format(self.opcode))
                print('Global frame : {}'.format(self.global_frame))
                print('Local frame : {}'.format(self.local_frame[self.scope]))
                print('Temporary frame : {}'.format(self.temp_frame))
                print('The number of instructions being executed:{}'.format(count+1))
            elif self.opcode == "CLEARS":
                self.stack = []
            #ADDS
            elif self.opcode == "ADDS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] != "int":
                    exit(53)
                self.stack.append(["int",int(value1[1])+int(value2[1])])
            #SUBS
            elif self.opcode == "SUBS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] != "int":
                    exit(53)
                self.stack.append(["int",int(value1[1])-int(value2[1])])
            #MULS
            elif self.opcode == "MULS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] != "int":
                    exit(53)
                self.stack.append(["int",int(value1[1])*int(value2[1])])
            #IDIVS
            elif self.opcode == "IDIVS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] != "int":
                    exit(53)
                if int(value2[1]) == 0:
                    exit(57)
                self.stack.append(["int",int(value1[1])//int(value2[1])])
            #LTS
            elif self.opcode == "LTS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] == "nil" or value1[0] == "var":
                    exit(53)
                self.stack.append([value1[1]<value2[1]])
            #GTS
            elif self.opcode == "GTS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] == "nil" or value1[0] == "var":
                    exit(53)
                self.stack.append([value1[1]>value2[1]])
            #EQS
            elif self.opcode == "EQS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value1[0] != value2[0] or value1[0] == "var":
                    if value1[0] != "nil" and value2[0] != "nil":
                        exit(53)
                self.stack.append([value1[1] == value2[1]])
            #ANDS
            elif self.opcode == "ANDS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value2[0] != value1[0] or value1[0] != "bool":
                    exit(53)
                else:
                    if value1[1] == "true" and value2[1] == "true":
                        self.stack.append(["bool","true"])
                    else:
                        self.stack.append(["bool","false"])
            #ORS
            elif self.opcode == "ORS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value2[0] != value1[0] or value1[0] != "bool":
                    exit(53)
                else:
                    if value1[1] == "false" and value2[1] == "false":
                        self.stack.append(["bool","false"])
                    else:
                        self.stack.append(["bool","true"])
            #NOTS
            elif self.opcode == "NOTS":
                if len(self.stack) < 1:
                    exit(56)
                value = self.stack.pop()
                if value[0] != "bool":
                    exit(53)
                else:
                    if value[1] == "true":
                        self.stack.append(["bool","false"])
                    else:
                        self.stack.append(["bool","true"])
            #INT2CHARS
            elif self.opcode == "INT2CHARS":
                if len(self.stack) < 1:
                    exit(56)
                value = self.stack.pop()
                if value[0] != "int":
                    exit(53)
                try:
                    value[1] = chr(int(value[1]))
                except ValueError:
                    exit(58)
                self.stack.append(["string",value[1]])
            #STRI2INTS
            elif self.opcode == "STRI2INTS":
                if len(self.stack) < 2:
                    exit(56)
                value2 = self.stack.pop()
                value1 = self.stack.pop()
                if value2[0] != "int" or value1[0] != "string":
                    exit(53)
                try:
                    index = int(value2[1])
                except ValueError:
                    exit(53)
                if index >= len(value1[1]) or index < 0:
                    exit(58)
                char = value1[1][index]
                self.stack.append(["int",ord(char)])
            elif self.opcode == "DEFVAR":
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] in self.global_frame:
                        exit(52)
                    else:
                        self.global_frame[name[1]] = [None,None]
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    if name[1] in self.temp_frame:
                        exit(52)
                    else:
                        self.temp_frame[name[1]] = [None, None]
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope != None:
                        if self.scope in self.local_frame:
                            if name[1] in self.local_frame[self.scope]:
                                exit(52)
                    else:
                        self.scope = 0
                    self.local_frame[self.scope] = {}
                    self.local_frame[self.scope][name[1]] = [None, None]
            #POPS
            elif self.opcode == "POPS":
                if not bool(self.stack):
                    exit(56)
                else:
                    name = args[0].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        value = self.stack.pop()
                        self.global_frame[name[1]] = [value[0], value[1]]
                    elif name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        if name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            value = self.stack.pop()
                            self.temp_frame[name[1]] = [value[0], value[1]]
                    elif name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        scope = len(self.local_frame[self.scope]) - 1
                        value = self.stack.pop()
                        self.local_frame[self.scope][scope][name[1]] = [value[0], value[1]]
            #PUSHS
            elif self.opcode == "PUSHS":
                # symb = args[0]
                if args[0] == None or type[0] == None:
                    exit(56)
                if type[0] == "var":
                    name = args[0].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            l_type = self.global_frame[name[1]][0]
                            l_value = self.global_frame[name[1]][1]
                            if l_type == None or l_value == None:
                                exit(56)
                            self.stack.append([l_type, l_value])
                    elif name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        if name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            l_type = self.temp_frame[name[1]][0]
                            l_value = self.temp_frame[name[1]][1]
                            if l_type == None or l_value == None:
                                exit(56)
                            self.stack.append([l_type, l_value])
                    elif name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        l_type = self.local_frame[self.scope][name[1]][0]
                        l_value = self.local_frame[self.scope][name[1]][1]
                        if l_type == None or l_value == None:
                            exit(56)
                        self.stack.append([l_type, l_value])
                else:
                    self.stack.append([type[0],args[0]])
            #MOVE
            elif self.opcode == "MOVE":
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    if type[1] == "string":
                        args[1] = ""
                    else:
                        exit(56)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    elif type[1] == "var":
                        symb = args[1].split('@')
                        if symb[0] == "GF":
                            if symb[1] not in self.global_frame:
                                exit(54)
                            else:
                                if self.global_frame[symb[1]][1] == None:
                                    if self.global_frame[symb[1]][0] == "string":
                                        self.global_frame[symb[1]][1] = ""
                                    else:
                                        exit(56)
                                self.global_frame[name[1]][0] = self.global_frame[symb[1]][0]
                                self.global_frame[name[1]][1] = self.global_frame[symb[1]][1]
                        elif symb[0] == "TF":
                            if not self.tf_exists:
                                exit(55)
                            elif symb[1] not in self.temp_frame:
                                exit(54)
                            else:
                                if self.temp_frame[symb[1]][1] == None:
                                    if self.temp_frame[symb[1]][0] == "string":
                                        self.temp_frame[symb[1]][1] = ""
                                    else:
                                        exit(56)
                                self.global_frame[name[1]][0] = self.temp_frame[symb[1]][0]
                                self.global_frame[name[1]][1] = self.temp_frame[symb[1]][1]
                        elif symb[0] == "LF":
                            if not self.lf_exists:
                                exit(55)
                            if self.scope in self.local_frame:
                                if symb[1] not in self.local_frame[self.scope]:
                                    exit(54)
                            else:
                                    exit(54)
                            if self.local_frame[self.scope][symb[1]][1] == None:
                                if self.local_frame[self.scope][symb[1]][0] == "string":
                                    self.local_frame[self.scope][symb[1]][1] = ""
                                else:
                                    exit(56)
                            self.global_frame[name[1]][0] = self.local_frame[self.scope][symb[1]][0]
                            self.global_frame[name[1]][1] = self.local_frame[self.scope][symb[1]][1]
                    else:
                        self.global_frame[name[1]][0] = type[1]
                        self.global_frame[name[1]][1] = args[1]
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    if type[1] == "var":
                        symb = args[1].split('@')
                        if symb[0] == "GF":
                            if symb[1] not in self.global_frame:
                                exit(54)
                            else:
                                self.local_frame[self.scope][name[1]][0] = self.global_frame[symb[1]][0]
                                self.local_frame[self.scope][name[1]][1] = self.global_frame[symb[1]][1]
                        elif symb[0] == "TF":
                            if not self.tf_exists:
                                exit(55)
                            elif symb[1] not in self.temp_frame:
                                exit(54)
                            else:
                                self.local_frame[self.scope][name[1]][0] = self.temp_frame[symb[1]][0]
                                self.local_frame[self.scope][name[1]][1] = self.temp_frame[symb[1]][1]
                        elif symb[0] == "LF":
                            if not self.lf_exists:
                                exit(55)
                            elif symb[1] not in self.local_frame[self.scope]:
                                exit(54)
                            else:
                                self.local_frame[self.scope][name[1]][0] = self.local_frame[self.scope][symb[1]][0]
                                self.local_frame[self.scope][name[1]][1] = self.local_frame[self.scope][symb[1]][1]
                    else:
                        self.local_frame[self.scope][name[1]][0] = type[1]
                        self.local_frame[self.scope][name[1]][1] = args[1]
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    elif type[1] == "var":
                        symb = args[1].split('@')
                        if symb[0] == "GF":
                            if symb[1] not in self.global_frame:
                                exit(54)
                            else:
                                self.temp_frame[name[1]][0] = self.global_frame[symb[1]][0]
                                self.temp_frame[name[1]][1] = self.global_frame[symb[1]][1]
                        elif symb[0] == "TF":
                            if not self.tf_exists:
                                exit(55)
                            elif symb[1] not in self.temp_frame:
                                exit(54)
                            else:
                                self.temp_frame[name[1]][0] = self.temp_frame[symb[1]][0]
                                self.temp_frame[name[1]][1] = self.temp_frame[symb[1]][1]
                        elif symb[0] == "LF":
                            if not self.lf_exists:
                                exit(55)
                            elif symb[1] not in self.local_frame[self.scope]:
                                exit(54)
                            else:
                                self.temp_frame[name[1]][0] = self.local_frame[self.scope][symb[1]][0]
                                self.temp_frame[name[1]][1] = self.local_frame[self.scope][symb[1]][1]
                    else:
                        self.temp_frame[name[1]][0] = type[1]
                        self.temp_frame[name[1]][1] = args[1]
            #CALL
            elif self.opcode == "CALL":
                if args[0] not in self.label_dict:
                    exit(52)
                else:
                    self.call_stack.append(count)
                    count = int(self.label_dict[args[0]])
            #ADD
            elif self.opcode == "ADD":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "int":
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "int"
                        self.global_frame[name[1]][1] = int(args[1]) + int(args[2])
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "int"
                    self.local_frame[self.scope][name[1]][1] = int(args[1]) + int(args[2])
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "int"
                        self.temp_frame[name[1]][1] = int(args[1]) + int(args[2])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #SUB
            elif self.opcode == "SUB":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "int":
                    if type[1] == None or type[2] == None:
                        exit(56)
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "int"
                        self.global_frame[name[1]][1] = int(args[1]) - int(args[2])
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "int"
                    self.local_frame[self.scope][name[1]][1] = int(args[1]) - int(args[2])
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "int"
                        self.temp_frame[name[1]][1] = int(args[1]) - int(args[2])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #MUL
            elif self.opcode == "MUL":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "int":
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "int"
                        self.global_frame[name[1]][1] = int(args[1]) * int(args[2])
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "int"
                    self.local_frame[self.scope][name[1]][1] = int(args[1]) * int(args[2])
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "int"
                        self.temp_frame[name[1]][1] = int(args[1]) * int(args[2])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #IDIV
            elif self.opcode == "IDIV":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "int":
                    exit(53)
                if int(args[2]) == 0:
                    exit(57)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "int"
                        self.global_frame[name[1]][1] = int(args[1]) // int(args[2])
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "int"
                    self.local_frame[self.scope][name[1]][1] = int(args[1]) // int(args[2])
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "int"
                        self.temp_frame[name[1]][1] = int(args[1]) // int(args[2])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #LT
            elif self.opcode == "LT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if type[1] != type[2] or type[1] == "nil" or type[2] == "var":
                    exit(53)
                if type[1] == "string":
                    args[1] = self.rewrite_string(args[1])
                    args[2] = self.rewrite_string(args[2])
                if type[1] == "int":
                    args[1] = int(args[1])
                    args[2] = int(args[2])
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        self.global_frame[name[1]][1] = str(args[1] < args[2]).lower()
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    self.local_frame[self.scope][name[1]][1] = str(args[1] < args[2]).lower()
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        self.temp_frame[name[1]][1] = str(args[1] < args[2]).lower()
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #GT
            elif self.opcode == "GT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if type[1] != type[2] or type[1] == "nil" or type[2] == "var":
                    exit(53)
                if type[1] == "string":
                    args[1] = self.rewrite_string(args[1])
                    args[2] = self.rewrite_string(args[2])
                if type[1] == "int":
                    args[1] = int(args[1])
                    args[2] = int(args[2])
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        self.global_frame[name[1]][1] = str(args[1] > args[2]).lower()
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    self.local_frame[self.scope][name[1]][1] = str(args[1] > args[2]).lower()
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        self.temp_frame[name[1]][1] = str(args[1] > args[2]).lower()
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #EQ
            elif self.opcode == "EQ":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if type[1] != type[2] or type[2] == "var":
                    if type[1] != "nil" and type[2] != "nil":
                        exit(53)
                if type[1] == "string":
                    args[1] = self.rewrite_string(args[1])
                    args[2] = self.rewrite_string(args[2])
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        self.global_frame[name[1]][1] = str(args[1] == args[2]).lower()
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    self.local_frame[self.scope][name[1]][1] = str(args[1] == args[2]).lower()
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        self.temp_frame[name[1]][1] = str(args[1] == args[2]).lower()
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #AND
            elif self.opcode == "AND":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "bool":
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        if args[1] == "true" and args[2] == "true":
                            self.global_frame[name[1]][1] = "true"
                        else:
                            self.global_frame[name[1]][1] = "false"
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    if args[1] == "true" and args[2] == "true":
                        self.local_frame[self.scope][name[1]][1] = "true"
                    else:
                        self.local_frame[self.scope][name[1]][1] = "false"
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        if args[1] == "true" and args[2] == "true":
                            self.temp_frame[name[1]][1] = "true"
                        else:
                            self.temp_frame[name[1]][1] = "false"
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #OR
            elif self.opcode == "OR":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != type[2] or type[1] != "bool":
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        if args[1] == "false" and args[2] == "false":
                            self.global_frame[name[1]][1] = "false"
                        else:
                            self.global_frame[name[1]][1] = "true"
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    if args[1] == "false" and args[2] == "false":
                        self.local_frame[self.scope][name[1]][1] = "false"
                    else:
                        self.local_frame[self.scope][name[1]][1] = "true"
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        if args[1] == "false" and args[2] == "false":
                            self.temp_frame[name[1]][1] = "false"
                        else:
                            self.temp_frame[name[1]][1] = "true"
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #NOT
            elif self.opcode == "NOT":
                if type[1] == "var":
                    name = args[1].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            type[1] = self.global_frame[name[1]][0]
                            args[1] = self.global_frame[name[1]][1]
                    if name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        type[1] = self.local_frame[self.scope][name[1]][0]
                        args[1] = self.local_frame[self.scope][name[1]][1]
                    if name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        elif name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            type[1] = self.temp_frame[name[1]][0]
                            args[1] = self.temp_frame[name[1]][1]
                if args[1] == None or type[1] == None:
                    exit(56)
                if type[1] != "bool":
                    exit(53)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "bool"
                        if args[1] == "true":
                            self.global_frame[name[1]][1] = "false"
                        else:
                            self.global_frame[name[1]][1] = "true"
                if name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "bool"
                    if args[1] == "true":
                        self.local_frame[self.scope][name[1]][1] = "false"
                    else:
                        self.local_frame[self.scope][name[1]][1] = "true"
                if name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "bool"
                        if args[1] == "true":
                            self.temp_frame[name[1]][1] = "false"
                        else:
                            self.temp_frame[name[1]][1] = "true"
            #INT2CHAR
            elif self.opcode == "INT2CHAR":
                if type[1] == "var":
                    name = args[1].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            type[1] = self.global_frame[name[1]][0]
                            args[1] = self.global_frame[name[1]][1]
                    if name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        type[1] = self.local_frame[self.scope][name[1]][0]
                        args[1] = self.local_frame[self.scope][name[1]][1]
                    if name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        elif name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            type[1] = self.temp_frame[name[1]][0]
                            args[1] = self.temp_frame[name[1]][1]
                if args[1] == None or type[1] == None:
                    exit(56)
                if type[1] != "int":
                    exit(53)
                try:
                    args[1] = chr(int(args[1]))
                except ValueError:
                    exit(58)
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "string"
                        self.global_frame[name[1]][1] = args[1]
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "string"
                    self.local_frame[self.scope][name[1]][1] = args[1]
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "string"
                        self.temp_frame[name[1]][1] = args[1]
            #STRI2INT
            elif self.opcode == "STRI2INT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if type[2] != "int" or type[1] != "string":
                    if type[1] == None or type[2] == None:
                        exit(56)
                    exit(53)
                args[1] = self.rewrite_string(args[1])
                try:
                    index = int(args[2])
                except ValueError:
                    exit(58)
                if index >= len(args[1]) or index < 0:
                    exit(58)
                char = args[1][index]
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "int"
                        self.global_frame[name[1]][1] = ord(char)
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "int"
                    self.local_frame[self.scope][name[1]][1] = ord(char)
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "int"
                        self.temp_frame[name[1]][1] = ord(char)
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #READ
            elif self.opcode == "READ":
                if self.input_file == sys.stdin:
                    try:
                        input_to_read = input()
                    except EOFError:
                        input_to_read = ""
                else:
                    input_to_read = self.input_file.readline().replace('\n', "")
                if args[1] == "int":
                    try:
                        input_to_read = int(input_to_read)
                    except:
                        input_to_read = "nil"
                        args[1] = "nil"
                elif args[1] == "bool":
                    if(input_to_read.lower() == "true"):
                        input_to_read = "true"
                    else:
                        input_to_read = "false"
                elif args[1] == "string" and input_to_read != None:
                    input_to_read = re.sub('&lt;', '<', input_to_read)
                    input_to_read = re.sub('&gt;', '>', input_to_read)
                    input_to_read = re.sub('&amp;', '&', input_to_read)
                    input_to_read = re.sub('&quot;', '"', input_to_read)
                    input_to_read = re.sub('&apos;', '\'', input_to_read)
                    pattern = r'\\\d{3}'
                    match = re.search(pattern, input_to_read)
                    while match:
                        num = int(match.group()[1:])
                        char = chr(num)
                        input_to_read = re.sub(pattern, char, input_to_read, count=1)
                        match = re.search(pattern, input_to_read)
                if input_to_read == None:
                    input_to_read = ""
                    args[1] = "nil"
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = args[1]
                        self.global_frame[name[1]][1] = input_to_read
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = args[1]
                    self.local_frame[self.scope][name[1]][1] = input_to_read
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = args[1]
                        self.temp_frame[name[1]][1] = input_to_read
            #WRITE
            elif self.opcode == "WRITE":
                if type[0] == "var":
                    value = args[0]
                    typ = type[0]
                    name = args[0].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            type[0] = self.global_frame[name[1]][0]
                            args[0] = self.global_frame[name[1]][1]
                    if name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        type[0] = self.local_frame[self.scope][name[1]][0]
                        args[0] = self.local_frame[self.scope][name[1]][1] 
                    if name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        elif name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            type[0] = self.temp_frame[name[1]][0]
                            args[0] = self.temp_frame[name[1]][1]
                    if args[0] == None:
                        exit(56)
                    elif type[0] == "int":
                        print(int(args[0]), end='')
                    elif type[0] == "bool":
                        print(args[0], end='')
                    elif type[0] == "nil":
                        print("", end='')
                    elif type[0] == "string":
                        input_to_read = self.rewrite_string(args[0])
                        print(input_to_read, end='')
                    type[0] = typ
                    args[0] = value
                else:
                    if type[0] == "int":
                        print(int(args[0]), end='')
                    elif type[0] == "bool":
                        print(args[0], end='')
                    elif type[0] == "nil":
                        print("", end='')
                    elif type[0] == "string":
                        input_to_read = self.rewrite_string(args[0])
                        print(input_to_read, end='')
            #CONCAT
            elif self.opcode == "CONCAT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if type[1] != type[2] or type[1] != "string":
                    exit(53)
                else:
                    name = args[0].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            self.global_frame[name[1]][0] = "string"
                            self.global_frame[name[1]][1] = args[1] + args[2]
                    if name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        self.local_frame[self.scope][name[1]][0] = "string"
                        self.local_frame[self.scope][name[1]][1] = args[1] + args[2]
                    if name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        elif name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            self.temp_frame[name[1]][0] = "string"
                            self.temp_frame[name[1]][1] = args[1] + args[2]
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #STRLEN
            elif self.opcode == "STRLEN":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,2):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if type[1] != "string":
                    if type[1] == None:
                        exit(56)
                    exit(53)
                else:
                    name = args[0].split('@')
                    if name[0] == "GF":
                        if name[1] not in self.global_frame:
                            exit(54)
                        else:
                            self.global_frame[name[1]][0] = "int"
                            if args[1] == None:
                                self.global_frame[name[1]][1] = 0
                            else:
                             self.global_frame[name[1]][1] = len(args[1])
                    if name[0] == "LF":
                        if not self.lf_exists:
                            exit(55)
                        if self.scope in self.local_frame:
                            if name[1] not in self.local_frame[self.scope]:
                                exit(54)
                        else:
                                exit(54)
                        self.local_frame[self.scope][name[1]][0] = "int"
                        if args[1] == None:
                            self.local_frame[self.scope][name[1]][1] = 0
                        else:
                            self.local_frame[self.scope][name[1]][1] = len(args[1])
                    if name[0] == "TF":
                        if not self.tf_exists:
                            exit(55)
                        elif name[1] not in self.temp_frame:
                            exit(54)
                        else:
                            self.temp_frame[name[1]][0] = "int"
                            if args[1] == None:
                                self.temp_frame[name[1]][1] = 0
                            else:
                             self.temp_frame[name[1]][1] = len(args[1])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #GETCHAR
            elif self.opcode == "GETCHAR":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[2] != "int" or type[1] != "string":
                    exit(53)
                try:
                    index = int(args[2])
                except ValueError:
                    exit(58)
                if index >= len(args[1]) or index < 0:
                    exit(58)
                char = args[1][index]
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "string"
                        self.global_frame[name[1]][1] = char
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "string"
                    self.local_frame[self.scope][name[1]][1] = char
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "string"
                        self.temp_frame[name[1]][1] = char
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #SETCHAR
            elif self.opcode == "SETCHAR":
                help_stack = []
                typ = {}
                value = {}
                for i in range(0,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if 2 not in typ:
                    if args[2] == None:
                        exit(58)
                if args[0] == None:
                    exit(56)
                if args[1] == None or type[1] == None:
                    exit(56)
                if args[2] == None or type[2] == None:
                    exit(56)
                if type[1] != "int" or type[2] != "string" or type[0] != "string":
                    exit(53)
                try:
                    index = int(args[1])
                except ValueError:
                    exit(58)
                if args[0] == None:
                    exit(56)
                if int(args[1]) >= len(args[0]) or int(args[1]) < 0:
                    exit(58)
                args[2] = self.rewrite_string(args[2])
                if len(args[2]) == 0:
                    exit(58)
                var_list = list(args[0])  # Convert string to list
                var_list[index] = args[2][0]  # Modify the character at the given index
                args[0] = "".join(var_list)  # Convert list back to string and update the variable
                rewrite = args[0]
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "string"
                        self.global_frame[name[1]][1] = rewrite
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "string"
                    self.local_frame[self.scope][name[1]][1] = rewrite
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "string"
                        self.temp_frame[name[1]][1] = rewrite
            #TYPE
            elif self.opcode == "TYPE":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,2):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value1 = self.getfromvar(args,type,i,typ,value)
                if type[1] == None:
                    value = ""
                else:
                    value = type[1]
                name = args[0].split('@')
                if name[0] == "GF":
                    if name[1] not in self.global_frame:
                        exit(54)
                    else:
                        self.global_frame[name[1]][0] = "string"
                        self.global_frame[name[1]][1] = value
                elif name[0] == "LF":
                    if not self.lf_exists:
                        exit(55)
                    if self.scope in self.local_frame:
                        if name[1] not in self.local_frame[self.scope]:
                            exit(54)
                    else:
                        exit(54)
                    self.local_frame[self.scope][name[1]][0] = "string"
                    self.local_frame[self.scope][name[1]][1] = value
                elif name[0] == "TF":
                    if not self.tf_exists:
                        exit(55)
                    elif name[1] not in self.temp_frame:
                        exit(54)
                    else:
                        self.temp_frame[name[1]][0] = "string"
                        self.temp_frame[name[1]][1] = value
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value1[k]
            #LABEL
            elif self.opcode == "LABEL":
                pass
            #JUMP
            elif self.opcode == "JUMP":
                if args[0] not in self.label_dict:
                    exit(54)
                else:
                    count = self.label_dict[args[0]]
            #JUMPIFEQ
            elif self.opcode == "JUMPIFEQ":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if args[0] not in self.label_dict:
                    exit(52)
                else:
                    if (type[1] == type[2]):
                        if type[1] == "int":
                            value1 = int(args[1])
                            value2 = int(args[2])
                        else:
                            if type[1] == "string":
                                args[1] = self.rewrite_string(args[1])
                                args[2] = self.rewrite_string(args[2])
                            value1 = args[1]
                            value2 = args[2]
                        if (value1 == value2):
                            count = self.label_dict[args[0]]
                    elif type[1] != "nil" and type[2] != "nil":
                        exit(53)
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #JUMPIFNEQ
            elif self.opcode == "JUMPIFNEQ":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,3):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[1] == None:
                    if type[1] == None:
                        exit(56)
                    args[1] = ""
                if args[2] == None:
                    if type[2] == None:
                        exit(56)
                    args[2] = ""
                if args[0] not in self.label_dict:
                    exit(52)
                else:
                    if (type[1] == type[2]) or type[1] == "nil" or type[2] == "nil":
                        if type[1] == "int" and type[2] == "int":
                            value1 = int(args[1])
                            value2 = int(args[2])
                        else:
                            if type[1] == "string":
                                args[1] = self.rewrite_string(args[1])
                                args[2] = self.rewrite_string(args[2])
                            value1 = args[1]
                            value2 = args[2]
                        if (value1 != value2):
                            count = self.label_dict[args[0]]
                    elif type[1] != "nil" and type[2] != "nil":
                        exit(53)
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #EXIT
            elif self.opcode == "EXIT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(0,1):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[0] == None:
                    exit(56)
                if type[0] != "int":
                    exit(53)
                elif int(args[0]) > 49 or int(args[0]) < 0:
                    exit(57)
                elif args[0] == "":
                    exit(56)
                else:
                    exit(int(args[0]))
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
            #DPRINT
            elif self.opcode == "DPRINT":
                help_stack = []
                typ = {}
                value = {}
                for i in range(1,2):
                    if type[i] == "var":
                        help_stack.append(i)
                        typ, value = self.getfromvar(args,type,i,typ,value)
                if args[0] == None:
                    print("")
                else:
                    print(args[0])
                for k in help_stack:
                    type[k] = typ[k]
                    args[k] = value[k]
             # increment the count
            count += 1
if __name__ == "__main__":
    # create an instance of the Args class and parse the command line arguments
    args = Args()
    args.execute_program_params()
    # create an instance of the ProgramXMLReader class and read the XML file
    XML = ProgramXMLReader(args.soursefile)
    XML.execute_program
    # create instances of the Instructions and Interpret classes
    instr = Instructions(XML._root)
    program = Interpret(instr.instr_dict, instr.label_dict, args.inputfile)

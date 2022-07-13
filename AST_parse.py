
import json
import sys
import re
from functools import reduce
import CFG_process

def parse(js):
    if js is None:
        return ""
    elif js['nodeType'] == 'SourceUnit':
        return parse_SourceUnit(js)
    elif js['nodeType'] == 'PragmaDirective':
        return parse_PragmaDirective(js)
    elif js['nodeType'] == 'ContractDefinition':
        return parse_ContractDefinition(js)
    elif js['nodeType'] == 'VariableDeclaration':
        return parse_VariableDeclaration(js)
    elif js['nodeType'] == 'VariableDeclarationStatement':
        return parse_VariableDeclarationStatement(js)
    elif js['nodeType'] == 'Mapping':
        return parse_Mapping(js)
    elif js['nodeType'] == 'ElementaryTypeName':
        return parse_ElementaryTypeName(js)
    elif js['nodeType'] == 'EventDefinition':
        return parse_EventDefinition(js)
    elif js['nodeType'] == 'ModifierDefinition':
        return parse_ModifierDefinition(js)
    elif js['nodeType'] == 'FunctionDefinition':
        return parse_FunctionDefinition(js)
    elif js['nodeType'] == 'FunctionCall':
        return parse_FunctionCall(js)
    elif js['nodeType'] == 'Return':
        return parse_Return(js)
    elif js['nodeType'] == 'ParameterList':
        return parse_ParameterList(js)
    elif js['nodeType'] == 'StructDefinition':
        return parse_StructDefinition(js)
    elif js['nodeType'] == 'EnumDefinition':
        return parse_EnumDefinition(js)
    elif js['nodeType'] == 'EnumValue':
        return parse_EnumValue(js)
    elif js['nodeType'] == 'UserDefinedTypeName':
        return parse_UserDefinedTypeName(js)
    elif js['nodeType'] == 'ArrayTypeName':
        return parse_ArrayTypeName(js)
    elif js['nodeType'] == 'TupleExpression':
        return parse_TupleExpression(js)
    elif js['nodeType'] == 'Block':
        return parse_Block(js)
    elif js['nodeType'] == 'IfStatement':
        return parse_IfStatement(js)
    elif js['nodeType'] == 'ForStatement':
        return parse_ForStatement(js)
    elif js['nodeType'] == 'WhileStatement':
        return parse_WhileStatement(js)
    elif js['nodeType'] == 'ExpressionStatement':
        return parse_ExpressionStatement(js)
    elif js['nodeType'] == 'Assignment':
        return parse_Assignment(js)
    elif js['nodeType'] == 'UnaryOperation':
        return parse_UnaryOperation(js)
    elif js['nodeType'] == 'BinaryOperation':
        return parse_BinaryOperation(js)
    elif js['nodeType'] == 'IndexAccess':
        return parse_IndexAccess(js)
    elif js['nodeType'] == 'MemberAccess':
        return parse_MemberAccess(js)
    elif js['nodeType'] == 'Identifier':
        return parse_Identifier(js)
    elif js['nodeType'] == 'ElementaryTypeNameExpression':
        return parse_ElementaryTypeNameExpression(js)
    elif js['nodeType'] == 'PlaceholderStatement':
        return parse_PlaceholderStatement(js)
    elif js['nodeType'] == 'Continue':
        return parse_Continue(js)
    elif js['nodeType'] == 'Literal':
        return parse_Literal(js)
    else:
        return ""

def parse_var_names(_str):
    global found_first_function
    _str = str(_str)
    if found_first_function:

        space_sep_str = re.sub('([A-Z]+)', r' \1', _str).lower()
        space_sep_str = re.sub('_', ' ', space_sep_str).lower()
        return " " + space_sep_str + " "
    else:
        return ""

def dedupe_spaces(description):
    single_space_sep_desc = re.sub(' +', ' ', description)
    single_space_sep_desc = re.sub(' \'', '\'', single_space_sep_desc)
    single_space_sep_desc = re.sub(' ,', ',', single_space_sep_desc)
    return single_space_sep_desc

def parse_Literal(js):
    return parse_var_names(js['value'])

def parse_Continue(js):
    return "do nothing"

def parse_PlaceholderStatement(js):
    return ""

def parse_ElementaryTypeNameExpression(js):
    return ""

def parse_Identifier(js):
    global msg_found
    if js['name'] == 'msg':
        msg_found = True
        return ""
    else:
        return parse_var_names(js['name'])

def parse_MemberAccess(js):
    global msg_found
    ret_str = parse(js['expression'])
    if msg_found:
        ret_str += parse_var_names(templates[js['memberName']])
        msg_found = False
    else:
        ret_str += parse_var_names('\'s ' + js['memberName'] + ' ')
    return ret_str

def parse_IndexAccess(js):
    return parse(js['baseExpression']) \
           + parse_var_names(" list at ") \
           + parse(js['indexExpression'])

def parse_BinaryOperation(js):
    return parse(js['leftExpression']) \
           + parse_var_names(templates[js['operator']]) \
           + parse(js['rightExpression'])

def parse_UnaryOperation(js):
    return parse_var_names(templates[js['operator']]) \
           + parse(js['subExpression'])

def parse_Assignment(js):
    return parse(js['leftHandSide']) \
           + parse_var_names(templates[js['operator']]) \
           + parse(js['rightHandSide'])

def parse_ExpressionStatement(js):
    return dedupe_spaces(parse(js['expression']))

def parse_IfStatement(js):
    cond_str = parse(js['condition'])

    ret_str = "\nIf " + cond_str + " then do "
    ret_str += parse(js['trueBody'])

    if js['falseBody'] != None:
        ret_str += "\nIf it is not the case that " + cond_str
        ret_str += parse(js['falseBody'])

    return dedupe_spaces(ret_str)

def parse_WhileStatement(js):
    return "\nAs long as " \
           + parse(js['condition']) \
           + " do\n" \
           + parse(js['body']) \
           + " and this continues as long as " \
           + parse(js['condition']) + "\n"

def parse_ForStatement(js):
    global in_for_loop_header

    in_for_loop_header = True
    ret_str = "\nSet "
    ret_str += parse(js['initializationExpression'])
    ret_str += "\nThen as long as "
    ret_str += parse(js['condition'])
    ret_str += " do\n"

    in_for_loop_header = False
    ret_str += parse(js['body'])
    ret_str += "\nEach time that happens "

    in_for_loop_header = True
    ret_str += parse(js['loopExpression'])
    ret_str += " and this continues as long as "
    ret_str += parse(js['condition'])

    return dedupe_spaces(ret_str) + "\n"

def parse_Block(js):
    ret_str = ""
    ret_strs = []
    for js_expr in js['statements']:
        if js_expr['nodeType'] != 'IfStatement' \
           and js_expr['nodeType'] != 'ForStatement' \
           and js_expr['nodeType'] != 'WhileStatement':
            ret_strs.append(dedupe_spaces(parse(js_expr).strip()))
        else:
            ret_strs = CFG_process.preproc(ret_strs)
            ret_str += reduce(CFG_process.concat, ret_strs, "")
            ret_strs = []
            ret_str += parse(js_expr)

    if ret_strs:
        ret_strs = CFG_process.preproc(ret_strs)
        ret_str += reduce(CFG_process.concat, ret_strs, "")
    return ret_str

def parse_TupleExpression(js):
    ret_str = ""
    for component in js['components']:
        ret_str += parse(component)
    return ret_str

def parse_ArrayTypeName(js):
    return parse(js['baseType'])

def parse_UserDefinedTypeName(js):
    return ""

def parse_EnumDefinition(js):
    ret_str = ""
    for member in js['members']:
        ret_str += parse(member)
    return ret_str

def parse_EnumValue(js):
    return ""

def parse_StructDefinition(js):
    ret_str = ""
    for member in js['members']:
        ret_str += parse(member)
    return ret_str

def parse_ParameterList(js):
    ret_str = ""
    for param in js['parameters']:
        ret_str += parse(param)
    return ret_str

def parse_Return(js):
    if js['expression'] != None:
        return parse(js['expression'])
    else:
        return ""

def parse_FunctionCall(js):
    ret_str = parse(js['expression'])
    for arg in js['arguments']:
        ret_str += parse(arg)
    return ret_str

def parse_FunctionDefinition(js):
    global found_first_function
    found_first_function = True
    func = {}
    func[js['name']]=parse(js['body'])
    return str(func)

def parse_ModifierDefinition(js):
    return parse(js['parameters']) + parse(js['body'])

def parse_EventDefinition(js):

    return parse(js['parameters'])

def parse_ElementaryTypeName(js):
    return ""

def parse_Mapping(js):
    return parse(js['keyType']) + parse(js['valueType'])

def parse_VariableDeclarationStatement(js):
    ret_str = ""
    declarations_size = len(js['declarations'])
    for declaration in js['declarations']:
        ret_str += parse(declaration)
        if declarations_size > 1:
            ret_str += parse_var_names(' and ')
        declarations_size -= 1
    ret_str += parse_var_names(' is ')
    if js['initialValue'] != None:
        ret_str += parse(js['initialValue'])
    else:
        ret_str += parse_var_names(' default value ')
    if not in_for_loop_header:
        ret_str = dedupe_spaces(ret_str)
    return ret_str

def parse_VariableDeclaration(js):
    return parse_var_names(js['name'])

def parse_ContractDefinition(js):
    ret_str = ""
    for js_node in js['nodes']:
        ret_str += parse(js_node)
    return ret_str

def parse_PragmaDirective(js):
    return ""

def parse_SourceUnit(js):
    ret_str = ""
    for js_node in js['nodes']:
        ret_str += parse(js_node)
    return ret_str

templates = {"data": " the complete calldata ", "gas": " the remaining money in this function ", "sender": " the money sender ", "sig": " the function the sender activated ", "value": " the money sent by the sender ", "*": " multiplied by ", "/": " divided by ", "%": " remainder of ", "+": " added to ", "-": " subtracted by ", "&&": " and ", "||": " or ", ">": " is greater than ", "<": " is less than ", ">=": " is greater than or equal to ", "<=": " is less than or equal to ", "==": " is equal to ", "!=": " is not equal to ", "**": "to the power of", "<<": " is shifted left by", ">>": " is shifted right by", "|": "or", "++": " add one to ", "--": " remove one from ", "!": " not ", "-": " negative of ", "=": " is ", "+=": " gains ", "|=": "gains", "-=": " loses ", "*=": " multiplied by ", "/=": " divided by ", "%=": " moded by ", "delete": "delete"}

msg_found = False
found_first_function = False

in_for_loop_header = False

if __name__ == "__main__":
    # Get path to solcTrans json output
    file_path = sys.argv[1]
    file_contents = ''
    with open(file_path, 'r') as file:
        line_num = 0
        for line in file:
            # Skip first 4 lines
            if line_num >= 4:
                file_contents += line;
            line_num += 1
    solc_json = json.loads(file_contents)
    print("\n\n" + re.sub("[\n]{2,}", "\n\n", parse(solc_json)))


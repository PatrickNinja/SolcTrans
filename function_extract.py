import sys
import pprint
import json

# from solidity_parser import parser
#
# sourceUnit = parser.parse_file("test.sol")
# json_str = json.dumps(sourceUnit, indent=4)
# with open('test_data.json', 'w') as json_file:
#     json_file.write(json_str)
# pprint.pprint(sourceUnit)

import re

def parChecker(symbolString):
    str = ''
    count = 0
    for char in symbolString:
        if char == "{":
            count = count + 1
        if char == "}":
            count = count - 1
        str = str + char
        if count == 0:
            break
    return str



def funcExtract(str, funcname):
    functions = {}
    for func in funcname:
        pmin = re.compile(r'function '+ func +'[(]([\s\S]*?)[)]')
        parse_json = re.findall(pmin, str)
        parse_json_new = ["function "+ func +"("+item+")" for item in parse_json]
        if parse_json_new == []:
            continue
        rest = str.split(parse_json_new[0])[-1]
        funchead = parse_json_new[0] + rest.split("{")[0]
        funcbody = rest.lstrip(rest.split("{")[0])
        functions[func] = funchead + parChecker(funcbody)
    return functions




# address = '0xdc59242010e2d29617bfeec57e62c7c00a5acb52'
# solpath = 'D:/codesearch/sols/'+address+'.sol'
# with open(solpath, 'r') as f:
#     data = f.read()
#
# intersection = ['convertInternal', 'convert', 'getPurchaseReturn', 'withdrawFromToken', 'getSaleReturn', 'transferOwnership', 'addConnector', 'disableTokenTransfers', 'disableConnectorPurchases', 'acceptTokenOwnership', 'getCrossConnectorReturn', 'updateConnector', 'getConnectorBalance', 'disableConversions', 'getQuickBuyPathLength', 'transferManagement', 'quickConvert', 'quickConvertPrioritized', 'getReturn', 'connectorTokenCount', 'transferTokenOwnership', 'acceptOwnership', 'setConversionFee', 'acceptManagement', 'withdrawTokens']
#
# aa = funcExtract(data, intersection)
# print(aa)

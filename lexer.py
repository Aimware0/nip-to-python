from NTIPAliasQuality import NTIPAliasQuality
from NTIPAliasClass import NTIPAliasClass
from NTIPAliasClassID import NTIPAliasClassID
from NTIPAliasFlag import NTIPAliasFlag
from NTIPAliasStat import NTIPAliasStat
from NTIPAliasType import NTIPAliasType

from tokens import Token, TokenType
from enum import Enum

import json



item_data = json.loads("""{
    "Name": "RUNE LOOP",
    "Quality": "rare",
    "Text": "RUNE LOOP|RING|REQUIRED LEVEL: 15|+1 TO MAXIMUM DAMAGE|3% LIFE STOLEN PER HIT|+5 TO STRENGTH|COLD RESIST +11%|FIRE RESIST +23%|9% BETTER CHANCE OF GETTING MAGIC ITEMS",
    "BaseItem":
    {
        "DisplayName": "Ring",
        "NTIPAliasClassID": 522,
        "NTIPAliasType": 10,
        "dimensions": [1, 1],
        "sets": ["ANGELICHALO", "CATHANSSEAL"],
        "uniques": ["NAGELRING", "MANALDHEAL", "THESTONEOFJORDAN", "CONSTRICTINGRING", "BULKATHOSWEDDINGBAND", "DWARFSTAR", "RAVENFROST", "NATURESPEACE", "WISPPROJECTOR", "CARRIONWIND"]
    },
    "Item": null,
    "NTIPAliasType": 10,
    "NTIPAliasClassID": 522,
    "NTIPAliasClass": null,
    "NTIPAliasQuality": 6,
    "NTIPAliasStat":
    {
        "43": 11,
        "39": 23,
        "80": 9,
        "22": 1,
        "0": 5,
        "60": 3
    },
    "NTIPAliasFlag":
    {
        "0x10": true,
        "0x4000000": false,
        "0x400000": true
    }
}""")

WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789.%"
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "", "", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["(", ")", "^", "*", "/", "\\", "+", "-"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'"

class Lexer:
    def __init__(self, nip_expression):
        self.text = iter(nip_expression)
        self.advance()

    def advance(self):
        try:
            self.current_token = next(self.text)
        except StopIteration:
            self.current_token = None

    def create_tokens(self):
        while self.current_token != None:
            if self.current_token in DIGITS:
                yield self.create_digits()
            elif self.current_token in WHITESPACE:
                self.advance()
                # yield Token(TokenType.WHITESPACE, " ")
            elif self.current_token in SYMBOLS:
                yield self.create_logical_operator()
            elif self.current_token in MATH_SYMBOLS:
                yield self.create_math_operator()
                # self.advance()
            elif self.current_token == "[":
                yield self.create_nip_lookup()
            elif self.current_token in CHARS:
                yield self.create_d2r_image_data_lookup()
        
    def create_digits(self):
        dot_count = 0
        n_str = self.current_token
        self.advance()
        while self.current_token != None and self.current_token in DIGITS:
            if self.current_token == ".":
                if dot_count >= 1:
                    break
                dot_count += 1
            n_str += self.current_token
            
            if self.current_token == "%":
                self.advance()
                break
            self.advance()

        if n_str.startswith("."):
            n_str = "0" + n_str
        elif n_str.endswith("."):
            n_str = n_str + "0"
        elif n_str.endswith("%"):
            return Token(TokenType.NUMBERPERCENT, n_str[:-1])

        return Token(TokenType.NUMBER, float(n_str))


    def create_math_operator(self):
        symbol = self.current_token
        self.advance()

        symbol_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '\\': TokenType.MODULO,
            '^': TokenType.POW
        }

        while self.current_token != None:            

            if symbol == "+":
                return Token(TokenType.PLUS, symbol)
            elif symbol == "-":
                return Token(TokenType.MINUS, symbol)
            elif symbol == "*":
                return Token(TokenType.MULTIPLY, symbol)
            elif symbol == "/":
                return Token(TokenType.DIVIDE, symbol)
            elif symbol == "\\":
                return Token(TokenType.MODULO, symbol)
            elif symbol == "^":
                return Token(TokenType.POW, symbol)
            elif symbol == "(":
                return Token(TokenType.LPAREN, symbol)
            elif symbol == ")":
                return Token(TokenType.RPAREN, symbol)

        if symbol == "(":
            return Token(TokenType.LPAREN, symbol)
        elif symbol == ")":
            return Token(TokenType.RPAREN, symbol)
 
            
    def create_nip_lookup(self):
        self.advance()
        lookup_key = self.current_token

        while self.current_token != None:
            self.advance()

            if self.current_token == "]":
                break
            lookup_key += self.current_token

        self.advance()

        if lookup_key in "name":
            return Token(TokenType.NAME, lookup_key)
        elif lookup_key == "flag":
            return Token(TokenType.FLAG, lookup_key)
        elif lookup_key == "class":
            return Token(TokenType.CLASS, lookup_key)
        elif lookup_key == "quality":
            return Token(TokenType.QUALITY, lookup_key)
        elif lookup_key == "maxquanity":
            return Token(TokenType.MAXQUANITY, lookup_key)
        elif lookup_key == "type":
            return Token(TokenType._TYPE, lookup_key)
        elif lookup_key in NTIPAliasClass:
            return Token(TokenType.NTIPAliasClass, NTIPAliasClass[lookup_key])
        elif lookup_key in NTIPAliasQuality:
            return Token(TokenType.NTIPAliasQuality, NTIPAliasQuality[lookup_key])
        elif lookup_key in NTIPAliasClassID:
            return Token(TokenType.NTIPAliasClassID, NTIPAliasClassID[lookup_key])
        elif lookup_key in NTIPAliasFlag:
            return Token(TokenType.NTIPAliasFlag, NTIPAliasFlag[lookup_key])
        elif lookup_key in NTIPAliasStat:
            return Token(TokenType.NTIPAliasStat, NTIPAliasStat[lookup_key])
        elif lookup_key in NTIPAliasType:
            return Token(TokenType.NTIPAliasType, NTIPAliasType[lookup_key])
        else:
            return Token(TokenType.UNKNOWN, "-1")
        
    def create_d2r_image_data_lookup(self):
        lookup_key = self.current_token

        while self.current_token != None:
            self.advance()
            if self.current_token == None or self.current_token not in CHARS:
                break
            
            if self.current_token == "'":
                self.current_token = "\\'" # TODO FIX THIS (make stuff like diablo'shorn work..)
            lookup_key += self.current_token

        # Converts stuff like ethereal to NTIPAliasFlag['ethereal']
        if lookup_key in NTIPAliasClass:
            return Token(TokenType.NTIPAliasClass, lookup_key)
        elif lookup_key in NTIPAliasQuality:
            return Token(TokenType.NTIPAliasQuality, lookup_key)
        elif lookup_key in NTIPAliasClassID:
            return Token(TokenType.NTIPAliasClassID, lookup_key)
        elif lookup_key in NTIPAliasFlag:
            return Token(TokenType.NTIPAliasFlag, lookup_key)
        elif lookup_key in NTIPAliasStat:
            return Token(TokenType.NTIPAliasStat, lookup_key)
        elif lookup_key in NTIPAliasType:
            return Token(TokenType.NTIPAliasType, lookup_key)
        else:
            return Token(TokenType.UNKNOWN, "-1")


    def create_logical_operator(self):
        char = self.current_token
        self.advance()
        while self.current_token != None:
            
            if char == ">":
                if self.current_token == "=":
                    self.advance()
                    return Token(TokenType.GE, ">=")
                else:
                    return Token(TokenType.GT, ">")
            elif char == "<":
                if self.current_token == "=":
                    self.advance()
                    return Token(TokenType.LE, "<=")
                else:
                    return Token(TokenType.LT, "<")
            elif char == "=":
                if self.current_token == "=":
                    self.advance()
                    return Token(TokenType.EQ, "==")
            elif char == "!":
                if self.current_token == "=":
                    self.advance()
                    return Token(TokenType.NE, "!=")
            elif char == "&":
                if self.current_token == "&":
                    self.advance()
                    return Token(TokenType.AND, "and")
            elif char == "#":
                return Token(TokenType.AND, "and")
            elif char == "|":
                if self.current_token == "|":
                    self.advance()
                    return Token(TokenType.OR, "or")
            elif char == "/":
                if self.current_token == "/":
                    self.advance()
                    return Token(TokenType.COMMENT, "") # We don't really need comments in the transpiled version...
                else:
                    return Token(TokenType.DIVIDE, "/")
            else:
                # print("Unknown operator", char)
                break
        
        if char == "#":
            return Token(TokenType.AND, "and")

        self.advance()

class Transpiler:
    def transpile(self, tokens):
        expression = ""
        for i, token in enumerate(tokens):
            if token == None:
                continue
            if token.type == TokenType.NTIPAliasStat:
                if len(tokens) >= i + 2 and tokens[i + 2].type == TokenType.NUMBERPERCENT: # Look at the other side of the comparsion.
                    # Write an expression to test make sure the item_data['Item']['NTIPAliasStatProps'] is a dict.
                    stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                    stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"

                    is_dict = eval(f"isinstance({stat_min_max}, dict)") # ghetto, but for now, ok..
                    if is_dict:
                        expression += f"(int(({stat_value} - {stat_min_max}['min']) * 100.0 / ({stat_min_max}['max'] - {stat_min_max}['min'])))"
                    else:
                        expression += f"(int(-1))" # Ignore it since it wasn't a dict and the user tried to use a %
                else:
                    # stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                    # stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                    # clamp value between min and max
            
                    # expression += f"(({stat_value} >= {stat_min_max}['max'] and {stat_min_max}['max']) or ({stat_value} <= {stat_min_max}['min'] and {stat_min_max}['min']) or {stat_value})"
                    # expression += f"(int(item_data['NTIPAliasStat']['{token.value}']))"
                    expression += f"(int(item_data['NTIPAliasStat'].get('{token.value}', -1)))"
            elif token.type == TokenType.NTIPAliasClass:
                expression += f"(int(NTIPAliasClass['{token.value}']))"
            elif token.type == TokenType.NTIPAliasQuality:
                expression += f"(int(NTIPAliasQuality['{token.value}']))"
            elif token.type == TokenType.NTIPAliasClassID:
                expression += f"(int(NTIPAliasClassID['{token.value}']))"
            elif token.type == TokenType.NTIPAliasFlag:
                pass
                # we don't need the flag value here, it's used below
                # expression += f"NTIPAliasFlag['{token.value}']"
            elif token.type == TokenType.NTIPAliasType:
                expression += f"(int(NTIPAliasType['{token.value}']))"
            elif token.type == TokenType.NAME:
                expression += "(int(item_data['NTIPAliasClassID']))"
            elif token.type == TokenType.CLASS:
                expression += "(int(item_data['NTIPAliasClass']))"
            elif token.type == TokenType.QUALITY:
                expression += "(int(item_data['NTIPAliasQuality']))"
            elif token.type == TokenType.FLAG:
                if tokens[i + 2].type == TokenType.NTIPAliasFlag: 
                    condition_type = tokens[i + 1]
                    print(condition_type)
                    if condition_type.type == TokenType.EQ:
                        expression += f"(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
                    elif condition_type.type == TokenType.NE:
                        expression += f"(not item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
                # Check if the flag we're looking for (i.e ethereal) is i + 2 away from here, if it is, grab it's value (0x400000) and place it inside the lookup.
            elif token.type == TokenType._TYPE:
                expression += "(int(item_data['NTIPAliasType']))"
            elif token.type == TokenType.EQ:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += "=="
            elif token.type == TokenType.NE:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += "!="
            elif token.type == TokenType.GT:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += ">"
            elif token.type == TokenType.LT:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += "<"
            elif token.type == TokenType.GE:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += ">="
            elif token.type == TokenType.LE:
                if tokens[i + 1].type != TokenType.NTIPAliasFlag:
                    expression += "<="
            elif token.type == TokenType.NUMBER:
                expression += f"({token.value})"
            elif token.type == TokenType.NUMBERPERCENT:
                expression += f"int({token.value})"
            else:
                expression += f"{token.value}"
                
            expression += "" # add space if spaces are needed
        return expression


    def transpile_nip_expression(self, expression: str):
        if expression.startswith("//") or expression.startswith("-"):
            return None
        expression = expression.split("//")[0].rstrip() # ignore the comments
        try:
            lexer = Lexer(expression)
            tokens = list(lexer.create_tokens())
            return self.transpile(tokens)
        except Exception as e:
            print("\n[ERROR]", expression)
            return


    def transpile_nip_expressions(self, expressions):
        transpiled_expressions = []
        for expression in expressions:
            transpiled_expression = self.transpile_nip_expression(expression)
            if transpiled_expression:
                transpiled_expressions.append(transpiled_expression)
        return transpiled_expressions





# x = transpile_nip_file("kolton.nip")

# write a transpiled.nip file with each expression on a new line

# for i, expression in enumerate(x):
#     with open("transpiled.nip", "a") as file:
#         file.write(expression + "\n")



text = "[name] == duskshroud && [quality] == unique && [flag] == ethereal # [passivecoldmastery] == 15 && [skillblizzard] == 3 //ormus"
expression = Transpiler().transpile_nip_expression(text)
print(expression)
print(eval(expression))


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
    "Name": "War Traveler",
    "Quality": "unique",
    "Text": "WAR TRAVELER|BATTLE BOOTS|DEFENSE: 139|DURABILITY: 13 OF 48|REQUIRED STRENGTH: 95|REQUIRED LEVEL: 42|+25% FASTER RUN/WALK|ADDS 15-25 DAMAGE|+190% ENHANCED DEFENSE|+10 TO STRENGTH|+10 TO VITALITY|40% SLOWER STAMINA DRAIN|ATTACKER TAKES DAMAGE OF 10|50% BETTER CHANCE OF GETTING MAGIC ITEMS",
    "BaseItem":
    {
        "DisplayName": "Battle Boots",
        "NTIPAliasClassID": 388,
        "NTIPAliasType": 15,
        "NTIPAliasStatProps":
        {
            "72": 18,
            "73": 18,
            "31":
            {
                "min": 39,
                "max": 47
            },
            "0x400000":
            {
                "min": 0,
                "max": 1
            }
        },
        "dimensions": [2, 2],
        "sets": ["ALDURSADVANCE"],
        "uniques": ["WARTRAVELER"],
        "NTIPAliasClass": 1
    },
    "Item":
    {
        "DisplayName": "War Traveler",
        "NTIPAliasClassID": 388,
        "NTIPAliasType": 15,
        "NTIPAliasStatProps":
        {
            "3":
            {
                "min": 10,
                "max": 10
            },
            "0":
            {
                "min": 10,
                "max": 10
            },
            "80":
            {
                "min": 30,
                "max": 50
            },
            "72": 30,
            "73": 30,
            "96":
            {
                "min": 25,
                "max": 25
            },
            "16,0":
            {
                "min": 150,
                "max": 190
            },
            "21": 15,
            "22": 25,
            "78":
            {
                "min": 5,
                "max": 10
            },
            "154":
            {
                "min": 40,
                "max": 40
            }
        }
    },
    "NTIPAliasType": 15,
    "NTIPAliasClassID": 388,
    "NTIPAliasClass": null,
    "NTIPAliasQuality": 7,
    "NTIPAliasStat":
    {
        "21": 15,
        "22": 25,
        "78": 10,
        "31": 139,
        "72": 13,
        "73": 48,
        "80": 50,
        "0": 10,
        "3": 10,
        "16": 190,
        "96": 25,
        "154": 40
    },
    "NTIPAliasFlag":
    {
        "0x10": true,
        "0x4000000": false
    }
}""")


WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789."
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "(", ")", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["^", "*", "/", "\\", "+", "-"]
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"

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
                self.advance()
            elif self.current_token == "[":
                yield self.create_nip_lookup()
            elif self.current_token in CHARS:
                yield self.create_d2r_image_data_lookup()

    def create_digits(self):
        dot_count = 0
        n_str = self.current_token
        self.advance()
        while self.current_token != None and (self.current_token.isdigit() or self.current_token == "."):
            if self.current_token == ".":
                if dot_count >= 1:
                    break
                dot_count += 1
            n_str += self.current_token
            self.advance()

        if n_str.startswith("."):
            n_str = "0" + n_str
        elif n_str.endswith("."):
            n_str = n_str + "0"

        return Token(TokenType.NUMBER, float(n_str))


    def create_math_operator(self):
        symbol = self.current_token
        self.advance()
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
        
    def create_d2r_image_data_lookup(self):
        lookup_key = self.current_token

        while self.current_token != None:
            self.advance()
            if self.current_token == None or self.current_token not in CHARS:
                break
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
                    return Token(TokenType.COMMENT, "#")
            else:
                print("Unknown operator")
                break
        
        if char == "#":
            return Token(TokenType.AND, "and")

        self.advance()


def transpile(tokens):
    expression = ""


    for i, token in enumerate(tokens):
        if token.type == TokenType.NTIPAliasStat:
            expression += f"NTIPAliasStat['{token.value}']"
        elif token.type == TokenType.NTIPAliasClass:
            expression += f"NTIPAliasClass['{token.value}']"
        elif token.type == TokenType.NTIPAliasQuality:
            expression += f"NTIPAliasQuality['{token.value}']"
        elif token.type == TokenType.NTIPAliasClassID:
            expression += f"NTIPAliasClassID['{token.value}']"
        elif token.type == TokenType.NTIPAliasFlag:
            expression += f"NTIPAliasFlag['{token.value}']"
        elif token.type == TokenType.NTIPAliasType:
            expression += f"NTIPAliasType['{token.value}']"
        elif token.type == TokenType.NAME:
            expression += "str(item_data['Item']['NTIPAliasClassID'])"
        elif token.type == TokenType.CLASS:
            expression += "str(item_data['Item']['NTIPAliasClass'])"
        elif token.type == TokenType.QUALITY:
            expression += "str(item_data['NTIPAliasQuality'])"
        elif token.type == TokenType.FLAG:
            if tokens[i + 2].type == TokenType.NTIPAliasFlag: 
                expression += f"str(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
        elif token.type == TokenType._TYPE:
            expression += "str(item_data['Item']['NTIPAliasType'])"
        else:
            expression += f"{token.value}"
        expression += " "
    return expression


txt = "[flag] == ethereal"
lexer = Lexer(txt)
tokens = list(lexer.create_tokens())


expression = transpile(tokens)
print(expression)
# print(eval(expression))
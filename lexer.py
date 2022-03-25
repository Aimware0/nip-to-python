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
  "BaseItem": {
    "DisplayName": "Battle Boots",
    "NTIPAliasClassID": 388,
    "NTIPAliasType": 15,
    "NTIPAliasStatProps": {
      "31": {
        "min": 39,
        "max": 47
      },
      "72": 18,
      "73": 18,
      "0x400000": {
        "min": 0,
        "max": 1
      }
    },
    "dimensions": [
      2,
      2
    ],
    "sets": [
      "ALDURSADVANCE"
    ],
    "uniques": [
      "WARTRAVELER"
    ],
    "NTIPAliasClass": 1
  },
  "Item": {
    "DisplayName": "War Traveler",
    "NTIPAliasClassID": 388,
    "NTIPAliasType": 15,
    "NTIPAliasStatProps": {
      "0": {
        "min": 10,
        "max": 10
      },
      "3": {
        "min": 10,
        "max": 10
      },
      "21": 15,
      "22": 25,
      "72": 30,
      "73": 30,
      "78": {
        "min": 5,
        "max": 10
      },
      "80": {
        "min": 30,
        "max": 50
      },
      "96": {
        "min": 25,
        "max": 25
      },
      "154": {
        "min": 40,
        "max": 40
      },
      "16,0": {
        "min": 150,
        "max": 190
      }
    }
  },
  "NTIPAliasType": 15,
  "NTIPAliasClassID": 388,
  "NTIPAliasClass": null,
  "NTIPAliasQuality": 7,
  "NTIPAliasStat": {
    "0": 10,
    "3": 10,
    "16": 190,
    "21": 15,
    "22": 25,
    "31": 139,
    "72": 13,
    "73": 48,
    "78": 10,
    "80": 50,
    "96": 25,
    "154": 40
  },
  "NTIPAliasFlag": {
    "0x10": true,
    "0x4000000": false
  }
}""")



WHITESPACE = " \t\n\r\v\f"
DIGITS = "0123456789.%"
SYMBOLS = [">", "=> ", "<", "<=", "=", "!", "(", ")", ",", "&", "|", "#", "/"]
MATH_SYMBOLS = ["(", ")", "^", "*", "/", "\\", "+", "-"]
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
                    return Token(TokenType.COMMENT, "") # We don't really need comments in the transpiled version...
            else:
                print("Unknown operator", char)
                break
        
        if char == "#":
            return Token(TokenType.AND, "and")
        elif char == "(":
            return Token(TokenType.LPAREN, char)
        elif char == ")":
            return Token(TokenType.RPAREN, char)

        self.advance()



def transpile(tokens):
    expression = ""
    for i, token in enumerate(tokens):
        if token == None:
            continue
        if token.type == TokenType.NTIPAliasStat:
            if len(tokens) >= 2 and tokens[i + 2].type == TokenType.NUMBERPERCENT: # Look at the other side of the comparsion.
                stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                expression += f"(int(({stat_value} - {stat_min_max}['min']) * 100.0 / ({stat_min_max}['max'] - {stat_min_max}['min'])))"
            else:
                stat_value = f"(item_data['NTIPAliasStat']['{token.value}'])"
                stat_min_max = f"(item_data['Item']['NTIPAliasStatProps']['{token.value}'])"
                # clamp value between min and max
                expression += f"((({stat_value} >= {stat_min_max}['max'] and {stat_min_max}['max']) or ({stat_value} <= {stat_min_max}['min'] and {stat_min_max}['min']) or {stat_value}))"

                expression += f"(int(item_data['NTIPAliasStat']['{token.value}']))"
        elif token.type == TokenType.NTIPAliasClass:
            expression += f"(NTIPAliasClass['{token.value}'])"
        elif token.type == TokenType.NTIPAliasQuality:
            expression += f"(NTIPAliasQuality['{token.value}'])"
        elif token.type == TokenType.NTIPAliasClassID:
            expression += f"(NTIPAliasClassID['{token.value}'])"
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
                expression += f"(item_data['NTIPAliasFlag']['{NTIPAliasFlag[tokens[i + 2].value]}'])"
            # Check if the flag we're looking for (i.e ethereal) is i + 2 away from here, if it is, grab it's value (0x400000) and place it inside the lookup.
        elif token.type == TokenType._TYPE:
            expression += "(int(item_data['NTIPAliasType']))"
        
        elif token.type == TokenType.EQ:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += "=="
        elif token.type == TokenType.NE:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += "!="
        elif token.type == TokenType.GT:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += ">"
        elif token.type == TokenType.LT:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += "<"
        elif token.type == TokenType.GE:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += ">="
        elif token.type == TokenType.LE:
            if tokens[i +1].type != TokenType.NTIPAliasFlag:
                expression += "<="
        elif token.type == TokenType.NUMBERPERCENT:
            expression += f"int({token.value})"
        else:
            expression += f"{token.value}"
            
        expression += "" # add space if spaces are needed
    return expression


txt = "[name] == battleboots && [quality] == unique # [itemmagicbonus] == 50"





lexer = Lexer(txt)
tokens = list(lexer.create_tokens())
# print(tokens)
# print(
#     (int(item_data['NTIPAliasClassID']))==(NTIPAliasClassID['ring'])and(int(item_data['NTIPAliasQuality']))==(NTIPAliasQuality['unique'])and(int(item_data['NTIPAliasStat']['77']))==25.0#
# )

expression = transpile(tokens)
print(expression)
print(eval(expression))
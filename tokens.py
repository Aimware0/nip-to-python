from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    NUMBER =              1
    PLUS =                2
    MINUS =               3
    MULTIPLY =            4
    DIVIDE =              5
    MODULO =              6
    POW =                 7
    LPAREN =              8
    RPAREN =              9
    
    GT =                  10
    LT =                  11
    LE =                  12
    GE =                  13
    EQ =                  14
    NE =                  15
    AND =                16
    OR =                 17

    NTIPAliasClass =     18
    NTIPAliasClassID =   19
    NTIPAliasFlag =      20
    NTIPAliasQuality =   21
    NTIPAliasStat =      22
    NTIPAliasType =      23
    NTIPAlias =          24

    NAME =               32
    FLAG =               33
    QUALITY =            34
    CLASS =              35
    MAXQUANITY =         36
    _TYPE =               37

    WHITESPACE =          38



@dataclass
class Token:
    type: TokenType
    value: any

    def __repr__(self) -> str:
        return f"{self.type} : {self.value}"
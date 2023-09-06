from enum import Enum

class StandardDataType(str, Enum):

    integer = "integer"
    bigint = "bigint"
    float = "float"
    text = "text"
    datetime = "datetime"


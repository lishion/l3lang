from abc import ABC, abstractmethod
from typing import *
import sys

class RegularExpression(ABC):

    def get_inner_expression(self) -> 'RegularExpression': return self

    def get_expression_string(self) -> AnyStr: 
        return self.get_inner_expression().get_expression_string()

    def concat(self, other: 'RegularExpression'):
        return ConcatRegularExpressionOp(self, other)

    def union(self, other: 'RegularExpression'):
        return OrRegularExpressionOp(self, other)

    def __add__(self, other: 'RegularExpression') -> 'RegularExpression': 
        return self.concat(other)

    def __radd__(self, other: 'RegularExpression') -> 'RegularExpression': 
        return other.concat(self)

    def __or__(self, other: 'RegularExpression') -> 'RegularExpression':
        return self.union(other)

    def any_times(self) -> 'RegularExpression': 
        """
            same as the star operation in perl regular expression
        """
        return StarRegularExpressionOp(self)

    def at_least_once(self) -> 'RegularExpression':
        return self + self.any_times()

    @abstractmethod
    def to_nfa_model(self, converter): pass


class BaseRegularExpression(RegularExpression):

    def __init__(self, char: AnyStr) -> None:
        self._char = char

    def get_match_char_index(self) -> int: return ord(self._char)

    def get_match_char(self) -> int: return self._char

    def get_expression_string(self) -> AnyStr: 
        return self._char

    def to_nfa_model(self, converter):
        return converter.convert_base_expression(self)

class EmptyRegularExpression(BaseRegularExpression):
    def __init__(self) -> None:
        super().__init__('')

    def get_match_char_index(self) -> int:
        return None

    def get_expression_string(self) -> AnyStr: 
        return 'ε'

    def to_nfa_model(self, converter):
        return converter.convert_base_expression(self)


class BiRegularExpressionOp(RegularExpression):
    
    def __init__(self, left: RegularExpression, right: RegularExpression) -> None:
        self._left = left
        self._right = right

    @property
    def left(self): return self._left
    
    @property
    def right(self): return self._right


class OrRegularExpressionOp(BiRegularExpressionOp):
    def __init__(self, left, right) -> None:
       super().__init__(left, right)
    
    def get_expression_string(self) -> AnyStr:
        return f"({self._left.get_expression_string()}|{self._right.get_expression_string()})"

    def to_nfa_model(self, converter):
        return converter.convert_or_expression(self)

class ConcatRegularExpressionOp(BiRegularExpressionOp):
    def __init__(self, left, right) -> None:
        super().__init__(left, right)
    
    def get_expression_string(self) -> AnyStr:
        return f"(({self._left.get_expression_string()})({(self._right.get_expression_string())}))"

    def to_nfa_model(self, converter):
        return converter.convert_concat_expression(self)

class BatchRegularExpression(RegularExpression):
    def __init__(self, chars) -> None:
        super().__init__()
        self._chars = chars

    def get_match_chars(self):
        yield from self._chars


class BatchOrRegularExpression(BatchRegularExpression):
    def __init__(self, chars) -> None:
        super().__init__(chars)

    def to_nfa_model(self, converter):
        return converter.convert_batch_or_expression(self)
    
    def get_expression_string(self) -> AnyStr:
        return f"({'|'.join(self._chars)})"

class RangeRegularExpression(BatchOrRegularExpression):
    def __init__(self, left, right) -> None:
        super().__init__([chr(index) for index in range(ord(left), ord(right) + 1)])
        self._left = left
        self._right = right

    def get_expression_string(self) -> AnyStr:
        return f"[{self._left}, {self._right}]"

class LiteralRegularExpression(BatchRegularExpression):
    def __init__(self, chars) -> None:
        super().__init__(chars)

    def to_nfa_model(self, converter):
        return converter.convert_literal_expression(self)

    def get_expression_string(self) -> AnyStr:
        return self._chars

class StarRegularExpressionOp(RegularExpression):
    def __init__(self, inner: RegularExpression) -> None:
        self._inner = inner
    
    def get_inner_expression(self) -> 'RegularExpression':
        return self._inner

    def get_expression_string(self) -> AnyStr:
        return f"({self._inner.get_expression_string()})*"
    
    def to_nfa_model(self, converter):
        return converter.convert_star_expression(self)

class FunctionRegularExpression(RegularExpression):
    def __init__(self, predictor) -> None:
        super().__init__()
        self._predictor = predictor
        all_chars = (chr(i) for i in range(0, 65535 + 1))
        accepted_chars = (char for char in all_chars if self._predictor(char))
        self._inner_expression = BatchOrRegularExpression(accepted_chars)
    
    def to_nfa_model(self, converter):
        return converter.convert_batch_or_expression(self._inner_expression)

    def get_expression_string(self) -> AnyStr:
        return "by function"


class RE:
    EMPTY = EmptyRegularExpression()

    @staticmethod
    def char(char) -> RegularExpression:
        return BaseRegularExpression(char)
    
    @staticmethod
    def chars(*chars) -> RegularExpression:
        return BatchOrRegularExpression(chars)

    @staticmethod
    def range(start, end) -> RegularExpression:
        return RangeRegularExpression(start, end)

    @staticmethod
    def literal(string) -> RegularExpression:
        return LiteralRegularExpression(string)

    @staticmethod
    def cal_by(predictor) -> RegularExpression:
        return FunctionRegularExpression(predictor)
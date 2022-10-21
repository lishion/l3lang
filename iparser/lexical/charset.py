from abc import ABC, abstractmethod
from typing import *

class CharSetManager(ABC):

    @abstractmethod
    def all_chars(self) -> Collection[int]: pass

    @abstractmethod
    def all_char_ids(self) -> Collection[int]: 
        yield from (self.char_to_index(char) for char in self.all_chars())

    @abstractmethod
    def char_num(self) -> int: pass

    @abstractmethod
    def char_to_index(self, char) -> int: pass

class ASCIICharSetManager(CharSetManager):
    
    def __init__(self) -> None:
        super().__init__()
    
    def all_chars(self) -> Collection[int]:
        return super().all_chars()
    
    def char_num(self) -> int:
        return 128
    
    def char_to_index(self, char) -> int:
        return ord(char)
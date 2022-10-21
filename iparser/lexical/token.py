from iparser.lexical.regular_expression import RegularExpression
from iparser.lexical.nfa_model import NFAModel
from iparser.lexical.nfa_model_converter import NFAModelConverter
from abc import ABC, abstractmethod
from typing import List

class Token:
    def __init__(self, token_index, name, value) -> None:
        self.token_index = token_index
        self.value = value
        self.name = name
    
    def __repr__(self) -> str:
        return f"{self.name} -> '{self.value}'"

    def __str__(self) -> str:
        return self.__repr__()

class TokenDefinition(ABC):

    def __init__(self, name) -> None:
        super().__init__()
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_nfa_model(self) -> NFAModel: pass


class RETokenDefinition(TokenDefinition):
    def __init__(self, name, re: RegularExpression, converter) -> None:
        super().__init__(name)
        self._re = re
        self._converter = converter
    
    def get_nfa_model(self) -> NFAModel:
        return self._re.to_nfa_model(self._converter)


class ReTokenDefinitions:
    def __init__(self, converter: NFAModelConverter) -> None:
        self._definitions: List[TokenDefinition] = []
        self._models: List[NFAModel] = []
        self._converter = converter
    
    def define(self, name: str, re: RegularExpression):
        definition = RETokenDefinition(name, re, self._converter)
        model = definition.get_nfa_model()
        token_index = len(self._definitions)
        self._definitions.append(definition)
        model.tail_state.token_index = token_index
        self._models.append(model)
    
    def get_token_definition(self, index):
        return self._definitions[index]
    
    @property
    def models(self) -> List[NFAModel]:
        return self._models
    
    @property
    def definitions(self) -> List[TokenDefinition]:
        return self._definitions

        
    
from iparser.lexical.charset import CharSetManager
from iparser.lexical.nfa_model import NFAModel, NFAState
from iparser.lexical.regular_expression import RE
from iparser.lexical.token import ReTokenDefinitions, Token
from abc import ABC, abstractmethod
from typing import AnyStr, Iterable, Tuple
from iparser.lexical.dfa_model import DFAModel
from iparser.lexical.fsa import FiniteStateMachine

class Reader(ABC):
    EOF = -1
    @abstractmethod
    def head(self) -> AnyStr: pass

    @abstractmethod
    def peek(self) -> AnyStr: pass

    @abstractmethod
    def position(self) -> Tuple[int, int]: pass

class StringReader(Reader):

    def __init__(self, string) -> None:
        super().__init__()
        self._string = string
        self._index = 0
        self._max_index = len(self._string)

    def head(self) -> int:
        if self._index < self._max_index:
            return ord(self._string[self._index])
        return Reader.EOF
    
    def peek(self) -> int:
        if self._index < self._max_index:
            c = ord(self._string[self._index])
            self._index += 1
            return c
        return Reader.EOF

    def position(self) -> Tuple[int, int]:
        return 0, self._index

class Scanner:  
    def __init__(self, reader: Reader, definitions: ReTokenDefinitions) -> None:
        self._definitions = definitions
        self._reader = reader
        self._dfa_model = None
        self._fsa = None
        self.init()
      
    def init(self):
        init_state = NFAState()
        tail_state = NFAState()
        nfa_model = NFAModel(init_state, tail_state)
        for model in self._definitions.models:
            init_state.epsilon_move_to(model.init_state)
            model.tail_state.epsilon_move_to(tail_state)
            nfa_model.add_state(*model.states)
        self._dfa_model = DFAModel(nfa_model)
        self._dfa_model.init()
        self._fsa = FiniteStateMachine(self._dfa_model.transition_table, self._dfa_model.accept_table)

    def token_stream(self) -> Iterable[Token]:
        token_value_builder = []
        print(self._dfa_model.accept_table)
        while True:
            char = self._reader.head()
            # print(self._fsa.current_state, chr(char), '->')
            self._fsa.input(char)
            char != Reader.EOF and (not self._fsa.stop()) and token_value_builder.append(chr(char))
            # print(self._fsa.current_state)
            if self._fsa.stop():
                # print(self._fsa.last_state)
                token_value = ''.join(token_value_builder)
                last_accept_index = self._dfa_model.accept_table[self._fsa.last_state]
                if last_accept_index == -1:
                    raise Exception(f"error token: {token_value}")
                else:
                    yield Token(last_accept_index, self._definitions.get_token_definition(last_accept_index).name, token_value)
                if char == Reader.EOF:
                    return
                token_value_builder.clear()
                self._fsa.reset()
            else:
                self._reader.peek()

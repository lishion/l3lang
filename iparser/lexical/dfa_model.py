from typing import *
from iparser.lexical import regular_expression
from iparser.lexical.charset import CharSetManager
from iparser.lexical.nfa_model import NFAModel, NFAState, NFAEdge
from collections import defaultdict
import time


class DFAState:
    def __init__(self, token_index=-1) -> None:
        self._token_index = token_index
        self._out_edges: List[DFAState] = []
        self.nfa_state_ids: Set[int] = set()
        self.nfa_states: Set[NFAState] = set()
        self._state_index = -1
        self.signature: Tuple[int] = None

    @property
    def out_edges(self) -> List['DFAEdge']: return self._out_edges

    def add_edge(self, edge: 'DFAState'):
        self._out_edges.append(edge)

    @property
    def state_index(self):
        return self._state_index
    
    @state_index.setter
    def state_index(self, state_index):
        self._state_index = state_index

    @property
    def token_index(self): return self._token_index

    @token_index.setter
    def token_index(self, index): 
        self._token_index = index
    
    def convert_to(self, symbol: int, dfa_state) -> None:
        self.add_edge(DFAEdge(symbol, dfa_state))

    def set_nfa_states(self, nfa_states: Collection[NFAState], signature):
        self.nfa_states = nfa_states
        self.signature = signature


class DFAEdge:
    def __init__(self, symbol: int=None, state: DFAState=None) -> None:
        self._symbol = symbol
        self._linked_state = state

    @property
    def symbol(self) -> int: return self._symbol

    @property
    def linked_state(self) -> DFAState: return self._linked_state

    def link_to(self, state: DFAState): self._linked_state = state

class DFAModel:
    def __init__(self, nfa_model: NFAModel) -> None:
        self._init_state = None
        self._nfa_model = nfa_model
        self._states: Dict[Tuple[int], DFAState] = {}
        self._transition_table = None
        self._accept_table = []
        self._all_symbols: Set[int] = set()
        self._closure_cache: Dict[NFAState, List[Set]] = {}

    def init(self):
        self._build_model()
        self._build_transition_table()

    @property
    def accept_table(self): return self._accept_table

    @property
    def transition_table(self): return self._transition_table

    @property
    def init_state(self): return self._init_state

    @init_state.setter
    def init_state(self, state: DFAState): 
        self._init_state = state
    
    def _get_closure(self, *states: NFAState) -> Set[NFAState]:
        closure = set()

        def helper(state: NFAState, res: Set[NFAState]):
            if state in res:
                return
            res.add(state)
            for next_state in state.can_epsilon_move_states():
                helper(next_state, res)

        for state in states:
            if state not in self._closure_cache:
                res = set()
                helper(state, res)
                self._closure_cache[state] = res
            closure.update(self._closure_cache[state])
        return closure

    # closure(move(T, symbol))
    def _move_and_closure(self, nfa_states: Collection[NFAState], symbol: int) -> Collection[NFAState]:
        new_states = set()
        for state in nfa_states:
            new_states.update(state.linked_state_lookup[symbol])
        return self._get_closure(*new_states)

    def _get_accept_state(self, nfa_states: Collection[NFAState]):
        accept_states = list(sorted((state for state in nfa_states if state._token_index != -1), key=lambda s: s.token_index))
        return accept_states and accept_states[0] or None

    def _create_dfa_state(self, nfa_states: Collection[NFAState], signature):
        dfa_state = DFAState()
        accept_state = self._get_accept_state(nfa_states)
        dfa_state.token_index = accept_state.token_index if accept_state else -1
        self._states[signature] = dfa_state
        dfa_state.state_index = len(self._states)
        dfa_state.set_nfa_states(nfa_states, signature)
        return dfa_state

    def _cal_signature(self, nfa_states: Collection[NFAState]):
        return tuple(set((state.state_index for state in nfa_states)))

    def _build_model(self):
        start_nfa_states = self._get_closure(self._nfa_model.init_state)
        self._init_state = self._create_dfa_state(start_nfa_states, self._cal_signature(start_nfa_states))
        wait_move_states: List[DFAState] = [self._init_state]
        while True and wait_move_states:
            source_state = wait_move_states.pop()
            valid_inputs = set()
            for state in source_state.nfa_states:
                v = state.valid_inputs()
                valid_inputs.update(v)
                self._all_symbols.update(v)
            print(source_state.signature, valid_inputs)
            for symbol in valid_inputs:
                new_nfa_states = self._move_and_closure(source_state.nfa_states, symbol)
                if not new_nfa_states:
                    continue
                signature = tuple(set((state.state_index for state in new_nfa_states)))
                # print(source_state.signature, symbol, signature)
                existed_state = self._states.get(signature)
                if existed_state:
                    source_state.convert_to(symbol, existed_state)
                else:
                    new_state = self._create_dfa_state(new_nfa_states, signature)
                    source_state.convert_to(symbol, new_state)
                    wait_move_states.append(new_state)
    
    def _build_transition_table(self):
        max_symbol = max(self._all_symbols) + 1
        transition_table = [[0] * max_symbol for _ in range(0, len(self._states) + 1)]
        accept_table = [-1] * len(transition_table)
        visited = set()

        def helper(state: DFAState):
            if state.state_index in visited:
                return
            visited.add(state.state_index)
            accept_table[state.state_index] = state.token_index
            for edge in state.out_edges:
                transition_table[state.state_index][edge.symbol] = edge.linked_state.state_index
                helper(edge.linked_state)

        helper(self._init_state)
        self._transition_table = transition_table
        self._accept_table = accept_table

from typing import *
from collections import defaultdict


class NFAState:
    def __init__(self, token_index=-1) -> None:
        self._token_index = token_index
        self._out_edges: List[NFAEdge] = []
        self.state_index = -1
        self.linked_state_lookup: Dict[int, List[NFAState]] = defaultdict(list)

    def valid_inputs(self) -> Set[int]: return set(self.linked_state_lookup.keys())
        
    @property
    def out_edges(self) -> List['NFAEdge']: return self._out_edges

    def can_epsilon_move_states(self) -> List['NFAState']: return self.linked_state_lookup.get(None, set())

    def linked_state_lookup(self) -> Dict[int, List['NFAState']]: return self._linked_state_lookup

    def add_edge(self, edge: 'NFAEdge'):
        self.linked_state_lookup[edge.symbol].append(edge.linked_state)
        self._out_edges.append(edge)

    def move_to(self, symbol: int, state: 'NFAState'):
        self.add_edge(NFAEdge(symbol, state))

    def epsilon_move_to(self, state: 'NFAState'):
        self.add_edge(NFAEdge(None, state))

    @property
    def token_index(self): return self._token_index

    @token_index.setter
    def token_index(self, index): 
        self._token_index = index

    def __eq__(self, other: 'NFAState'):
        return self.state_index == other.state_index

    def __hash__(self):
        return self.state_index.__hash__()


class NFAEdge:
    def __init__(self, symbol: int=None, state: NFAState=None) -> None:
        self._symbol = symbol
        self._linked_state = state

    @property
    def symbol(self) -> int: return self._symbol

    @property
    def linked_state(self) -> NFAState: return self._linked_state

    def link_to(self, state: NFAState): self._linked_state = state


class NFAModel:
    def __init__(self, init_state: NFAEdge=None, tail_state: NFAState=None) -> None:
        self._states: List[NFAState] = []
        self._init_state = init_state
        self._tail_state = tail_state
        self.add_state(self._init_state)
        self.add_state(self._tail_state)

    @property
    def init_state(self): 
        return self._init_state

    @init_state.setter
    def init_state(self, state: NFAState): 
        self.add_state(state)
        self._init_state = state

    @property
    def tail_state(self): return self._tail_state

    @tail_state.setter
    def tail_state(self, tail_state: NFAState):
        self.add_state(tail_state)
        self._tail_state = tail_state
    
    @property
    def states(self) -> List[NFAState]:
        return self._states

    def add_state(self, *states: NFAState):
        """
            add state to this model and assign index to it
        """
        for state in states:
            state.state_index = len(self._states)
            self._states.append(state)
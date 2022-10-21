class FiniteStateMachine:
    def __init__(self, transition_table, accept_table):
        self._transition_table = transition_table
        self._accept_table = accept_table
        self._current_state = 1
        self._last_state = None

    def input(self, symbol):
        now_state = self._transition_table[self._current_state][symbol]
        accept_state = self._accept_table[self._current_state]
        self._last_state = self._current_state
        self._current_state = now_state
        return accept_state

    @property
    def current_state(self): return self._current_state

    @property
    def last_state(self): return self._last_state

    def stop(self):
        return self._current_state == 0
    
    def reset(self):
        self._current_state = 1
        self._last_state = None
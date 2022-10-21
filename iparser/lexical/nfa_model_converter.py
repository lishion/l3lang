from iparser.lexical.regular_expression import BaseRegularExpression, \
    ConcatRegularExpressionOp, OrRegularExpressionOp, \
    BatchOrRegularExpression, StarRegularExpressionOp
from iparser.lexical.nfa_model import NFAState, NFAModel


class NFAModelConverter:

    def _char_to_index(self, char):
        return ord(char) if char else None

    def convert_base_expression(self, expression: BaseRegularExpression):
        init_state = NFAState()
        tail_state = NFAState()
        init_state.move_to(self._char_to_index(expression.get_match_char()), tail_state)
        model = NFAModel(init_state, tail_state)
        return model

    def convert_or_expression(self, expression: OrRegularExpressionOp) -> NFAModel:
        left_model = expression.left.to_nfa_model(self)
        right_model = expression.right.to_nfa_model(self)

        init_state = NFAState()
        init_state.epsilon_move_to(left_model.init_state)
        init_state.epsilon_move_to(right_model.init_state)

        tail_state = NFAState()
        left_model.tail_state.epsilon_move_to(tail_state)
        right_model.tail_state.epsilon_move_to(tail_state)

        new_model = NFAModel(init_state, tail_state)
        new_model.add_state(*left_model.states)
        new_model.add_state(*right_model.states)
        return new_model
    
    def convert_concat_expression(self, expression: ConcatRegularExpressionOp) -> NFAModel:
        left_model = expression.left.to_nfa_model(self)
        right_model = expression.right.to_nfa_model(self)
        new_model = NFAModel(left_model.init_state, right_model.tail_state)
        left_model.tail_state.epsilon_move_to(right_model.init_state)
        new_model.add_state(*left_model.states)
        new_model.add_state(*right_model.states)
        return new_model
    
    def convert_star_expression(self, expression: StarRegularExpressionOp):
        inner_model = expression.get_inner_expression().to_nfa_model(self)
        init_state = NFAState()
        tail_state = NFAState()
        init_state.epsilon_move_to(tail_state)
        tail_state.epsilon_move_to(init_state)
        init_state.epsilon_move_to(inner_model.init_state)
        inner_model.tail_state.epsilon_move_to(tail_state)
        new_model = NFAModel(init_state, tail_state)
        new_model.add_state(*inner_model.states)
        return new_model
    
    def convert_batch_or_expression(self, expression: BatchOrRegularExpression): 
        init_state = NFAState()
        tail_state = NFAState()
        model = NFAModel(init_state, tail_state)
        for char in expression.get_match_chars():
            target_state = NFAState()
            target_state.epsilon_move_to(tail_state)
            init_state.move_to(self._char_to_index(char), target_state)
            model.add_state(target_state)
        return model

    def convert_literal_expression(self, expression: BatchOrRegularExpression):
        init_state = NFAState()
        end_state = NFAState()
        state = init_state
        model = NFAModel(init_state, end_state)
        for char in expression.get_match_chars():
            target_state = NFAState()
            state.move_to(self._char_to_index(char), target_state)
            model.add_state(target_state)
            state = target_state
        state.epsilon_move_to(end_state)
        return model
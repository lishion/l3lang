from iparser.lexical import charset
from iparser.lexical.nfa_model import NFAModel, NFAState, NFAEdge
from iparser.lexical.dfa_model import DFAModel
from iparser.lexical.charset import ASCIICharSetManager
from iparser.lexical.regular_expression import RE, StarRegularExpressionOp
from iparser.lexical.fsa import FiniteStateMachine
from iparser.lexical.nfa_model_converter import NFAModelConverter
from iparser.lexical.charset import ASCIICharSetManager
from iparser.lexical.token import ReTokenDefinitions
from iparser.lexical.scanner import StringReader, Scanner
import unicodedata

def test_match(fsa: FiniteStateMachine, string: str):
    fsa.reset()
    for i, c in enumerate(string):
        accept = fsa.input(ord(c))
        if fsa.stop() and accept == -1:
            return False
    accept = fsa.input(0)
    if fsa.stop() and accept == -1:
        return False
    return True

def is_letter(char):
    return unicodedata.category(char) in {"Lu", "Ll", "Lt", "Lm", "Lo"}

def is_number(char):
    return unicodedata.category(char) == "Nd"

if __name__ == "__main__":
    # nfa_state0 = NFAState()
    # nfa_state1 = NFAState()
    # nfa_state2 = NFAState()
    # nfa_state3 = NFAState()
    # nfa_state4 = NFAState()
    # nfa_model = NFAModel(nfa_state0, nfa_state4)
    # nfa_state0.epsilon_move_to(nfa_state1)
    # nfa_state1.move_to(1, nfa_state2)
    # nfa_state1.move_to(1, nfa_state3)
    # nfa_state2.move_to(2, nfa_state4)
    # nfa_state3.move_to(3, nfa_state4)
    # nfa_model.add_state(nfa_state0, nfa_state1, nfa_state2, nfa_state3, nfa_state4)
    # dfa_model = DFAModel(nfa_model, ASCIICharSetManager())
    # dfa_model.init()
    # print(dfa_model.transition_table)
    # re = RE.literal("我就说几句")
    # nfa_model: NFAModel = re.to_nfa_model(NFAModelConverter())
    # nfa_model.tail_state.token_index = 2
    # dfa_model = DFAModel(nfa_model)
    # dfa_model.init()
    # fsa = FiniteStateMachine(dfa_model.transition_table, dfa_model.accept_table)
    # print(test_match(fsa, "我就说几句"))
    # print(test_match(fsa, "1234aaa"))
    # print(test_match(fsa, "我aaa1"))

    

    # dfa_model = DFAModel(nfa_model, charset_manager)
    # dfa_model.init()
    # print(dfa_model.accept_table)
    # fsa = FiniteStateMachine(dfa_model.transition_table, dfa_model.accept_table)
    # print(test_match(fsa, "if"))
    # print(test_match(fsa, "aa123"))

    definitions = ReTokenDefinitions(NFAModelConverter())
    # definitions.define("IF", RE.literal("若"))
    # definitions.define("EQUAL", RE.literal("等于"))
    # definitions.define("ASSIGN", RE.char("为"))
    # definitions.define("LEFT", RE.char("("))
    # definitions.define("RIGHT", RE.char(")"))
    definitions.define("ID", (RE.cal_by(is_letter) | RE.char("_")) + (RE.cal_by(is_letter) | RE.cal_by(is_number) | RE.char("_")).any_times())
    # definitions.define("BLANK", RE.char(" ").at_least_once())
    # definitions.define("NUMBER", RE.range('0', '9'))
    # definitions.define("ID", RE.cal_by(is_letter))
    reader = StringReader("if(姓名==name) a = b c=1000")
    scanner = Scanner(reader, definitions)
    for token in scanner.token_stream():
        print(token)


    

class NFA:
    def __init__(self, start, accept, transitions):
        self.start = start              # start state
        self.accept = accept            # accept state
        self.transitions = transitions  # dict: state → [(symbol, next_state)]

state_counter = 0

def new_state():
    global state_counter
    s = state_counter
    state_counter += 1
    return s



def add_transition(transitions, src, symbol, dest):
    if src not in transitions:
        transitions[src] = []
    transitions[src].append((symbol, dest))



def merge(t1, t2):
    result = {}

    for k, v in t1.items():
        result[k] = v.copy()

    for k, v in t2.items():
        if k in result:
            result[k].extend(v)
        else:
            result[k] = v.copy()

    return result


def build_char_nfa(char):
    start = new_state()
    end = new_state()
    transitions = {}
    add_transition(transitions, start, char, end)
    return NFA(start, end, transitions)

def concat_nfa(nfa1, nfa2):
    transitions = merge(nfa1.transitions, nfa2.transitions)

    add_transition(transitions, nfa1.accept, 'EPS', nfa2.start)

    return NFA(nfa1.start, nfa2.accept, transitions)



def union_nfa(nfa1, nfa2):
    start = new_state()
    end = new_state()

    transitions = merge(nfa1.transitions, nfa2.transitions)

    add_transition(transitions, start, 'EPS', nfa1.start)
    add_transition(transitions, start, 'EPS', nfa2.start)
    add_transition(transitions, nfa1.accept, 'EPS', end)
    add_transition(transitions, nfa2.accept, 'EPS', end)

    return NFA(start, end, transitions)



def star_nfa(nfa):
    start = new_state()
    end = new_state()

    transitions = merge(nfa.transitions, {})

    add_transition(transitions, start, 'EPS', nfa.start)
    add_transition(transitions, start, 'EPS', end)
    add_transition(transitions, nfa.accept, 'EPS', nfa.start)
    add_transition(transitions, nfa.accept, 'EPS', end)

    return NFA(start, end, transitions)


def plus_nfa(nfa):
    start = new_state()
    end = new_state()

    transitions = merge(nfa.transitions, {})

    add_transition(transitions, start, 'EPS', nfa.start)
    add_transition(transitions, nfa.accept, 'EPS', nfa.start)
    add_transition(transitions, nfa.accept, 'EPS', end)

    return NFA(start, end, transitions)


def qmark_nfa(nfa):
    start = new_state()
    end = new_state()

    transitions = merge(nfa.transitions, {})

    add_transition(transitions, start, 'EPS', nfa.start)
    add_transition(transitions, start, 'EPS', end)
    add_transition(transitions, nfa.accept, 'EPS', end)

    return NFA(start, end, transitions)


def postfix_to_nfa(postfix_tokens):
    stack = []

    for token_type, value in postfix_tokens:

        if token_type == 'CHAR':
            stack.append(build_char_nfa(value))

        elif token_type == 'CONCAT':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concat_nfa(nfa1, nfa2))

        elif token_type == 'UNION':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(union_nfa(nfa1, nfa2))

        elif token_type == 'STAR':
            nfa = stack.pop()
            stack.append(star_nfa(nfa))

        elif token_type == 'PLUS':
            nfa = stack.pop()
            stack.append(plus_nfa(nfa))

        elif token_type == 'QMARK':
            nfa = stack.pop()
            stack.append(qmark_nfa(nfa))

    return stack.pop()



from regex_parser import parse

regex = "(a|b)*ab"
postfix = parse(regex)

nfa = postfix_to_nfa(postfix)

print("Start:", nfa.start)
print("Accept:", nfa.accept)
print("Transitions:")
for state, trans in nfa.transitions.items():
    for symbol, dest in trans:
        print(f"{state} --{symbol}--> {dest}")


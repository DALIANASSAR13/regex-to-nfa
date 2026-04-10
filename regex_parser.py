# انواع التوكين الا تي نستخدمها
CHAR   = 'CHAR'    # any letter, digit, or '.' wildcard
CONCAT = 'CONCAT'  # · (we add this ourselves)
UNION  = 'UNION'   # |
STAR   = 'STAR'    # *
PLUS   = 'PLUS'    # +
QMARK  = 'QMARK'   # ?
LPAREN = 'LPAREN'  # (
RPAREN = 'RPAREN'  # )
#who come first? STAR, PLUS, QMARK or CONCAT? STAR, PLUS, QMARK have higher precedence than CONCAT, and UNION has the lowest precedence. So we can assign precedence values accordingly.
PRECEDENCE = {
    UNION:  1,
    CONCAT: 2,
    STAR:   3,
    PLUS:   3,
    QMARK:  3,
}
#validate the regux 
def validate(regex):

    if not regex:
        raise ValueError("Regex cannot be empty.")
    # allowed chars
    allowed = set('abcdefghijklmnopqrstuvwxyz'
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                  '0123456789'
                  '|*+?().')

    for i, ch in enumerate(regex):
        if ch not in allowed:
            raise ValueError(f"Invalid character '{ch}' at position {i}.")

    depth = 0
    for i, ch in enumerate(regex):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if depth < 0:
            raise ValueError(f"Unexpected ')' at position {i}.")
    if depth != 0:
        raise ValueError("Missing closing ')'.")

    if '()' in regex:
        raise ValueError("Empty group '()' is not allowed.")

    for i, ch in enumerate(regex):
        if ch == '|':
            if i == 0 or i == len(regex) - 1:
                raise ValueError(f"'|' at position {i} is missing an operand.")
            if regex[i - 1] in '|(':
                raise ValueError(f"'|' at position {i} is missing a left operand.")

    for i, ch in enumerate(regex):
        if ch in '*+?':
            if i == 0:
                raise ValueError(f"'{ch}' at position {i} has nothing to apply to.")
            if regex[i - 1] in '(|':
                raise ValueError(f"'{ch}' at position {i} has nothing to apply to.")
#convert to tokens
def tokenize(regex):

    tokens = []

    for ch in regex:
        if   ch == '|': tokens.append((UNION,  ch))
        elif ch == '*': tokens.append((STAR,   ch))
        elif ch == '+': tokens.append((PLUS,   ch))
        elif ch == '?': tokens.append((QMARK,  ch))
        elif ch == '(': tokens.append((LPAREN, ch))
        elif ch == ')': tokens.append((RPAREN, ch))
        else:           tokens.append((CHAR,   ch))  

    return tokens
#insert CONCAT tokens where needed. For example, "ab" becomes "a·b", and "a(b|c)" becomes "a·(b|c)".
def insert_concat(tokens):

    result = []

    for i, token in enumerate(tokens):
        result.append(token)

        if i + 1 < len(tokens):
            left  = token[0]
            right = tokens[i + 1][0]

            left_ends    = {CHAR, STAR, PLUS, QMARK, RPAREN}
            right_starts = {CHAR, LPAREN}

            if left in left_ends and right in right_starts:
                result.append((CONCAT, '·'))

    return result

# Convert infix tokens to postfix using the Shunting Yard algorithm. For example, "a|b" becomes "ab|", and "ab*" becomes "ab*·".
def to_postfix(tokens):

    output = []  
    stack  = []  

    for token in tokens:
        t_type = token[0]

        if t_type == CHAR:
            output.append(token)

        elif t_type in (STAR, PLUS, QMARK, UNION, CONCAT):
            while (stack and
                   stack[-1][0] != LPAREN and
                   PRECEDENCE.get(stack[-1][0], 0) >= PRECEDENCE.get(t_type, 0)):
                output.append(stack.pop())
            stack.append(token)

        elif t_type == LPAREN:
            stack.append(token)

        elif t_type == RPAREN:
            while stack and stack[-1][0] != LPAREN:
                output.append(stack.pop())
            stack.pop()  

    while stack:
        output.append(stack.pop())

    return output
# Main function to parse a regex string into postfix tokens.
def parse(regex):
    """
    Takes a raw regex string.
    Returns a postfix list of (type, value) tuples.

    Example:
        parse("a|b")  ->  [('CHAR','a'), ('CHAR','b'), ('UNION','|')]
        parse("ab*")  ->  [('CHAR','a'), ('CHAR','b'), ('STAR','*'), ('CONCAT','·')]

    Raises ValueError if the regex is invalid.
    """
    validate(regex)
    tokens = tokenize(regex)
    tokens = insert_concat(tokens)
    tokens = to_postfix(tokens)
    return tokens


def add_concatenation(regex):
    """Insert explicit concatenation dots into a regex."""
    result = ""

    for i, char in enumerate(regex):
        result += char

        if i + 1 < len(regex):
            next_char = regex[i + 1]

            if (
                (char.isalnum() or char == ")" or char == "*")
                and (next_char.isalnum() or next_char == "(")
            ):
                result += "."

    return result


def to_postfix(regex):
    """Convert a basic infix regex to postfix notation."""
    regex = add_concatenation(regex)

    precedence = {"|": 1, ".": 2}
    output = []
    operators = []

    if not regex:
        raise ValueError("Regular expression cannot be empty")

    for char in regex:
        if char.isalnum():
            output.append(char)

        elif char == "(":
            operators.append(char)

        elif char == ")":
            while operators and operators[-1] != "(":
                output.append(operators.pop())

            if not operators:
                raise ValueError("Mismatched parentheses")

            operators.pop()

        elif char in precedence:
            while (
                operators
                and operators[-1] != "("
                and precedence[operators[-1]] >= precedence[char]
            ):
                output.append(operators.pop())

            operators.append(char)

        elif char == "*":
            output.append(char)

        else:
            raise ValueError(f"Unsupported character: {char}")

    if "(" in operators:
        raise ValueError("Mismatched parentheses")

    while operators:
        output.append(operators.pop())

    return "".join(output)


if __name__ == "__main__":
    regex = input("Enter a regular expression: ")

    try:
        print("With concatenation:", add_concatenation(regex))
        print("Postfix:", to_postfix(regex))
    except ValueError as error:
        print("Error:", error)


from dataclasses import dataclass


@dataclass
class NFA:
    start: int
    accept: int
    transitions: dict


class ThompsonBuilder:
    def __init__(self):
        self.next_state = 0
        self.transitions = {}

    def new_state(self):
        state = self.next_state
        self.next_state += 1
        self.transitions[state] = []
        return state

    def add_transition(self, source, symbol, destination):
        self.transitions[source].append((symbol, destination))

    def build(self, postfix):
        stack = []

        for char in postfix:
            if char.isalnum():
                start = self.new_state()
                accept = self.new_state()
                self.add_transition(start, char, accept)
                stack.append((start, accept))

            elif char == ".":
                if len(stack) < 2:
                    raise ValueError("Invalid concatenation")

                b_start, b_accept = stack.pop()
                a_start, a_accept = stack.pop()

                self.add_transition(a_accept, "ε", b_start)
                stack.append((a_start, b_accept))

            elif char == "|":
                if len(stack) < 2:
                    raise ValueError("Invalid union")

                b_start, b_accept = stack.pop()
                a_start, a_accept = stack.pop()

                start = self.new_state()
                accept = self.new_state()

                self.add_transition(start, "ε", a_start)
                self.add_transition(start, "ε", b_start)
                self.add_transition(a_accept, "ε", accept)
                self.add_transition(b_accept, "ε", accept)

                stack.append((start, accept))

            elif char == "*":
                if not stack:
                    raise ValueError("Invalid Kleene star")

                old_start, old_accept = stack.pop()

                start = self.new_state()
                accept = self.new_state()

                self.add_transition(start, "ε", old_start)
                self.add_transition(start, "ε", accept)
                self.add_transition(old_accept, "ε", old_start)
                self.add_transition(old_accept, "ε", accept)

                stack.append((start, accept))

            else:
                raise ValueError(
                    f"Unsupported postfix symbol: {char}"
                )

        if len(stack) != 1:
            raise ValueError("Invalid regular expression")

        start, accept = stack.pop()

        return NFA(start, accept, self.transitions)


def print_nfa(nfa):
    print("\nNFA Start State:", f"q{nfa.start}")
    print("NFA Accepting State:", f"q{nfa.accept}")
    print("\nNFA Transitions:")

    for source, edges in nfa.transitions.items():
        for symbol, destination in edges:
            print(f"q{source} --{symbol}--> q{destination}")


if __name__ == "__main__":
    from regex_parser import to_postfix

    regex = input("Enter a regular expression: ")

    try:
        postfix = to_postfix(regex)
        nfa = ThompsonBuilder().build(postfix)

        print("Postfix:", postfix)
        print_nfa(nfa)

    except ValueError as error:
        print("Error:", error)

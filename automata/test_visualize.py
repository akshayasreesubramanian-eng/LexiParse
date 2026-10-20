
from regex_parser import to_postfix
from nfa import ThompsonBuilder
from dfa import nfa_to_dfa
from visualize import draw_nfa, draw_dfa


def main():
    regex = input("Enter regex: ")

    try:
        postfix = to_postfix(regex)
        nfa = ThompsonBuilder().build(postfix)

        alphabet = sorted({
            symbol
            for edges in nfa.transitions.values()
            for symbol, _ in edges
            if symbol != "ε"
        })

        if not alphabet:
            raise ValueError("Regex must contain at least one symbol")

        states, transitions, accepting = nfa_to_dfa(
            nfa, alphabet
        )

        draw_nfa(nfa, "nfa")
        draw_dfa(
            states, transitions, accepting, alphabet, "dfa"
        )

        print("\nPostfix:", postfix)
        print("NFA and DFA diagrams generated successfully.")

    except ValueError as error:
        print(f"\nInvalid regular expression: {error}")


if __name__ == "__main__":
    main()

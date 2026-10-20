
from collections import deque

from nfa import ThompsonBuilder
from regex_parser import to_postfix


def epsilon_closure(states, transitions):
    """Find all states reachable through epsilon transitions."""
    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()

        for symbol, destination in transitions[state]:
            if symbol == "ε" and destination not in closure:
                closure.add(destination)
                stack.append(destination)

    return frozenset(closure)


def move(states, symbol, transitions):
    """Find NFA states reachable using a given symbol."""
    result = set()

    for state in states:
        for edge_symbol, destination in transitions[state]:
            if edge_symbol == symbol:
                result.add(destination)

    return result


def nfa_to_dfa(nfa, alphabet):
    """Convert an NFA into a complete DFA using subset construction."""
    start = epsilon_closure({nfa.start}, nfa.transitions)

    dfa_states = [start]
    state_ids = {start: 0}
    dfa_transitions = {}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        current_id = state_ids[current]
        dfa_transitions[current_id] = {}

        for symbol in alphabet:
            destinations = move(
                current, symbol, nfa.transitions
            )

            target = epsilon_closure(
                destinations, nfa.transitions
            )

            # Include the empty set as a dead state when necessary.
            if target not in state_ids:
                state_ids[target] = len(dfa_states)
                dfa_states.append(target)
                queue.append(target)

            dfa_transitions[current_id][symbol] = state_ids[target]

    accepting_states = {
        state_ids[state]
        for state in dfa_states
        if nfa.accept in state
    }

    return dfa_states, dfa_transitions, accepting_states


def simulate_dfa(input_string, alphabet, transitions, accepting_states):
    """Test an input string and return its path through the DFA."""
    current_state = 0
    trace = [current_state]

    for char in input_string:
        if char not in alphabet:
            return False, trace, f"Invalid symbol: {char}"

        current_state = transitions[current_state][char]
        trace.append(current_state)

    return current_state in accepting_states, trace, None


def main():
    regex = input("Enter a regular expression: ")

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

        print("\nPostfix:", postfix)
        print("Alphabet:", alphabet)

        print("\nDFA States:")
        for state_id, nfa_states in enumerate(states):
            members = ", ".join(
                f"q{s}" for s in sorted(nfa_states)
            )
            print(f"D{state_id} = {{{members}}}")

        print("\nDFA Transition Table:")
        print("State\t" + "\t".join(alphabet))

        for state_id in range(len(states)):
            row = [f"D{state_id}"]

            for symbol in alphabet:
                destination = transitions[state_id][symbol]
                row.append(f"D{destination}")

            print("\t".join(row))

        print("\nDFA Start State: D0")
        print(
            "DFA Accepting States:",
            [f"D{s}" for s in sorted(accepting)]
        )

        while True:
            input_string = input(
                "\nEnter a string to test (or type 'quit'): "
            )

            if input_string.lower() == "quit":
                break

            accepted, trace, error = simulate_dfa(
                input_string, alphabet, transitions, accepting
            )

            print(
                "DFA Path:",
                " -> ".join(f"D{s}" for s in trace)
            )

            if error:
                print("Error:", error)
            elif accepted:
                print("Result: ACCEPTED")
            else:
                print("Result: REJECTED")

    except ValueError as error:
        print("Error:", error)


if __name__ == "__main__":
    main()

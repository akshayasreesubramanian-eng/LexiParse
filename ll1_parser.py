
def parse_grammar(grammar_text):
    grammar = {}

    for line in grammar_text.strip().splitlines():
        if not line.strip():
            continue

        if "->" not in line:
            raise ValueError(f"Invalid grammar rule: {line}")

        left, right = line.split("->", 1)
        left = left.strip()
        right = right.strip()

        if not left or not right:
            raise ValueError(f"Invalid grammar rule: {line}")

        if left in grammar:
            raise ValueError(
                f"Duplicate rule for {left}. "
                "Put alternatives on the same line using |."
            )

        alternatives = []

        for alt in right.split("|"):
            symbols = alt.strip().split()

            if not symbols:
                raise ValueError(f"Empty production in rule: {line}")

            symbols = [
                "epsilon" if s == "ε" else s
                for s in symbols
            ]

            if "epsilon" in symbols and len(symbols) > 1:
                raise ValueError(
                    "epsilon must appear alone in a production."
                )

            alternatives.append(symbols)

        grammar[left] = alternatives

    if not grammar:
        raise ValueError("Please enter a grammar.")

    return grammar


def first_of_sequence(sequence, first, non_terminals):
    result = set()

    if not sequence or sequence == ["epsilon"]:
        return {"epsilon"}

    for symbol in sequence:
        if symbol == "epsilon":
            result.add("epsilon")
            return result

        if symbol not in non_terminals:
            result.add(symbol)
            return result

        result.update(first[symbol] - {"epsilon"})

        if "epsilon" not in first[symbol]:
            return result

    result.add("epsilon")
    return result


def compute_first(grammar):
    first = {nt: set() for nt in grammar}
    changed = True

    while changed:
        changed = False

        for nt, productions in grammar.items():
            for production in productions:
                new_symbols = first_of_sequence(
                    production, first, set(grammar)
                )

                old_size = len(first[nt])
                first[nt].update(new_symbols)

                if len(first[nt]) != old_size:
                    changed = True

    return first


def compute_follow(grammar, first):
    non_terminals = set(grammar)
    follow = {nt: set() for nt in grammar}

    start_symbol = next(iter(grammar))
    follow[start_symbol].add("$")

    changed = True

    while changed:
        changed = False

        for nt, productions in grammar.items():
            for production in productions:
                for i, symbol in enumerate(production):
                    if symbol not in non_terminals:
                        continue

                    remainder = production[i + 1:]

                    first_remainder = first_of_sequence(
                        remainder, first, non_terminals
                    )

                    additions = first_remainder - {"epsilon"}

                    if (
                        not remainder
                        or "epsilon" in first_remainder
                    ):
                        additions |= follow[nt]

                    old_size = len(follow[symbol])
                    follow[symbol].update(additions)

                    if len(follow[symbol]) != old_size:
                        changed = True

    return follow


def build_parsing_table(grammar, first, follow):
    non_terminals = set(grammar)
    table = {}
    conflicts = []

    for nt, productions in grammar.items():
        for production in productions:
            production_first = first_of_sequence(
                production, first, non_terminals
            )

            columns = production_first - {"epsilon"}

            if "epsilon" in production_first:
                columns |= follow[nt]

            for terminal in columns:
                key = (nt, terminal)

                if key in table and table[key] != production:
                    conflicts.append({
                        "non_terminal": nt,
                        "terminal": terminal,
                        "first_production": table[key],
                        "second_production": production
                    })
                else:
                    table[key] = production

    return table, conflicts


def parse_input(grammar, table, input_string, conflicts=None):
    if conflicts:
        return {
            "accepted": False,
            "message": "Grammar is not LL(1). Resolve conflicts first.",
            "steps": []
        }

    non_terminals = set(grammar)
    start_symbol = next(iter(grammar))

    tokens = input_string.split()

    if "$" in tokens:
        return {
            "accepted": False,
            "message": "Do not include $ in the input string.",
            "steps": []
        }

    if any(token == "epsilon" or token == "ε" for token in tokens):
        return {
            "accepted": False,
            "message": "Enter an empty input for an empty string; "
                       "do not type epsilon as an input token.",
            "steps": []
        }

    tokens.append("$")
    stack = ["$", start_symbol]
    index = 0
    steps = []

    max_steps = 10000

    for _ in range(max_steps):
        stack_text = " ".join(reversed(stack))
        remaining_input = " ".join(tokens[index:])
        top = stack[-1]
        lookahead = tokens[index]

        if top == "$" and lookahead == "$":
            steps.append({
                "stack": stack_text,
                "input": remaining_input,
                "action": "Accept"
            })

            return {
                "accepted": True,
                "message": "Input string accepted!",
                "steps": steps
            }

        if top not in non_terminals:
            if top == lookahead:
                steps.append({
                    "stack": stack_text,
                    "input": remaining_input,
                    "action": f"Match {top}"
                })

                stack.pop()
                index += 1
            else:
                steps.append({
                    "stack": stack_text,
                    "input": remaining_input,
                    "action": f"Error: expected {top}"
                })

                return {
                    "accepted": False,
                    "message": f"Rejected: expected '{top}', "
                               f"found '{lookahead}'.",
                    "steps": steps
                }

        else:
            production = table.get((top, lookahead))

            if production is None:
                steps.append({
                    "stack": stack_text,
                    "input": remaining_input,
                    "action": f"Error: no table entry for "
                              f"M[{top}, {lookahead}]"
                })

                return {
                    "accepted": False,
                    "message": f"Rejected: no rule for "
                               f"M[{top}, {lookahead}].",
                    "steps": steps
                }

            right_side = " ".join(production)

            steps.append({
                "stack": stack_text,
                "input": remaining_input,
                "action": f"{top} -> {right_side}"
            })

            stack.pop()

            if production != ["epsilon"]:
                for symbol in reversed(production):
                    stack.append(symbol)

    return {
        "accepted": False,
        "message": "Parsing stopped: maximum steps reached.",
        "steps": steps
    }


def display_sets(title, sets):
    print(f"\n{title}")

    for symbol, values in sets.items():
        print(f"{symbol}: {sorted(values)}")


def display_table(grammar, table):
    terminals = set()

    for _, terminal in table:
        terminals.add(terminal)

    terminals = sorted(terminals - {"$"}) + (
        ["$"] if "$" in terminals else []
    )

    print("\nLL(1) Parsing Table")
    print("Non-terminal | " + " | ".join(terminals))
    print("-" * (16 + len(terminals) * 15))

    for nt in grammar:
        row = []

        for terminal in terminals:
            production = table.get((nt, terminal))

            if production is None:
                row.append("-")
            else:
                row.append(
                    f"{nt} -> {' '.join(production)}"
                )

        print(f"{nt:12} | " + " | ".join(row))


def main():
    grammar_text = """\
E -> T E'
E' -> + T E' | epsilon
T -> id
"""

    try:
        grammar = parse_grammar(grammar_text)

        print("Grammar loaded successfully!")
        print(grammar)

        first = compute_first(grammar)
        follow = compute_follow(grammar, first)

        display_sets("FIRST Sets", first)
        display_sets("FOLLOW Sets", follow)

        table, conflicts = build_parsing_table(
            grammar, first, follow
        )

        display_table(grammar, table)

        if conflicts:
            print("\nGrammar is NOT LL(1). Conflicts found:")

            for conflict in conflicts:
                print(
                    f"M[{conflict['non_terminal']}, "
                    f"{conflict['terminal']}]: "
                    f"{conflict['first_production']} vs "
                    f"{conflict['second_production']}"
                )
        else:
            print("\nGrammar is LL(1). No conflicts found.")

        test_inputs = [
            "id",
            "id + id",
            "id + id + id",
            "id +",
            "+ id",
            "id id"
        ]

        for input_string in test_inputs:
            result = parse_input(
                grammar, table, input_string, conflicts
            )

            print(f"\nInput: {input_string!r}")
            print(result["message"])
            print(f"{'Stack':25} | {'Input':20} | Action")
            print("-" * 75)

            for step in result["steps"]:
                print(
                    f"{step['stack']:25} | "
                    f"{step['input']:20} | "
                    f"{step['action']}"
                )

    except ValueError as error:
        print("Grammar error:", error)


if __name__ == "__main__":
    main()



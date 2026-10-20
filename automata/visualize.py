
from graphviz import Digraph


def draw_nfa(nfa, filename="nfa"):
    graph = Digraph("NFA", format="png")
    graph.attr(rankdir="LR")
    graph.attr("node", shape="circle")

    # Invisible start node with an arrow to the start state.
    graph.node("start", label="", shape="none")
    graph.edge("start", f"q{nfa.start}")

    graph.node(
        f"q{nfa.accept}",
        shape="doublecircle"
    )

    for source, edges in nfa.transitions.items():
        for symbol, destination in edges:
            graph.edge(
                f"q{source}",
                f"q{destination}",
                label=symbol
            )

    path = graph.render(filename, cleanup=True)
    print(f"NFA diagram saved to: {path}")


def draw_dfa(states, transitions, accepting_states,
             alphabet, filename="dfa"):
    graph = Digraph("DFA", format="png")
    graph.attr(rankdir="LR")
    graph.attr("node", shape="circle")

    graph.node("start", label="", shape="none")
    graph.edge("start", "D0")

    for state_id in range(len(states)):
        shape = (
            "doublecircle"
            if state_id in accepting_states
            else "circle"
        )
        members = ", ".join(
            f"q{s}" for s in sorted(states[state_id])
        )
        graph.node(
            f"D{state_id}",
            label=f"D{state_id}\n{{{members}}}",
            shape=shape
        )

    for state_id, row in transitions.items():
        for symbol in alphabet:
            destination = row[symbol]
            graph.edge(
                f"D{state_id}",
                f"D{destination}",
                label=symbol
            )

    path = graph.render(filename, cleanup=True)
    print(f"DFA diagram saved to: {path}")

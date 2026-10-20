
from flask import Flask, render_template, request

from ll1_parser import (
    parse_grammar,
    compute_first,
    compute_follow,
    build_parsing_table,
    parse_input
)

app = Flask(__name__)

DEFAULT_GRAMMAR = """E -> T E'
E' -> + T E' | epsilon
T -> id"""


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/", methods=["GET", "POST"])
def home():
    grammar_text = DEFAULT_GRAMMAR
    input_string = "id + id"

    grammar = {}
    first = {}
    follow = {}
    terminals = []
    table_rows = []
    conflicts = []
    result = None
    error = None

    if request.method == "POST":
        grammar_text = request.form.get("grammar", "").strip()
        input_string = request.form.get("input_string", "").strip()

    try:
        grammar = parse_grammar(grammar_text)
        first = compute_first(grammar)
        follow = compute_follow(grammar, first)

        table, conflicts = build_parsing_table(
            grammar, first, follow
        )

        non_terminals = set(grammar)
        terminal_set = set()

        for productions in grammar.values():
            for production in productions:
                for symbol in production:
                    if (
                        symbol not in non_terminals
                        and symbol != "epsilon"
                    ):
                        terminal_set.add(symbol)

        terminal_set.add("$")
        terminals = sorted(terminal_set - {"$"}) + ["$"]

        for nt in grammar:
            cells = []

            for terminal in terminals:
                production = table.get((nt, terminal))

                production_text = (
                    f"{nt} -> {' '.join(production)}"
                    if production is not None
                    else ""
                )

                cells.append({
                    "terminal": terminal,
                    "production": production_text
                })

            table_rows.append({
                "non_terminal": nt,
                "cells": cells
            })

        if request.method == "POST":
            if not input_string:
                result = {
                    "accepted": False,
                    "message": "Please enter an input string.",
                    "steps": []
                }
            else:
                result = parse_input(
                    grammar,
                    table,
                    input_string,
                    conflicts
                )

    except ValueError as exc:
        error = str(exc)

    except Exception as exc:
        error = f"Something went wrong: {exc}"

    return render_template(
        "index.html",
        grammar_text=grammar_text,
        input_string=input_string,
        grammar=grammar,
        first=first,
        follow=follow,
        terminals=terminals,
        table_rows=table_rows,
        conflicts=conflicts,
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)

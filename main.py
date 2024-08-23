from unified_planning.io import PDDLReader
from unified_planning.shortcuts import Problem, FluentExp
from waitress import serve
from flask import Flask, jsonify, send_from_directory, request
import webbrowser
import argparse
from NonDeterministicSimulator import NonDeterministicSimulator

with open("help_page.txt") as help_file:
    description = help_file.read()

parser = argparse.ArgumentParser(description=description)
parser.add_argument('domain', type=str, help='Path to the PPDDL domain')
parser.add_argument('problem', type=str, help='Path to the PPDDL problem')
parser.add_argument('-s', '--no-browser', action='store_true', help='Stops the browser from opening on launch')
args = parser.parse_args()

problem: Problem = PDDLReader().parse_problem(args.domain, args.problem)


with NonDeterministicSimulator(problem) as simulator:
    simulator: NonDeterministicSimulator
    app = Flask(__name__)

    @app.route('/get_graph')
    def get_graph():
        def formatta(act):
            return f"{act['name']}{act['args']}"
        response_data = {
            "nodes": [
                {
                    "id": n.id,
                    "is_final": n.is_final,
                    "children": n.children,
                    "diff": [d for d in n.changes],
                    "choice": None if n.choice is None else formatta(n.choices[n.choice])
                } for n in simulator.get_nodes()
            ]
        }
        return jsonify(response_data)

    @app.route('/get_fluents')
    def get_fluents():
        print("GUI: getting fluents")

        response_data = {
            "fluents": [
                {
                    "name": f.name,
                    "type": str(f.type),
                    "signature": [
                        {
                            "name": p.name,
                            "type": str(p.type)
                        } for p in f.signature
                    ],
                    "str": str(f)
                } for f in problem.fluents
            ]
        }
        return jsonify(response_data)

    @app.route('/get_objects')
    def get_objects():
        print("GUI: getting objects")
        oggetti = {}
        for tipo in problem.user_types:
            oggetti[str(tipo)] = []
            for oggetto in problem.objects(tipo):
                oggetti[str(tipo)].append(str(oggetto))
        response_data = {
            "objects": oggetti
        }
        return jsonify(response_data)

    @app.route('/state_description')
    def state_description():
        if request.args.get("id") is None:
            return ('', 400)

        id = int(request.args.get("id"))
        if id not in simulator.nodi:
            return ('', 404)

        print(f"GUI: getting description for state {id}")
        stato = simulator.get_state(id)

        fluent_values = {}
        for fluent in problem.fluents:
            stack = [[]]
            actual_params = []
            while len(stack) > 0:
                corrente = stack.pop()
                if len(corrente) == len(fluent.signature):
                    actual_params.append(corrente)
                    continue
                for o in problem.objects(fluent.signature[len(corrente)].type):
                    new = corrente.copy()
                    new.append(o)
                    stack.append(new)

            fluent_values[fluent.name] = [
                {
                    "parameters": [
                        p.name for p in ap
                    ],
                    "value": str(stato.get_value(FluentExp(fluent, ap)))
                } for ap in actual_params
            ]

        return jsonify({
            "fluents": fluent_values
        })

    @app.route('/get_aviable')
    def get_aviable():
        if request.args.get("id") is None:
            return ('', 400)

        id = int(request.args.get("id"))
        if not simulator.has_state(id):
            return ('', 404)
        id = int(request.args.get("id"))
        return jsonify({
            "actions": [
                {
                    "name": act["name"],
                    "args": list(map(str, act["args"])),
                    "effects": [
                        [
                            str(eff) for eff in eff_set
                        ] for eff_set in act["effects"]
                    ]
                } for act in simulator.get_choices(id)
            ]
        })

    @app.route('/choose', methods=["POST"])
    def choose():
        if request.args.get("id") is None:
            return ('', 400)
        if request.args.get("n") is None:
            return ('', 400)

        id = int(request.args.get("id"))
        n = int(request.args.get("n"))

        if not simulator.choose(id, n):
            return ('', 404)

        print(f"GUI: choosing action {n} for state {id}")
        return ('', 200)

    @app.route('/undo_choice', methods=['POST'])
    def undo_choice():
        if request.args.get("id") is None:
            return ('', 400)
        id = int(request.args.get("id"))
        if not simulator.has_state(id):
            return ('', 404)
        print(f"GUI: undoing choice for state {id}")

        simulator.undo_choice(id)
        return ('', 200)

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)


if __name__ == '__main__':
    port = 5000
    host = "127.0.0.1"
    link = f"http://{host}:{port}/index.html"
    print(f"GUI at {link}")
    if not args.no_browser:
        webbrowser.open_new(link)
    serve(app, host=host, port=port)

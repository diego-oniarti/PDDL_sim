from unified_planning.io import PDDLReader
from unified_planning.shortcuts import SequentialSimulator, Fluent, Object, State, Action, Problem, Parameter, FluentExp
from unified_planning.engines.sequential_simulator import UPSequentialSimulator
from waitress import serve
from flask import Flask, jsonify, send_from_directory, request
import webbrowser
import argparse
import re
from utils.simulator_utils import state_equality2, state_diff

with open("help_page.txt") as help_file:
    description = help_file.read()

parser = argparse.ArgumentParser(description=description)
parser.add_argument('domain', type=str, help='Path to the PPDDL domain')
parser.add_argument('problem', type=str, help='Path to the PPDDL problem')
parser.add_argument('-s', '--no-browser', action='store_true', help='Stops the browser from opening on launch')
args = parser.parse_args()

problem: Problem = PDDLReader().parse_problem(args.domain, args.problem)

diff_regex = re.compile(r'(_differ\d+)+$')


class Node:
    def __init__(self, id: int, state: State, simulator, parent=None):
        self.id: int = id
        self.state: State = state
        self.is_final = simulator.is_goal(state)

        self.parent = parent.id if parent is not None else None
        self.children = None
        self.changes = []

        acts = {}
        for act, arg in simulator.get_applicable_actions(state):
            stripped_name = re.sub(diff_regex, '', act.name)
            key = ' '.join([stripped_name]+list(map(str, arg)))
            if key not in acts:
                acts[key] = {
                    "name": stripped_name,
                    "acts": [],
                    "args": arg,
                    "effects": []
                }
            acts[key]["effects"].append(act.effects)
            acts[key]["acts"].append(act)
        self.choices = [x for x in acts.values()]
        self.choice: int = None

        if parent is not None:
            self.changes = state_diff(problem, parent.state, self.state)


class NonDeterministicSimulator:
    def __init__(self, problem):
        self._problem = problem

    def __enter__(self):
        self._simulator = SequentialSimulator(self._problem).__enter__()
        self.nodi = {0: Node(0, self._simulator.get_initial_state(), self._simulator)}  # id -> node

        return self

    def _get_id(self):
        i = 0
        while i in self.nodi:
            i += 1
        return i

    def get_nodes(self):
        return self.nodi.values()

    def get_node(self, i):
        return self.nodi.get(i)

    def get_state(self, i):
        return self.nodi.get(i).state

    def get_choices(self, i):
        return self.nodi.get(i).choices

    def has_state(self, i):
        return i in self.nodi

    def get_choice(self, i):
        return self.nodi.get(i).choice

    def choose(self, id, n):
        if not self.has_state(id):
            return False

        node = self.nodi.get(id)
        if n < 0 or n > len(node.choices):
            return False

        choice = node.choices[n]
        node.choice = n
        node.children = []

        for action in choice["acts"]:
            # print("applying action")
            new_state = self._simulator.apply_unsafe(node.state, action, choice["args"])
            # controlla se esiste già un nodo equivalente
            for other in self.get_nodes():
                if state_equality2(problem, other.state, new_state):
                    # print("old state found")
                    node.children.append(other.id)
                    break
            else:
                # se non esiste crea un nuovo nodo
                new_id = self._get_id()
                new_node = Node(new_id, new_state, self._simulator, node)
                self.nodi[new_id] = new_node
                node.children.append(new_id)
                # print(f"creato nuovo nodo {new_id}")
        node.children = list(dict.fromkeys(node.children))  # rimuovi eventuali ripetizioni
        return True

    def undo_choice(self, id):
        nodo = self.nodi.get(id)

        nodo.choice = None

        tobe_deleted_ids = []
        stack = [child_id for child_id in filter(lambda cid: self.nodi[cid].parent == id, nodo.children)]
        while len(stack) > 0:
            id_corrente = stack.pop()
            tobe_deleted_ids.append(id_corrente)
            corrente = self.nodi[id_corrente]
            if corrente.children is not None:
                for child_id in corrente.children:
                    child = self.nodi[child_id]
                    if child.parent == id_corrente:
                        stack.append(child_id)
        nodo.children = None

        queue = [0]
        while len(queue) > 0:
            id_corrente = queue.pop()
            corrente = self.nodi[id_corrente]
            if corrente.children is None:
                continue
            for child_id in corrente.children:
                child = self.nodi[child_id]
                if child_id in tobe_deleted_ids:
                    child.parent = id_corrente
                    child.changes = state_diff(problem, corrente.state, child.state)
                    tobe_deleted_ids.remove(child_id)
                if child.parent == id_corrente:
                    queue.insert(0, child_id)

        for id in tobe_deleted_ids:
            # print(f"deleting node {id}")
            del self.nodi[id]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._simulator.__exit__(exc_type, exc_val, exc_tb)


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

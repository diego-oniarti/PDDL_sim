from unified_planning.io import PDDLReader
from unified_planning.shortcuts import SequentialSimulator, Fluent, Object, State, Action, Problem, Parameter, FluentExp
from unified_planning.engines.sequential_simulator import UPSequentialSimulator

from waitress import serve

from flask import Flask, jsonify, send_from_directory, request
import webbrowser

from typing import Dict

import argparse

import re

from utils.simulator_utils import state_equality2

parser = argparse.ArgumentParser(description="PDDL problem simulator")
parser.add_argument('domain', type=str, help='Path to the PDDL domain')
parser.add_argument('problem', type=str, help='Path to the PDDL problem')
args = parser.parse_args()

problem: Problem = PDDLReader().parse_problem(args.domain, args.problem)

# Sposta fluents e objects in mappe nome->valore per non dover iterare gli elementi ogni volta
fluents: Dict[str, Fluent] = {}
for fluent in problem.fluents:
    fluents[fluent.name] = fluent

objects: Dict[str, Object] = {}
for obj in problem.all_objects:
    objects[obj.name] = obj

diff_regex = re.compile(r'(_differ\d+)+$')

with SequentialSimulator(problem) as simulator:
    simulator: UPSequentialSimulator

    class Node:
        def __init__(self, id: int, state: State, parent=None):
            self.id: int = id
            self.state: State = state
            self.is_final = simulator.is_goal(state)

            self.parent: Node = parent
            self.children = None

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

    nodi = {0: Node(0, simulator.get_initial_state())}  # id -> node

    def get_id():
        i = 0
        while i in nodi:
            i += 1
        return i

    app = Flask(__name__)

    @app.route('/get_graph')
    def get_graph():
        response_data = {
            "nodes": [
                {
                    "id": n.id,
                    "is_final": n.is_final,
                    "children": n.children
                } for n in nodi.values()
            ]
        }
        return jsonify(response_data)

    @app.route('/get_fluents')
    def get_fluents():
        print("getting fluents")

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
        print("getting objects")
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
        id = int(request.args.get("id"))
        print(f"getting description for state {id}")
        stato = nodi.get(id).state

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
                } for act in nodi.get(id).choices
            ]
        })

    @app.route('/choose')
    def choose():
        id = int(request.args.get("id"))
        n = int(request.args.get("n"))

        node = nodi.get(id)
        node.choice = n
        node.children = []

        choice = node.choices[n]
        for action in choice["acts"]:
            print("applying action")
            new_state = simulator.apply_unsafe(node.state, action, choice["args"])
            # controlla se esiste già un nodo equivalente
            for other in nodi.values():
                if state_equality2(problem, other.state, new_state):
                    print("old state found")
                    node.children.append(other.id)
                    break
            else:
                # se non esiste crea un nuovo nodo
                new_id = get_id()
                new_node = Node(new_id, new_state, node.id)
                nodi[new_id] = new_node
                node.children.append(new_id)
                print(f"creato nuovo nodo {new_id}")
        node.children = list(dict.fromkeys(node.children))  # rimuovi eventuali ripetizioni
        return ('', 200)

    @app.route('/undo_choice')
    def undo_choice():
        id = int(request.args.get("id"))
        nodo = nodi.get(id)

        nodo.choice = None

        for child_id in nodo.children:
            child = nodi[child_id]
            if child.parent == id:
                print(f"deleting node {child_id}")
                del nodi[child_id]
        nodo.children = None

        saturation = False
        while not saturation:
            saturation = True
            tobe_deleted = []
            for id, nodo in nodi.items():
                if (nodo.parent is not None) and (nodo.parent not in nodi):
                    saturation = False
                    tobe_deleted.append(id)
            for id in tobe_deleted:
                print(f"deleting node {id}")
                del nodi[id]

        return ('', 200)



    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)


if __name__ == '__main__':
    port = 5000
    host = "127.0.0.1"
    link = f"http://{host}:{port}/index.html"
    print(f"GUI at {link}")
    webbrowser.open_new(link)
    serve(app, host=host, port=port)

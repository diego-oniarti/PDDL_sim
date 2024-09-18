from unified_planning.shortcuts import SequentialSimulator, State
import re
from utils.simulator_utils import state_equality2, state_diff

diff_regex = re.compile(r'(_differ\d+)+$')


class Node:
    def __init__(self, id: int, state: State, simulator, problem, parent=None):
        self.id: int = id
        self.state: State = state
        self.is_final = simulator.is_goal(state)
        self.is_loop = False

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
        self.nodi = {0: Node(0, self._simulator.get_initial_state(), self._simulator, self._problem)}  # id -> node

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
                if state_equality2(self._problem, other.state, new_state):
                    # print("old state found")
                    node.children.append(other.id)
                    break
            else:
                # se non esiste crea un nuovo nodo
                new_id = self._get_id()
                new_node = Node(new_id, new_state, self._simulator, self._problem, node)
                self.nodi[new_id] = new_node
                node.children.append(new_id)
                # print(f"creato nuovo nodo {new_id}")
        node.children = list(dict.fromkeys(node.children))  # rimuovi eventuali ripetizioni
        self._find_loops()
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
                    child.changes = state_diff(self._problem, corrente.state, child.state)
                    tobe_deleted_ids.remove(child_id)
                if child.parent == id_corrente:
                    queue.insert(0, child_id)

        for id in tobe_deleted_ids:
            # print(f"deleting node {id}")
            del self.nodi[id]
        self._find_loops()

    def _find_loops(self):
        transposed = self._transpose()

        for id in self.nodi.keys():
            self._check_loop(id, transposed)

    def _check_loop(self, id, transposed):
        if self.get_node(id).choice is None:
            self.get_node(id).is_loop = False
            return
        raggiungibili = set()
        stack_forward = [id]
        while len(stack_forward) > 0:
            id_corrente = stack_forward.pop()
            nodo_corrente = self.get_node(id_corrente)

            if nodo_corrente.children is not None:
                for id_figlio in nodo_corrente.children:
                    if id_figlio not in raggiungibili:
                        raggiungibili.add(id_figlio)
                        stack_forward.append(id_figlio)

        affluenti = set()
        stack_backward = [id]
        while len(stack_backward) > 0:
            id_corrente = stack_backward.pop()
            nodo_corrente = transposed[id_corrente]

            for id_figlio in nodo_corrente.children:
                if id_figlio not in affluenti:
                    affluenti.add(id_figlio)
                    stack_backward.append(id_figlio)

        self.get_node(id).is_loop = raggiungibili.issubset(affluenti)

    def _transpose(self):
        class MiniNode:
            def __init__(self, id):
                self.id = id
                self.children = []

        transposed = {}
        for id in self.nodi.keys():
            transposed[id] = MiniNode(id)

        for nodo in self.nodi.values():
            id1 = nodo.id
            if nodo.children is not None:
                for child_id in nodo.children:
                    transposed[child_id].children.append(id1)

        for nodo in transposed.values():
            nodo.children = list(dict.fromkeys(nodo.children))

        return transposed

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._simulator.__exit__(exc_type, exc_val, exc_tb)

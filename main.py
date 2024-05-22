from unified_planning.io import PDDLReader
from unified_planning.shortcuts import SequentialSimulator, Fluent, Object, State, Action, Problem, Parameter, FluentExp
from unified_planning.engines.sequential_simulator import UPSequentialSimulator
from typing import Dict, List, Tuple, cast
import argparse

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

# Controlla l'uguaglianza tra due stati SOLO in base ai fluent
def state_equality(problem: Problem, state_a: State, state_b: State) -> bool:
    for fluent in problem.fluents:
        fluent: Fluent
        parametri: List[(None|Object)] = [None]*len(fluent.signature)
        if not fluent_equality(problem, fluent, state_a, state_b, parametri, 0):
            return False
    return True

def fluent_equality(problem: Problem, fluent: Fluent, state_a: State, state_b: State, parametri: List[(None|Object)], index: int) -> bool:
    signature: List[Parameter] = fluent.signature
    for oggetto in problem.objects(signature[index].type):
        oggetto: Object
        parametri[index] = oggetto
        if index == len(signature)-1:
            if state_a.get_value(FluentExp(fluent, parametri)) != state_b.get_value(FluentExp(fluent, parametri)):
                return False
        else:
            if not fluent_equality(problem, fluent, state_a, state_b, parametri, index+1):
                return False
    return True

def main():
    with SequentialSimulator(problem) as simulator:
        simulator: UPSequentialSimulator
        
        # Stack di tutti gli stati visti
        states: List[State] = [simulator.get_initial_state()]
        run: bool = True
        while run:
            print("\nState number: {n}".format(n=len(states)))
            # Prendi lo stato corrente dalla cima della stack
            state: State = states[len(states)-1]
            
            print("Applicable Actions")
            # get_applicable_actions -> (Action, (actual params...))
            applicable_actions = simulator.get_applicable_actions(state)
            actions: List[Tuple[Action, Tuple[Object, ...]]] = []
            for applicable_action in applicable_actions:
                # Stampa solo il nome dell'azione e i parametri per rendere la scelta più leggibile
                print("{n}: {action_name} {actual_params}".format(n=len(actions), action_name=applicable_action[0].name,actual_params=applicable_action[1]))
                actions.append(applicable_action)
            # Stampa menù
            print("i: Stato iniziale\nf: Stato finale\np: Print stato\nu: Undo\nq: Quit")
            
            taking_input = True
            while taking_input:
                # Crasha se non inserisci un numero. Per questo prototipo va bene così
                choice: str = input("> ").strip(" ")
                match (choice):
                    case "i":
                        # Controlla se lo stato corrente è uguale a quello di partenza
                        uguali = state_equality(problem, state, states[0])
                        print("Sono uguali: {val}".format(val=uguali))
                    case "f":
                        # Controlla se lo stato è un goal del problema
                        print("Stato finale: {val}".format(val=simulator.is_goal(state)))
                    case "p":
                        # Printa lo stato corrente
                        print(str(state))
                    case "u":
                        # Togle uno stato dalla stack
                        if (len(states)<2):
                            print("Already at beginning state")
                        else:
                            states.pop()
                            taking_input = False
                    case "q":
                        # Esce dalla simulazione
                        taking_input = False
                        run = False
                    case _:
                        if choice.isnumeric() and 0<=int(choice) and int(choice)<len(actions):
                            # Simula l'azione scelta
                            chosen_action = actions[int(choice)]
                            new_state: State = simulator.apply_unsafe(state, chosen_action[0], chosen_action[1])
                            states.append(new_state)
                            taking_input = False

if __name__ == '__main__':
   main() 

'''
Diego Oniarti
Mockup di un simulatore di problemi PDDL.
Permette di caricare un dominio e un problema su cui simulare una sequenza di azioni.
'''

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import SequentialSimulator

reader = PDDLReader()
problem = reader.parse_problem('./gripper.pddl', './gripper-ball.pddl')

# Sposta fluents e objects in mappe nome->valore per non dover iterare gli elementi ogni volta
fluents = {}
for fluent in problem.fluents:
    fluents[fluent.name] = fluent

objects = {}
for obj in problem.all_objects:
    objects[obj.name] = obj

# Devo pensare una funzione per comparare due stati. Serve per trovare cicli nella simulazione
# Non posso usare il tostring dei due stati perché i valori non sono necessatiamente nello stesso ordine
# Due stati possono avere tutti i valori uguali ma essere comunque diversi se si prende in considerazione l'aspetto temporale della simulazione.
def state_equality(state_a, state_b):
    return False

with SequentialSimulator(problem) as simulator:
    # Stack di tutti gli stati visti
    states = [simulator.get_initial_state()]
    run = True
    while run:
        # Prendi lo stato corrente dalla cima della stack
        state = states[len(states)-1]
        '''
        # Controlla se (free hand) è true nello stato corrente
        free_fluent = fluents.get("free")
        hand = objects.get("hand")
        is_hand_free = state.get_value(FluentExp(free_fluent, [hand]))
        print("(free hand): {free}".format(free=is_hand_free))
        '''

        # Le actions sono ritornate da get_applicable_actions come tupla dove il primo elemento è un'azione e il secondo è una tupla con i parametri effettivi
        print("Applicable Actions")
        applicable_actions = simulator.get_applicable_actions(state)
        actions = []
        for applicable_action in applicable_actions:
            # Stampa solo il nome dell'azione e i parametri per rendere la scelta più leggibile
            print("{n}: {action_name} {actual_params}".format(n=len(actions), action_name=applicable_action[0].name,actual_params=applicable_action[1]))
            actions.append(applicable_action)
        # Stampa menù
        print("-1: Stato iniziale\n-2: Stato finale\n-3: Print stato\n-4: Undo\n-5: Quit")
        
        taking_input = True
        while taking_input:
            # Crasha se non inserisci un numero. Per questo prototipo va bene così
            choice = int( input("input >") )
            if choice==-1:
                # Controlla se lo stato corrente è uguale a quello di partenza
                uguali = state_equality(state, states[0])
                print("Sono uguali: {val}".format(val=uguali))
            elif choice==-2:
                # Controlla se lo stato è un goal del problema
                print("Stato finale: {val}".format(val=simulator.is_goal(state)))
            elif choice==-3:
                # Printa lo stato corrente
                print(str(state))
            elif choice==-4:
                states.pop()
                taking_input = False
            elif choice==-5:
                # Esce dalla simulazione
                taking_input = False
                run = False
            else:
                # Simula l'azione scelta
                chosen_action = actions[choice]
                new_state = simulator.apply(state, chosen_action[0], chosen_action[1])
                states.append(new_state)
                taking_input = False


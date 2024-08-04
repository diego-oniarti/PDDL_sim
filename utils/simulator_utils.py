from unified_planning.shortcuts import SequentialSimulator, Fluent, Object, State, Action, Problem, Parameter, FluentExp
from typing import List

# Controlla l'uguaglianza tra due stati SOLO in base ai fluent
def state_equality(problem: Problem, state_a: State, state_b: State) -> bool:
    for fluent in problem.fluents:
        fluent: Fluent
        parametri: List[(None | Object)] = [None]*len(fluent.signature)
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


# versione iterativa e più stabile della funzione
def state_equality2(problem, state_a, state_b) -> bool:
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

        for ap in actual_params:
            if state_a.get_value(FluentExp(fluent, ap)) != state_b.get_value(FluentExp(fluent, ap)):
                return False

    return True

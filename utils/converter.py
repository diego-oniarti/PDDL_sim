import os
import re
from typing import List, Self
from enum import Enum
from collections import deque

def trim_par(x: str):
    return x.lstrip("(").rstrip(")")

class StringReader:
    def __init__(self, stringa: str):
        self.stringa = stringa.strip()
        self.index = 0

    def skip(self, pattern: str) -> bool:
        if self.stringa[self.index:self.index+len(pattern)] != pattern:
            return False
        self.index += len(pattern)
        return True

    def read_word(self) -> str:
        acc=""
        self.skip(" ")
        while self.index<len(self.stringa) and self.stringa[self.index]!=" " and self.stringa[self.index]!=")":
            acc += self.stringa[self.index]
            self.index+=1
        return acc

    def peak_word(self) -> str:
        acc=""
        self.skip(" ")
        i=self.index
        while i<len(self.stringa) and self.stringa[i]!=" " and self.stringa[i]!=")":
            acc += self.stringa[i]
            i+=1
        return acc

    def skip_to(self, pattern: str) -> None:
        while self.index<len(self.stringa):
            i=0
            while i<len(pattern) and self.stringa[self.index+i]==pattern[i]:
                i+=1
            if i==len(pattern):
                return
            self.index+=1

    def check(self, pattern: str) -> bool:
        return self.stringa[self.index:self.index+len(pattern)] == pattern

    def read_parentesis(self) -> str:
        acc = ""
        self.skip_to('(')
        self.index+=1
        aperte = 0
        while not (aperte==0 and self.stringa[self.index] == ')'):
            carattere = self.stringa[self.index]
            acc += carattere
            match carattere:
                case '(':
                    aperte+=1
                case ')':
                    aperte-=1
            self.index += 1
        self.index += 1
        return acc

    def ended(self) -> bool:
        return self.index == len(self.stringa) or self.stringa[self.index:].strip(" ")==""

    def rest(self) -> str:
        return self.stringa[self.index:]

class ExpressionType(Enum):
    AND = 1
    NOT = 2
    ONEOF = 3
    VALUE = 4

class Expression:
    def __init__(self, stringa: str, exp_id=0, parent: (None|Self)=None):
        reader = StringReader(stringa)
        self.childs: List[Expression] = []
        self.id = exp_id
        self.parent=parent
        match reader.peak_word():
            case 'and':
                self.ex_type = ExpressionType.AND
                reader.skip('and')
                while not reader.ended():
                    self.childs.append(Expression(reader.read_parentesis(), self.id+1+len(self.childs),self ))
            case 'not':
                self.ex_type = ExpressionType.NOT
                reader.skip('not')
                self.childs.append(Expression(reader.read_parentesis(), self.id+1,self) )
            case 'oneof':
                self.ex_type = ExpressionType.ONEOF
                reader.skip('oneof')
                self.childs = []
                while not reader.ended():
                    self.childs.append(Expression(reader.read_parentesis(), self.id+1+len(self.childs), self ))
            case _:
                self.ex_type = ExpressionType.VALUE
                self.value = stringa

    def has_oneof(self) -> bool:
        if self.ex_type == ExpressionType.VALUE or self.ex_type == ExpressionType.NOT:
            return False
        if self.ex_type == ExpressionType.ONEOF:
            return True
        for child in self.childs:
            if child.has_oneof():
                return True
        return False

    def __str__(self):
        ret = ""
        match self.ex_type:
            case ExpressionType.AND:
                ret = "and " + " ".join(map(lambda c: "({cs})".format(cs=c), self.childs))
            case ExpressionType.NOT:
                ret = "not ({ch})".format(ch=self.childs[0])
            case ExpressionType.VALUE:
                ret = self.value
            case ExpressionType.ONEOF:
                ret = "oneof " + " ".join(map(lambda c: "({cs})".format(cs=c), self.childs))
        return ret

'''
- name: Str
- parameters: Str
- precondition: Str
- effect: Expression
'''
class Action:
    def __init__(self, name: str, parameters: str, preconditions: str, effect: Expression):
        self.name = name
        self.parameters = parameters
        self.precondition = preconditions
        self.effect = effect

    @staticmethod
    def from_str(stringa: str):
        reader = StringReader(stringa)
        reader.skip(":action")

        name = reader.read_word()
        effect: Expression
        parameters: str = ""
        precondition: str = ""

        while not reader.ended():
            match reader.read_word():
                case ':parameters':
                    parameters = reader.read_parentesis()
                case ':precondition':
                    precondition = reader.read_parentesis()
                case ':effect':
                    effect = Expression(reader.read_parentesis())

        return Action(name, parameters, precondition, effect)

    def has_oneof(self) -> bool:
        return self.effect.has_oneof()

    def first_oneof(self) -> (Expression|None):
        Q = deque()
        cur: (Expression|None) = self.effect
        while (cur is not None) and (cur.ex_type != ExpressionType.ONEOF):
            for child in cur.childs:
                Q.append(child)
                if len(Q)>0:
                    cur = Q.popleft()
                else:
                    cur = None
        return cur

    def __str__(self):
        return "(:action {name} :parameters ({parameters}) :precondition ({precondition}) :effect ({effect}))".format(
                name = self.name,
                parameters = self.parameters,
                precondition = self.precondition,
                effect = self.effect
                )

'''
- name: Str
- actions: List[Action]
- requirements: List[Str]
- others: List[Str] I campi senza parentesi attorno
'''
class Domain:
    def __init__(self, file_str: str):
        reader = StringReader(trim_par(file_str))
        reader.skip("define")

        self.name = ""
        self.others: List[str] = []
        self.actions: List[Action] = []

        while not reader.ended():
            parentesi = reader.read_parentesis()
            reader_parentesi = StringReader(parentesi)
            match reader_parentesi.read_word():
                case 'domain':
                    self.name = reader_parentesi.read_word()
                case ':action':
                    self.actions.append(Action.from_str(parentesi))
                case ':requirements':
                    self.requirements = list(filter(lambda x: x!=':non-deterministic', reader_parentesi.rest().strip().split(' ')))
                case _:
                    self.others.append(parentesi)

    def convert(self) -> None:
        stack: List[Action] = [x for x in self.actions]
        self.actions = []
        while len(stack)>0:
            corrente = stack.pop()
            if not corrente.has_oneof():
                self.actions.append(corrente)
                continue

            bivio = corrente.first_oneof()
            N = len(bivio.childs)
            for i in range(N):
                new_action_name = corrente.name + "_def"+str(i)
                new_action_parameters = corrente.parameters
                new_action_precondition = corrente.precondition
                new_action_effect = Expression(str(corrente.effect))
                if bivio.id==0:
                    new_action_effect = new_action_effect.childs[i]
                else:
                    correction_stack = [new_action_effect]
                    stop=False
                    while not stop and len(correction_stack) > 0:
                        cur = correction_stack.pop()
                        if cur.id==bivio.id:
                            cur_index = cur.parent.childs.index(cur)
                            cur.parent.childs[cur_index] = cur.childs[i]
                            stop=True
                        else:
                            for child in cur.childs:
                                correction_stack.append(child)

                stack.append(Action(new_action_name, new_action_parameters, new_action_precondition, new_action_effect))

    def __str__(self):
        return 'Name: \t{name}\nActions:\n{actions}\nRequirements:\n{requirements}\nOthers:\n{others}'.format(
            name=self.name,
            requirements="\n".join(self.requirements),
            actions="\n".join(map(lambda x: str(x), self.actions)),
            others = "\n".join(self.others)
        )


# Read the contents of a file and convert them in a one line string
# Each group of adjacent whitespaces is replaced by one space to make parsing easier
# Rises an exception if the provided filepath doesn't point to any file
def file_to_string(filepath: str) -> str:
    if not os.path.isfile(filepath):
        raise Exception("File not found {fp}".format(fp=filepath))

    file = open(filepath, "r")
    contents = file.read()
    file.close()

    contents_one_line = re.sub(r"\s+", " ", contents)
    return contents_one_line.strip(" ")
# (define (domain table_non_deterministic) (:requirements :typing :strips :non-deterministic) (:types tavolo palla ) (:predicates (on_table ?x - palla ?y - tavolo) (on_floor ?x - palla) ) (:action prendi :parameters (?x - palla) :precondition (on_floor ?x) :effect (not (on_floor ?x)) ) (:action posa :parameters (?x - palla ?y - tavolo) :precondition (and (not (on_floor ?x)) (not (on_table ?x ?y)) ) :effect (oneof (on_table ?x ?y) (on_floor ?x) ) ) )


if __name__ == '__main__':
    # print(convert("examples/table/domain.pddl"))
    # print(convert("examples/jars/jar_domain.pddl"))
    contents = file_to_string("examples/table/domain.pddl")
    dom = Domain(contents)
    print("INITIAL DOMAIN")
    print(dom)
    dom.convert()
    print("CONVERTED DOMAIN")
    print(dom)

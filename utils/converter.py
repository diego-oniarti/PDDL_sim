import os
import re
from typing import List
from enum import Enum

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
    def __init__(self, stringa: str):
        reader = StringReader(stringa)
        match reader.peak_word():
            case 'and':
                self.ex_type = ExpressionType.AND
                reader.skip('and')
                self.childs = []
                while not reader.ended():
                    self.childs.append(Expression(reader.read_parentesis()))
            case 'not':
                self.ex_type = ExpressionType.NOT
                self.child = Expression(reader.read_parentesis())
            case 'oneof':
                self.ex_type = ExpressionType.ONEOF
                reader.skip('oneof')
                self.childs = []
                while not reader.ended():
                    self.childs.append(Expression(reader.read_parentesis()))
            case _:
                self.ex_type = ExpressionType.VALUE
                self.value = stringa
                pass

    def __str__(self):
        ret = ""
        match self.ex_type:
            case ExpressionType.AND:
                ret = "and " + " ".join(map(lambda c: "({cs})".format(cs=c), self.childs))
            case ExpressionType.NOT:
                ret = "not ({ch})".format(ch=self.child)
            case ExpressionType.VALUE:
                ret = self.value
            case ExpressionType.ONEOF:
                ret = "oneof " + " ".join(map(lambda c: "({cs})".format(cs=c), self.childs))
        return ret

'''
- name: Str
- parameters: Str
- precondition: Str
- effects: Expression
'''
class Action:
    def __init__(self, stringa: str):
        reader = StringReader(stringa)
        reader.skip(":action")
        self.name = reader.read_word()
        self.effects: List[Expression] = []

        while not reader.ended():
            match reader.read_word():
                case ':parameters':
                    self.parameters = reader.read_parentesis()
                case ':precondition':
                    self.precondition = reader.read_parentesis()
                case ':effect':
                    self.effects.append(Expression(reader.read_parentesis()))

    def __str__(self):
        return "(:action {name} :parameters ({parameters}) :precondition ({precondition}) {effects})".format(
                name = self.name,
                parameters = self.parameters,
                precondition = self.precondition,
                effects = " ".join(map(lambda x: ":effect ({ex})".format(ex=x), self.effects))
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
                    self.actions.append(Action(parentesi))
                case ':requirements':
                    self.requirements = filter(lambda x: x!=':non-deterministic', reader_parentesi.rest().strip().split(' '))
                case _:
                    self.others.append(parentesi)

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
    print(Domain(contents))

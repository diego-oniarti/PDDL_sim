import os
from ..utils.converter import *

def test_file_to_string():
    fp = os.path.join(os.path.dirname(__file__),'example_domain.pddl')
    assert file_to_string(fp) == "(define (domain table_non_deterministic) (:requirements :typing :strips :non-deterministic) (:types tavolo palla ) (:predicates (on_table ?x - palla ?y - tavolo) (on_floor ?x - palla) ) (:action prendi :parameters (?x - palla) :precondition (on_floor ?x) :effect (not (on_floor ?x)) ) (:action posa :parameters (?x - palla ?y - tavolo) :precondition (and (not (on_floor ?x)) (not (on_table ?x ?y)) ) :effect (oneof (on_table ?x ?y) (on_floor ?x) ) ) )"

def test_string_reader():
    reader = StringReader("aaaa (bbbb) cccc (dddd) eeee ffff")
    assert reader.skip("aaa")
    assert reader.read_word()=="a"
    reader.skip_to("cc")
    assert reader.index == 12
    assert reader.read_parentesis() == "dddd"
    reader.skip(" ")
    assert reader.check("eeee")
    assert reader.peak_word() == "eeee"
    
if __name__ == '__main__':
    test_file_to_string()


import sys
import os
# Aggiungi la directory del modulo al percorso di ricerca
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unified_planning.io import PDDLReader, PDDLWriter


def test_conversione_blocksworld():
    TMP_FILE_PATH = ".\\tests\\TMP\\converted_blockworlds.pddl"
    CONTROL_FILE_PATH = ".\\tests\\converted_blockworlds.pddl"
    problem = PDDLReader().parse_problem("examples\\blocksworld\\domain.pddl")
    PDDLWriter(problem).write_domain(TMP_FILE_PATH)

    with open(TMP_FILE_PATH, 'r') as file1, open(CONTROL_FILE_PATH, 'r') as file2:
        file1_content = file1.read()
        file2_content = file2.read()
        assert file1_content == file2_content

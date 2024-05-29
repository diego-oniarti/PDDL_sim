(define (domain table_non_deterministic)
  (:requirements :typing :strips :non-deterministic)
  (:types
    tavolo
    palla
  )
  (:predicates
    (on_table ?x - palla ?y - tavolo)
    (on_floor ?x - palla)
  )
  (:action prendi
    :parameters (?x - palla)
    :precondition (on_floor ?x)
    :effect (not (on_floor ?x))
  )
  (:action posa
    :parameters (?x - palla ?y - tavolo)
    :precondition (and
      (not (on_floor ?x))
      (not (on_table ?x ?y))
    )
    :effect (oneof
      (on_table ?x ?y)
      (on_floor ?x)
    )
  )
)

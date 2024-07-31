(define (domain water_transfer)
 (:requirements :strips :fluents)
 (:types jar)

 (:predicates
  (isjar ?x - jar)
 )

 (:functions
  (level ?x - jar)
 )

 (:action pour
  :parameters (?from - jar ?to - jar)
  :precondition (and
      (> (level ?from) 0)
      )
  :effect (and
      (decrease (level ?from) 1)
      (increase (level ?to) 1)
      )
 )
)


(define (domain oneofs)
 (:requirements :typing :strips :non-deterministic)
 (:predicates
  (A ?x)
  (B ?x)
  (C ?x)
 )
 (:action azione
  :parameters (?x)
  :precondition ()
  :effect (and
   (oneof 
    (C ?x) 
    (B ?x)
   )
   (oneof 
    (A ?x)
    (B ?x)
   )
  )
 )
)


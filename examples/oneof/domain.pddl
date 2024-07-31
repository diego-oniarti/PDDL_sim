(define (domain oneofs)
 (:requirements :conditional-effects :typing :strips :non-deterministic)
 (:predicates
  (A ?x)
  (B ?x)
  (C ?x)
  (D ?x)
  (E ?x)
  (F ?x)
  (G ?x)
  (H ?x)
  (I ?x)
  (J ?x)
 )
 (:action azione
  :parameters (?x)
  :precondition ()
  :effect (and
   (oneof
    (and
     (A ?x)
     (B ?x)
    )
    (oneof
     (C ?x)
     (D ?x)
    )
   )
   (and
    (E ?x)
    (F ?x)
   )
   (oneof
    (and
     (G ?x)
     (H ?x)
    )
    (when
     (A ?x)
     (oneof
      (not (I ?x))
      (not (J ?x))
     )
    )
   )
  )
 )
)


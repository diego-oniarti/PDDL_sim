(define (domain blocks2)
 (:requirements :non-deterministic :equality)
 (:predicates
  (holding ?b)
  (emptyhand)
  (on ?b1 ?b2)
  (ontable ?b)
  (clear ?b)
 )

 (:action grab
  :parameters (?b1 ?b2)
  :precondition (and 
   (clear ?b1)
   (emptyhand)
   (on ?b1 ?b2)
   (not (= ?b1 ?b2))
  )
  :effect (and
   (clear ?b2)
   (not (on ?b1 ?b2))
   (oneof
    (ontable ?b1)
    (and
     (not (emptyhand))
     (holding ?b1)
    )
   )
  )
 )

 (:action put
  :parameters (?b1 ?b2)
  :precondition (and 
   (clear ?b2)
   (holding ?b1)
   (not (= ?b1 ?b2))
  )
  :effect (and
   (not (holding ?b1))
   (emptyhand)
   (oneof
    (ontable ?b1)
    (and
     (on ?b1 ?b2)
     (not (clear ?b2))
    )
   )
  )
 )

 (:action pick-up
  :parameters (?b)
  :precondition (and 
   (clear ?b)
   (emptyhand)
   (ontable ?b)
  )
  :effect (oneof
   (and)
   (and 
    (not (emptyhand))
    (not (ontable ?b))
    (holding ?b)
   )
  )
 )

 (:action put-down
  :parameters (?b)
  :precondition (and 
   (holding ?b)
  )
  :effect (and
   (emptyhand)
   (ontable ?b)
   (not (holding ?b))
  )
 )


)

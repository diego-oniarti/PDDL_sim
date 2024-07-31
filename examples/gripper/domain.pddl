(define (domain gripper)
    (:predicates
        (ROOM ?x) (ISBALL ?x) (GRIPPER ?x)
        (at-room ?x) (ball-in-room ?x ?y)
        (free ?x) (carry ?x ?y)
    )
    (:action move :parameters (?x ?y)
        :precondition (
            and
            (ROOM ?x) (ROOM ?y) (at-room ?x)
            
        )
        :effect (
            and 
            (at-room ?y)
            (not (at-room ?x))
        )
    )
    (:action pick-up :parameters (?x ?y ?z)
        :precondition (
            and
            (ISBALL ?x) (ROOM ?y) (GRIPPER ?z)
            (ball-in-room ?x ?y)
            (at-room ?y)
            (free ?z)
        )
        :effect (
            and
            (carry ?z ?x)
            (not (ball-in-room ?x ?y))
            (not (free ?z))
        )
    )
    (:action drop :parameters (?x ?y ?z)
        :precondition (
            and
            (ISBALL ?x) (ROOM ?y) (GRIPPER ?z)
            (carry ?z ?x)
            (at-room ?y)
        )
        :effect (
            and
            (ball-in-room ?x ?y)
            (free ?z)
            (not (carry ?z ?x))
        )
    )
)

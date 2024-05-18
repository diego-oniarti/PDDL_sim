(define (problem gripper-four-balls)
    (:domain gripper)
    (:objects roomA roomB ball hand)
    (:init 
        (ROOM roomA) (ROOM roomB)
        (ISBALL ball)
        (GRIPPER hand) (free hand)
        (at-room roomA)
        (ball-in-room ball roomA)
    )
    (:goal
        (ball-in-room ball roomB)
    )
)

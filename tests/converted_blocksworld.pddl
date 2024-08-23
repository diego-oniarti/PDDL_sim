(define (domain blocks_domain-domain)
 (:requirements :strips :typing :negative-preconditions :equality)
 (:types block)
 (:predicates (holding ?b - block) (emptyhand) (ontable ?b - block) (on ?b1 - block ?b2 - block) (clear ?b - block))
 (:action put_tower_down
  :parameters ( ?b1 - block ?b2 - block)
  :precondition (and (holding ?b2) (on ?b1 ?b2))
  :effect (and (ontable ?b2) (emptyhand) (not (holding ?b2))))
 (:action put_tower_on_block_differ2
  :parameters ( ?b1 - block ?b2 - block ?b3 - block)
  :precondition (and (holding ?b2) (on ?b1 ?b2) (clear ?b3))
  :effect (and (ontable ?b2) (emptyhand) (not (holding ?b2))))
 (:action put_tower_on_block_differ1
  :parameters ( ?b1 - block ?b2 - block ?b3 - block)
  :precondition (and (holding ?b2) (on ?b1 ?b2) (clear ?b3))
  :effect (and (on ?b2 ?b3) (emptyhand) (not (holding ?b2)) (not (clear ?b3))))
 (:action pick_tower_differ2
  :parameters ( ?b1 - block ?b2 - block ?b3 - block)
  :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
  :effect (and (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3))))
 (:action pick_tower_differ1
  :parameters ( ?b1 - block ?b2 - block ?b3 - block)
  :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3)))
 (:action put_down
  :parameters ( ?b - block)
  :precondition (and (holding ?b))
  :effect (and (ontable ?b) (emptyhand) (clear ?b) (not (holding ?b))))
 (:action put_on_block_differ2
  :parameters ( ?b1 - block ?b2 - block)
  :precondition (and (holding ?b1) (clear ?b2))
  :effect (and (ontable ?b1) (emptyhand) (clear ?b1) (not (holding ?b1))))
 (:action put_on_block_differ1
  :parameters ( ?b1 - block ?b2 - block)
  :precondition (and (holding ?b1) (clear ?b2))
  :effect (and (on ?b1 ?b2) (emptyhand) (clear ?b1) (not (holding ?b1)) (not (clear ?b2))))
 (:action pick_up_from_table_differ2
  :parameters ( ?b - block)
  :precondition (and (emptyhand) (clear ?b) (ontable ?b))
  :effect (and (holding ?b) (not (emptyhand)) (not (ontable ?b))))
 (:action pick_up_from_table_differ1
  :parameters ( ?b - block)
  :precondition (and (emptyhand) (clear ?b) (ontable ?b)))
 (:action pick_up_differ2
  :parameters ( ?b1 - block ?b2 - block)
  :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
  :effect (and (clear ?b2) (ontable ?b1) (not (on ?b1 ?b2))))
 (:action pick_up_differ1
  :parameters ( ?b1 - block ?b2 - block)
  :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
  :effect (and (holding ?b1) (clear ?b2) (not (emptyhand)) (not (clear ?b1)) (not (on ?b1 ?b2))))
)


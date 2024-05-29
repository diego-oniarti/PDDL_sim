(define (problem table_problem)
  (:domain table_non_deterministic)
  (:objects
    t - tavolo
    p - palla
  )
  (:init
    (on_floor p)
  )
  (:goal
    (on_table p t)
  )
)

(define (problem water_problem)
  (:domain water_transfer)
  (:objects
    jar1 jar2 - jar
  )
  (:init
    (= (level jar1) 2)
    (= (level jar2) 0)
  )
  (:goal
    (and
      (= (level jar1) 0)
      (= (level jar2) 2)
    )
  )
)


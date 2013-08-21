#!/usr/local/bin/python3

""" Collects training data:
    - past x months' excess return
    - past y months' excess volume
    Volume gains are calculated with a bonus of 1 and capped at +/- 100%
    (theoretically a positive gain can be infinite).

    x and y are arrays from the flag, eg:
    --er_months=1,2,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48
    --ev_months=1,2,3,6,9,12,15,18,21,24
"""


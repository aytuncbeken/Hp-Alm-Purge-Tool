# Hp-Alm-Purge-Tool

Python Based, MultiThreaded, HP ALM Purge Wizard

Problem
--------------------
Embeded HP ALM Purge Wizard works so slow and fails to work if:
1. You have lots of test sets
2. You try to select lots of test sets at once

Also, Purge Wizard can not be scheduled. This prevents continuous clean up of runs.

Solution
-------------------
This tool is works as same HP ALM Purge Wizard. Addition to default behaviour, it can be run multithreaded. 
It connects ALM via it's Rest Api.




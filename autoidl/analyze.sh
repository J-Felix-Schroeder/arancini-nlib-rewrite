#!/bin/bash
python3 src/trim.py
python3 src/autoidl.py --anal -f testsets/box64_trimmed.txt | tee out/analytics.log

#!/bin/bash
export LD_BIND_NOW=1
n=$1
shift
for i in $(seq $n); do
	start=$(date +%s.%N)
	"$@" &> /dev/null
	end=$(date +%s.%N)
	echo "$end - $start" | bc
done

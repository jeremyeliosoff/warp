#!/bin/bash
proj="/home/jeremy/dev/warp"

touch $proj/dirty
first=1
while [ -e $proj/dirty ]; do
	if [ $first == 1 ]; then
		$proj/warp.py
	else
		$proj/warp.py -r
	fi
	first=0
done


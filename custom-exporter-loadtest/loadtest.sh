#!/bin/bash

number_of_exporters=(50 100)
number_of_metrics=(100 200 400)
number_of_labels=(10 50 100)
query_list=$1
timestamp=$(date +%+y%+m%+d%+k%+M)
logfile=log/loadtest2_log_$timestamp.txt
datafile=log/loadtest2_data_$timestamp.csv

if [[ -z $1 ]]; then
    echo "usage: loadtest.sh <filename>"
    exit
fi

# create datafile
echo "time;num_exporter;num_metrics;num_labels;query;jq_selector;exporter;description;value" > $datafile

# kill all endpoints
function kills() {
    echo "Looking for scripts to kill ..."
    #list1=$(ps -ax | grep -E "./loadtest-main.py" | grep -v -e "grep" | cut -d ' ' -f 2);
    list1=$(ps -ax | grep -E "./loadtest-main.py" | grep -v -e "grep" | awk '{print $1}');
    if [[ -n $list1 ]]; then
        echo "found pids to kill: $list1"
        for pid in $list1; do kill $pid; done
    else echo "nothing found."
    fi
}

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" | tee -a $logfile
echo "$(date): ---Starting Load Testing Script---" | tee -a $logfile
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" | tee -a $logfile

kills

for expcount in "${number_of_exporters[@]}"; do
    for metcount in "${number_of_metrics[@]}"; do
        for labelcount in "${number_of_labels[@]}"; do
            echo "$(date): $expcount exporters, $metcount metrics each and total number of labels $labelcount" | tee -a $logfile
            ./loadtest-main.py $expcount $metcount $labelcount &

            pause=90  # pause sollte mind 1 Minute (65) sein, damit HTTP SD abgefragt wird und Endpunkte bekannt sind.
            echo "---Waiting $pause secs for prometheus server to scrape HTTP service discovery---" | tee -a $logfile

            # pause countdown
            while [ $pause -gt 0 ]; do
               echo -ne " $pause\033[0K\r"
               let "pause=pause-1"
               sleep 1
               done

            # process query list query_list
            while read -r line; do
            if [[ ! $line =~ ^# && -n $line ]] ; then
                # split line in query and jq argument:
                query=$(echo "$line" | cut -d ";" -f 1)
                jqselector=$(echo "$line" | cut -d ";" -f 2)
                exporter=$(echo "$line" | cut -d ";" -f 3)
                description=$(echo "$line" | cut -d ";" -f 4)
                echo "---------------- new query: --------------------"
                echo "Querying: $query"
                echo  "JQ selector: $jqselector"

                value=$(curl -s http://10.0.0.116:9090/api/v1/query --data-urlencode "query=$query" | jq "$jqselector")
                echo "Value: $value"
                echo "$(date +%s);$expcount;$metcount;$labelcount;$query;$jqselector;$exporter;$description;$value" | tee -a $datafile
            fi
            done <$query_list

            # kill all endpoints (python exporter cloud)
            script_pid=$(ps -ax | grep -E "loadtest-main.py $expcount $metcount $labelcount" | grep -v -e "grep" | awk '{print $1}')
            echo "killing pid $script_pid..." | tee -a $logfile;
            kill $script_pid;
        done
    done
done

echo "finished!"

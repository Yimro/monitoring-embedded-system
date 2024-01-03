#!/bin/bash

number_of_exporters=(10 20 40 80 100 200 400)
number_of_metrics=(100 200 400 800)


function zpquery() {
   if [[ -z "$1" ]]; then echo "usage: zpquery <PromQL Query> [<jq selector>]";
   else curl -s "http://10.0.0.116:9090/api/v1/query" --data-urlencode "query=$1" | jq $2
   fi
}

echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" > auto_test_log.txt
echo "$(date): ---Starting Load Testing Script---" >> auto_test_log.txt
echo "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" >> auto_test_log.txt

echo "Looking for scripts to kill ..."
list1=$(ps -ax | grep -E "python3 ./main.py" | grep -v -e "grep" | cut -d ' ' -f 1);
if [[ -n $list1 ]]; then
    echo "found pids to kill: $list1"
    for pid in $list1; do kill $pid; done
else echo "nothing found."
fi

for i in "${number_of_exporters[@]}"; do
    for j in "${number_of_metrics[@]}"; do
    echo "$(date): $i exporters, $j metrics each"
    echo "$(date): $i exporters, $j metrics each" >> auto_test_log.txt
    ./main.py $i $j &

    pause=90   # pause sollte mind 1 Minute sein, damit HTTP SD abgefragt wird und Endpunkte bekannt sind.
    echo "---Waiting $pause secs for prometheus server to scrape HTTP service discovery---"

    # pause countdown
    while [ $pause -gt 0 ]; do
       echo -ne " $pause\033[0K\r"
       let "pause=pause-1"
       sleep 1
       done

    query_1=$(curl -s 10.0.0.116:9090/metrics |  grep -E "prometheus_sd_discovered_targets{config=\"load_test\"")
    # start Änderungen
    query_2=$(curl -s 10.0.0.116:9090/metrics |  grep -E "prometheus_target_sync_length_seconds{scrape_job=\"load_test\",quantile=\"0.5\"}")
    query_3=$(curl -s 10.0.0.116:9090/metrics |  grep -E "prometheus_target_sync_length_seconds_sum{scrape_job=\"load_test\"}")

    # hier weitere queries einfügen  und loggen!
    echo "$(date): $query_1"
    echo "$(date): $query_1" >> auto_test_log.txt
    echo "$(date): $query_2"
    echo "$(date): $query_2" >> auto_test_log.txt
    echo "$(date): $query_3"
    echo "$(date): $query_3" >> auto_test_log.txt
    # stop Änderungen

    #echo "$(date): $query_1" >> auto_test_log.txt
    sleep 1
    script_pid=$(ps -ax | grep -E "python3 ./main.py $i $j" | grep -v -e "grep" | cut -d ' ' -f 1)
    echo $script_pid
    echo "killing pid $script_pid...";
        kill $script_pid;
    done
done

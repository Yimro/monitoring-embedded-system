#!/bin/bash

file=$1

if [[ -z $1 ]]; then
    echo "usage: test_query_list <filename>"
    exit
fi

while read -r line; do
if [[ ! $line =~ ^# && -n $line ]] ; then
    # split line in query and jq argument:
    query=$(echo "$line" | cut -d ";" -f 1)
    jqselector=$(echo "$line" | cut -d ";" -f 2)
    exporter=$(echo "$line" | cut -d ";" -f 3)
    description=$(echo "$line" | cut -d ";" -f 4)
#    echo "---------------- new query: --------------------"
#    echo "Querying: $query"
#    echo  "JQ selector: $jqselector"

    value=$(curl -s http://10.0.0.116:9090/api/v1/query --data-urlencode "query=$query" | jq "$jqselector")
    echo -e "$description: $value"
#    echo "$(date +%s);$expcount;$metcount;$query;$jqselector;$exporter;$description;$value" # | tee -a $datafile

fi
done <$file

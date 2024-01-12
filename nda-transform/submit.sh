#!/bin/bash

export PATH=/data/predict1/miniconda3/bin:$PATH
export PYTHONPATH=/data/predict1/nda-tools/

_help()
{
    echo """Usage:
./submit.sh -u tashrif -f ndar_subject01 -n Pronet -e baseline
./submit.sh -u tashrif -f ndar_subject01 -n Prescient
./submit.sh -u tashrif -f ndar_subject01
./submit.sh -f ndar_subject01
./submit.sh -f langsamp01 -e baseline -s open

Mandatory:
-f : NDA dict name 

Optional:
-u : submitter's NDA username
-n : network
-e : event
-s : suffix

nda-submission directory is globed for \${f}_\${n}_\${e}_\${s}.csv to find files to submit
do not provide -u for only validation
"""

    exit
}


while getopts "u:f:n:e:c:s:" i
do
    case $i in
        u) user=$OPTARG ;;
        f) form=$OPTARG ;;
        n) network=$OPTARG ;;
        e) event=$OPTARG ;;
        c) collection=$OPTARG ;;
        s) suffix=$OPTARG ;;
        ?) _help ;;
    esac
done

if [ -z $form ]
then
    _help
fi


# collection=PROD-AMPSCZ
if [ -z $collection ]
then
    collection=3705
fi
# Personal Tracking Device data are collected at 4366

root=/data/predict1
datestamp=$(date +"%Y%m%d")


# look for existing submission ID
if [ -z $suffix ]
then
    event1=$event
else
    event1=${event}_${suffix}
fi

idline=`grep "$form,$event1," $root/utility/nda-transform/submission_ids.csv`
IFS=, read -ra idarray <<< "$idline"
id=${idarray[2]}
echo $id

pushd .
cd $root/to_nda/nda-submissions/network_combined/

for data in `ls ${form}*${network}*${event}*${suffix}.csv`
do
    echo Processing $data

    if [ -z $user ]
    then
        # validate only
        python $root/nda-tools/NDATools/clientscripts/vtcmd.py \
        $data

    else
        # validate and submit
        title=`basename ${data/.csv/}`

        if [ -z $id ]
        then
            python $root/nda-tools/NDATools/clientscripts/vtcmd.py \
            -u $user -t $title -d $title \
            -c $collection \
            -b $data
        else
            # -t and -d are disallowed with --replace-submission
            python $root/nda-tools/NDATools/clientscripts/vtcmd.py \
            -u $user \
            --replace-submission $id \
            -f \
            -b $data
        fi

        
    fi

    echo ''
    # the wait maybe useful
    sleep 15
done

popd


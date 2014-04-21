#!/bin/bash

# Change to code directory and activate the VEnv.
if [[ $HOSTNAME == "ip-172-31-29-49" ]];then
    cd /home/ubuntu/oposod
    source /home/ubuntu/environs/1337/bin/activate || exit 2
    REDIRECT=/dev/null
else
    cd /home/kronos/repos/oposod
    source ~/environs/envop/bin/activate || exit 2
    REDIRECT=/tmp/publisher.log
fi

# Create procs for users that have come online in the last time delta.
for i in $(echo "SDIFF online:users channels:live" | redis-cli -n 9 | awk '{print $1}');do
    #echo "Run proc for user " $i
    nohup python utils/pubsub_client.py $i > /tmp/python_${i}.log &
    echo $! > /var/tmp/rtc_${i}
    echo "SADD channels:live $i" | redis-cli -n 9 &>$REDIRECT
done

# Reap the procs for users who've gone offline in the last time delta.
for i in $(echo "SDIFF channels:live online:users" | redis-cli -n 9 | awk '{print $1}');do
    #echo "Kill proc for user" $i
    # TODO Kill signal is SIGKILL for now, test and implement something more subtle later on
    kill -9 $(cat /var/tmp/rtc_${i})
    rm /var/tmp/rtc_${i}
    echo "SREM channels:live $i" | redis-cli -n 9 &>$REDIRECT
done

exit 0

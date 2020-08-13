#!/bin/bash
echo "Nginx";
sudo service nginx stop
# kill supervisor
supervisorpid=$(cat "/tmp/supervisord.pid");
if [ -z "$supervisorpid" ]
then
    # no pid to kill
    echo "\$supervisorpid is empty"
else
    # kill process
    echo "Supervisor";
    echo $supervisorpid;
    # use pid to kill process
    sudo kill -9 $supervisorpid;
    sudo pkill supervisor;
fi

# kill gunicorn process
# get pid from file
gunicornpid=$(cat "/tmp/gunicorn.pid");

if [ -z "$gunicornpid" ]
then
    # no pid to kill
    echo "\$gunicornpid is empty"
else
    echo "Gunicorn";
    echo $gunicornpid;
    # use pid to kill process
    sudo kill -9 $gunicornpid;
    sudo pkill gunicorn;
fi

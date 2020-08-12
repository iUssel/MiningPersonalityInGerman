#!/bin/bash
# start webserver
sudo service nginx start
# start supervisor which starts gunicorn
sudo supervisord -c miping-gunicorn.conf

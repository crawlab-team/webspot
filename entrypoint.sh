#!/bin/sh
set -e

# Start ssh
service ssh start

# Start supervisor
supervisord -c /etc/supervisor/supervisord.conf

# Run main.py with argument
python main.py $1

#!/bin/sh
echo "Starting $NAME as `whoami`"

# Activate the virtual environment.
. /{{ user }}/{{ project_name }}/bin/activate

# Set environment variables
. /{{ user }}/{{ project_name }}/.env

# Create the run directory if it doesn't exist.
SOCKFILE=/{{ user }}/{{ project_name }}/run/gunicorn.sock
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

cd /{{ user }}/{{ project_name }}/src/

exec /{{ user }}/{{ project_name }}/bin/gunicorn \
    --name "{{ project_name }}" \
    --workers 2 \
    --max-requests 0 \
    --timeout 30 \
    --user {{ user }} \
    --group {{ group }} \
    --bind unix:$SOCKFILE \
    --error-logfile /var/logs/gunicorn/{{ project_name }}_error.log \
    --access-logfile /var/logs/gunicorn/{{ project_name }}_access.log \
    {{ project_name }}.wsgi

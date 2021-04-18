#!/bin/bash

# Start the run once job.
echo "Docker container has been started"

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

# Setup a cron schedule
echo "SHELL=/bin/bash
BASH_ENV=/container.env
* * * * * /usr/local/bin/python3 /app/downloader/downloader.py get_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
* * * * * /usr/local/bin/python3 /app/downloader/downloader.py clean_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
* * * * * /usr/local/bin/python3 /app/downloader/downloader.py get_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
* * * * * /usr/local/bin/python3 /app/downloader/downloader.py clean_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
# This extra line makes it a valid cron" > scheduler

crontab scheduler
cron -f
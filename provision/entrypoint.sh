#!/bin/bash

while true;
do
python3 /app/downloader/downloader.py get_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
sleep 10;

python3 /app/downloader/downloader.py clean_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
sleep 10;

python3 /app/downloader/downloader.py get_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
sleep 10;

python3 /app/downloader/downloader.py clean_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
sleep 10;
done
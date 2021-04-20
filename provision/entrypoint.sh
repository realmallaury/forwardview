#!/bin/bash

sleep 180;

while true;
do
python3 /app/downloader/downloader.py get_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
sleep 5;

python3 /app/downloader/downloader.py get_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
sleep 5;

python3 /app/downloader/downloader.py clean_ticker_list > /proc/1/fd/1 2>/proc/1/fd/2
sleep 5;

python3 /app/downloader/downloader.py clean_ticker_data > /proc/1/fd/1 2>/proc/1/fd/2
sleep 5;
done
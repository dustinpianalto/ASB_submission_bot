#!/bin/bash

until python /home/dusty/bin/ASB_submission_bot/bot.py; do
	echo "Submitter shutdown with error: $?. Restarting..." >&2
	sleep 1
done
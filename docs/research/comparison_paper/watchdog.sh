#!/bin/bash
# Keep the sweep alive until the collection is complete.
#
# run_sweep.sh restarts the collector when it dies. Nothing restarted
# run_sweep.sh, and whatever ends these background processes without a
# traceback ended two sweeps already. This watches for three failures and
# handles each:
#
#   the wrapper is gone          -> relaunch it
#   the wrapper lives but the log has not grown in six minutes -> kill and
#                                   relaunch (a hang leaves no other trace)
#   all 39 year files exist      -> stop
#
# Restarting is safe at any moment because the collector skips a year whose
# file is already written.
cd "$(dirname "$0")"
LOG=/tmp/claude-0/-home-user-saudi-legal-corpus-ai/ab365ba7-7041-5d73-b3b3-5bc7db4bbdb5/scratchpad/sweep3.log
STALL=360
last_size=0
last_change=$(date +%s)

while :; do
  n=$(ls uk_collection/*.json 2>/dev/null | wc -l)
  [ "$n" -ge 39 ] && { echo "COMPLETE: $n year files"; exit 0; }

  size=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
  now=$(date +%s)
  if [ "$size" != "$last_size" ]; then
    last_size=$size; last_change=$now
  fi

  alive=no
  [ -f /tmp/sweep3.pid ] && kill -0 "$(cat /tmp/sweep3.pid)" 2>/dev/null && alive=yes

  if [ "$alive" = no ]; then
    echo "$(date -u +%H:%M:%S) wrapper gone at $n files --- relaunching"
    nohup ./run_sweep.sh >> "$LOG" 2>&1 &
    echo $! > /tmp/sweep3.pid
    last_change=$(date +%s)
  elif [ $((now - last_change)) -gt $STALL ]; then
    echo "$(date -u +%H:%M:%S) no log growth for ${STALL}s at $n files --- restarting"
    pkill -f "python3 collect_uk.py --years" 2>/dev/null
    kill "$(cat /tmp/sweep3.pid)" 2>/dev/null
    sleep 3
    nohup ./run_sweep.sh >> "$LOG" 2>&1 &
    echo $! > /tmp/sweep3.pid
    last_change=$(date +%s)
  fi
  sleep 45
done

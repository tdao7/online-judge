#!/bin/bash
set -e
PROJECT_ROOT="/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-judge"
PID_FILE="$PROJECT_ROOT/runbridged.pid"
LOG_FILE="$PROJECT_ROOT/runbridged.log"
PYTHON="$PROJECT_ROOT/venv/bin/python"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Bridge daemon is already running (PID: $(cat "$PID_FILE"))."
    exit 0
fi

# Ensure port 9999 and 9998 are not occupied
if lsof -i :9999 >/dev/null 2>&1; then
    echo "ERROR: Port 9999 is already in use by another process."
    exit 1
fi
if lsof -i :9998 >/dev/null 2>&1; then
    echo "ERROR: Port 9998 is already in use by another process."
    exit 1
fi

echo "Starting DMOJ bridge daemon..."
cd "$PROJECT_ROOT"
nohup "$PYTHON" manage.py runbridged > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

# Wait up to 10 seconds for bridge to bind to 9999 and 9998
for i in {1..20}; do
    if nc -z 127.0.0.1 9999 && nc -z 127.0.0.1 9998; then
        echo "Bridge daemon successfully started and listening on 9999 and 9998 (PID: $(cat "$PID_FILE"))."
        exit 0
    fi
    sleep 0.5
done

echo "ERROR: Bridge daemon failed to bind to ports within 10 seconds. Check $LOG_FILE:"
tail -n 20 "$LOG_FILE"
exit 1

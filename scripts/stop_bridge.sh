#!/bin/bash
PROJECT_ROOT="/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-judge"
PID_FILE="$PROJECT_ROOT/runbridged.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "No bridge PID file found at $PID_FILE."
    exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping bridge daemon (PID: $PID)..."
    kill -TERM "$PID"
    for i in {1..20}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "Bridge daemon stopped cleanly."
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 0.5
    done
    echo "Force killing bridge daemon..."
    kill -9 "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "Bridge daemon terminated."
else
    echo "Process $PID is not running. Cleaning up stale PID file."
    rm -f "$PID_FILE"
fi

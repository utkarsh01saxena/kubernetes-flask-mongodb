#!/bin/bash

TARGET_URL=${1:-"http://localhost:5000"}
CONCURRENCY=${2:-20}
DURATION_SECONDS=${3:-120}

echo "================================================================="
echo "Starting Load Generator for HPA Testing"
echo "Target URL:       $TARGET_URL"
echo "Concurrency:      $CONCURRENCY concurrent threads"
echo "Duration:         $DURATION_SECONDS seconds"
echo "================================================================="

if command -v hey &> /dev/null; then
    hey -z "${DURATION_SECONDS}s" -c "$CONCURRENCY" -m GET "$TARGET_URL/"
    exit 0
fi

if command -v ab &> /dev/null; then
    ab -t "$DURATION_SECONDS" -c "$CONCURRENCY" "$TARGET_URL/"
    exit 0
fi

END_TIME=$((SECONDS + DURATION_SECONDS))

# Sends continuous HTTP GET requests in a loop until the duration expires
worker() {
    while [ $SECONDS -lt $END_TIME ]; do
        curl -s -o /dev/null -w "%{http_code}\n" "$TARGET_URL/" > /dev/null
    done
}

for i in $(seq 1 "$CONCURRENCY"); do
    worker &
done

wait
echo "Load test completed."

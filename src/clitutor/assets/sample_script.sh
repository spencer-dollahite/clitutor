#!/usr/bin/env bash
# sample_script.sh - A sample shell script for learning purposes
# This script demonstrates basic scripting concepts

# Variables
GREETING="Hello"
NAME="${1:-World}"

# Function definition
say_hello() {
    local target="$1"
    echo "${GREETING}, ${target}!"
}

# Conditional logic
if [[ -z "$NAME" ]]; then
    echo "Usage: $0 <name>"
    exit 1
fi

# Loop example
for i in 1 2 3; do
    say_hello "$NAME (attempt $i)"
done

# Exit with success
echo "Script completed successfully."
exit 0

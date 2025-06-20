#!/bin/bash

# Usage: ./scp_source_dirs.sh <user>@<host>:/remote/path [source_files.json]
# Example: ./scp_source_dirs.sh user@192.168.1.100:/home/user/data

REMOTE_DEST="$1"
SOURCE_JSON="${2:-analysis_result.json}"

if [ -z "$REMOTE_DEST" ]; then
  echo "Usage: $0 <user>@<host>:/remote/path [source_files.json]"
  exit 1
fi

# jqが無い場合はエラー表示して終了
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not installed. Please install jq (e.g., sudo apt-get install jq)."
  exit 2
fi

# Extract unique directories from source_files in the JSON
DIRS=$(jq -r '.source_files[]' "$SOURCE_JSON" | sort | uniq)

for dir in $DIRS; do
  echo "Sending $dir to $REMOTE_DEST"
  scp -o BatchMode=yes -r "$dir" "$REMOTE_DEST"
done

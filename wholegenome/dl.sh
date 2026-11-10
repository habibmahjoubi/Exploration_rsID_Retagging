#!/bin/bash
# resumable download: dl.sh <url> <out>; loops until local size == remote Content-Length
url=$1; out=$2
size=$(curl -sIL "$url" | grep -i '^content-length' | tail -1 | tr -dc 0-9)
while [ "$(stat -c %s "$out" 2>/dev/null || echo 0)" != "$size" ]; do
  curl -s -L -C - --retry 20 --retry-delay 10 --retry-all-errors -o "$out" "$url"
  sleep 5
done
echo "$out complete $size"

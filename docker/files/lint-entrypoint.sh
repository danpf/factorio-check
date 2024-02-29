#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "$#"
	echo "Usage: $0 <directory>"
	exit 1
fi

TARGET_DIR=$1

if [ ! -d "$TARGET_DIR" ]; then
	echo "Directory $TARGET_DIR does not exist."
	exit 1
fi

lua-language-server --check "$TARGET_DIR" --configpath /opt/factorio/luarc.json || echo "lua-language-server command failed" && exit 1
CHECK_FILE="/opt/luals/lua-language-server/log/check.json"
if [ -f $CHECK_FILE ]; then
	echo "Linting complete: Errors found!"
	jq -r '. as $root | to_entries[] | .key as $filename | .value | unique[] | "\($filename) code: \(.code), message: \(.message), severity: \(.severity), source: \(.source), line:char-range: \(.range.start.line):\(.range.start.character)-\(.range.end.line):\(.range.end.character)"' $CHECK_FILE
	exit 1
fi
echo "Linting complete: No errors found"

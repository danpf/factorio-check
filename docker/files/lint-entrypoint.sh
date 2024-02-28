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

cp /opt/factorio/luarc.json "$TARGET_DIR/.luarc.json"
cd "$TARGET_DIR" || exit 1
lua-language-server --check .
CHECK_FILE="/opt/luals/lua-language-server/log/check.json"
if [ -f $CHECK_FILE ]; then
	cat $CHECK_FILE
	exit 1
fi

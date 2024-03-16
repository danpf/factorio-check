#!/bin/bash

# lua-language-server requires absolute path
get_absolute_path() {
	local relative_path="$1"
	local absolute_path
	absolute_path=$(python -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$relative_path");
	echo "$absolute_path"
}

if [ "$MODE" = "LINT" ]; then
	# Required arguments:
	# MODE
	# TARGET_PATH
	echo "MODE is set to LINT."
	if [ -z "$TARGET_PATH" ]; then
		echo "TARGET_PATH environment variable is not set."
		exit 1
	fi
	ABSOLUTE_TARGET_PATH=$(get_absolute_path $TARGET_PATH)
	if [ ! -d "$ABSOLUTE_TARGET_PATH" ]; then
		echo "Directory $ABSOLUTE_TARGET_PATH does not exist."
		exit 1
	fi
	echo "running command: lua-language-server --check "$ABSOLUTE_TARGET_PATH" --configpath /opt/factorio/luarc.json"
	lua-language-server --check "$ABSOLUTE_TARGET_PATH" --configpath /opt/factorio/luarc.json
	if [ $? -ne 0 ]; then
		echo "lua-language-server command failed."
		exit 1
	fi

	CHECK_FILE="/opt/luals/lua-language-server/log/check.json"
	if [ -f $CHECK_FILE ]; then
		echo "Linting complete: Errors found!"
		jq -r '. as $root | to_entries[] | .key as $filename | .value | unique[] | "\($filename) code: \(.code), message: \(.message), severity: \(.severity), source: \(.source), line:char-range: \(.range.start.line):\(.range.start.character)-\(.range.end.line):\(.range.end.character)"' $CHECK_FILE
		exit 1
	fi

	echo "Linting complete: No errors found"
elif [ "$MODE" = "TEST" ]; then
	# Required arguments:
	# MODE
	# Note: python script parses environment variables for you
	use_box64_arg=""
	if [ "$PLATFORM" = "linux/arm64" ]; then
		use_box64_arg="--use_box64"
	fi
	echo "Running: run-factorio-test --factorio_executable /opt/factorio/bin/x64/factorio $use_box64_arg"
	run-factorio-test --factorio_executable /opt/factorio/bin/x64/factorio $use_box64_arg
fi

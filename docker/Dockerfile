FROM debian:12-slim

LABEL maintainer="https://github.com/danpf/factorio-docker"

ARG USER=factorio
ARG GROUP=factorio
ARG PUID=845
ARG PGID=845

# version checksum of the archive to download
ARG VERSION
ARG SHA256

# number of retries that curl will use when pulling the headless server tarball
ARG CURL_RETRIES=8

ENV PORT=34197 \
    RCON_PORT=27015 \
    VERSION=${VERSION} \
    SHA256=${SHA256} \
    SAVES=/factorio/saves \
    CONFIG=/factorio/config \
    MODS=/factorio/mods \
    SCENARIOS=/factorio/scenarios \
    SCRIPTOUTPUT=/factorio/script-output \
    PUID="$PUID" \
    PGID="$PGID"

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]
RUN set -ox pipefail \
    && if [[ "${VERSION}" == "" ]]; then \
        echo "build-arg VERSION is required" \
        && exit 1; \
    fi \
    && if [[ "${SHA256}" == "" ]]; then \
        echo "build-arg SHA256 is required" \
        && exit 1; \
    fi \
    && archive="/tmp/factorio_headless_x64_$VERSION.tar.xz" \
    && mkdir -p /opt /factorio \
    && apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get -qy install file ca-certificates curl jq pwgen xz-utils python3 python3-pip python3-venv vim --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL "https://www.factorio.com/get-download/$VERSION/headless/linux64" -o "$archive" --retry $CURL_RETRIES\
    && echo "$SHA256  $archive" | sha256sum -c \
    || (sha256sum "$archive" && file "$archive" && exit 1) \
    && tar xf "$archive" --directory /opt \
    && chmod ugo=rwx /opt/factorio \
    && rm "$archive" \
    && ln -s "$SCENARIOS" /opt/factorio/scenarios \
    && ln -s "$SAVES" /opt/factorio/saves \
    && mkdir -p /opt/factorio/config/ \
    && addgroup --system --gid "$PGID" "$GROUP" \
    && adduser --system --uid "$PUID" --gid "$PGID" --no-create-home --disabled-password --shell /bin/sh "$USER" \
    && chown -R "$USER":"$GROUP" /opt/factorio /factorio

COPY docker/files/*.sh /
COPY docker/files/server-settings.json /opt/factorio/server-settings.json
COPY docker/files/config.ini /opt/factorio/config/config.ini


# Factorio Check below here
VOLUME /factorio
EXPOSE $PORT/udp $RCON_PORT/tcp
# ENTRYPOINT ["/docker-entrypoint.sh"]

RUN apt-get -q update && apt-get install -y wget git nodejs npm ninja-build
# SHA specified until next lua-language-server release
RUN mkdir /opt/luals && cd /opt/luals \
	&& git clone https://github.com/LuaLS/lua-language-server \
	&& cd lua-language-server \
	&& git checkout 21d20b1522d2e76cb511b016d90dbd89d2acdcbc \
	&& git submodule update --init --recursive \
	&& ./make.sh
ENV PATH="${PATH}:/opt/luals/lua-language-server/bin"
RUN mkdir -p /opt/ \
	&& git clone --depth 1 --branch 1.1.41 https://github.com/justarandomgeek/vscode-factoriomod-debug.git /opt/vscode-factoriomod-debug \
	&& mkdir /opt/factorio-api-gen \
	&& cd /opt/factorio-api-gen \
	&& npm i factoriomod-debug \
	&& wget "https://lua-api.factorio.com/$VERSION/runtime-api.json" \
	&& wget "https://lua-api.factorio.com/$VERSION/prototype-api.json" \
	&& ./node_modules/.bin/fmtk sumneko-3rd -d runtime-api.json -p prototype-api.json
RUN <<EOF cat >> .luarc.json
{
	"misc": {
		"parameters": ["--develop=true"]
	},
	"diagnostics": {
		"libraryFiles": "Disable"
	},
	"workspace": {
		"checkThirdParty": false,
		"preloadFileSize": 1000,
		"maxPreload": 2000,
		"library": [
			"/opt/factorio/data",
			"/opt/factorio-api-gen",
			"/opt/vscode-factoriomod-debug/luals-addon/factorio/factorio-plugin"
		],
		"ignoreDir": [
			"/opt/vscode-factoriomod-debug/.vscode",
			"/opt/vscode-factoriomod-debug/test/factorio",
			"/opt/vscode-factoriomod-debug/luals-addon/factorio/library"
		]
	},
	"runtime": {
		"plugin": "/opt/vscode-factoriomod-debug/luals-addon/factorio/plugin.lua"
	}
}
EOF
RUN <<EOF cat >> /opt/luals/lua-language-server/log/trusted
/opt/vscode-factoriomod-debug/luals-addon/factorio/plugin.lua
EOF

RUN <<EOF cat >> /usr/local/bin/entrypoint.sh
#!/bin/bash

if [ "\$#" -ne 1 ]; then
	echo "\$#"
	echo "Usage: \$0 <directory>"
	exit 1
fi

TARGET_DIR=\$1

if [ ! -d "\$TARGET_DIR" ]; then
	echo "Directory \$TARGET_DIR does not exist."
	exit 1
fi

cp /.luarc.json "\$TARGET_DIR"
cd "\$TARGET_DIR"
lua-language-server --check .
CHECK_FILE="/opt/luals/lua-language-server/log/check.json"
if [ -f \$CHECK_FILE ]; then
	cat \$CHECK_FILE
	exit 1
fi
EOF

RUN chmod +x /usr/local/bin/entrypoint.sh

COPY src/python/factorio_check /tmp/factorio_check
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir /tmp/factorio_check  \
	&& mkdir /opt/factorio-check-examples
COPY src/lua/factorio-check /opt/factorio/mods/factorio-check
COPY src/lua/simple-scenario /opt/factorio-check-examples/simple-scenario
COPY src/lua/simple-mod /opt/factorio-check-examples/simple-mod

ENV VIRTUAL_ENV /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

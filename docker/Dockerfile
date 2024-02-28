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
	&& mkdir -p $SCENARIOS \
	&& mkdir -p $MODS \
	&& mkdir -p $SAVES \
    && mkdir -p $SCRIPTOUTPUT \
    && archive="/tmp/factorio_headless_x64_$VERSION.tar.xz" \
    && mkdir -p /opt /factorio \
    && apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get -qy install build-essential file ca-certificates curl jq pwgen xz-utils python3 python3-pip python3-venv vim wget git nodejs npm ninja-build --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL "https://www.factorio.com/get-download/$VERSION/headless/linux64" -o "$archive" --retry $CURL_RETRIES\
    && echo "$SHA256  $archive" | sha256sum -c \
    || (sha256sum "$archive" && file "$archive" && exit 1) \
    && tar xf "$archive" --directory /opt \
    && chmod ugo=rwx /opt/factorio \
    && rm "$archive" \
    && ln -s "$SCENARIOS" /opt/factorio/scenarios \
    && ln -s "$MODS" /opt/factorio/mods \
    && ln -s "$SAVES" /opt/factorio/saves \
    && ln -s "$SCRIPTOUTPUT" /opt/factorio/script-output \
    && mkdir -p /opt/factorio/config/ \
    && addgroup --system --gid "$PGID" "$GROUP" \
    && adduser --system --uid "$PUID" --gid "$PGID" --no-create-home --disabled-password --shell /bin/sh "$USER" \
    && chown -R "$USER":"$GROUP" /opt/factorio /factorio

VOLUME /factorio
EXPOSE $PORT/udp $RCON_PORT/tcp
# ENTRYPOINT ["/docker-entrypoint.sh"]

# (Mostly) Factorio Check below here

# SHA specified until next lua-language-server release
RUN mkdir /opt/luals \
	&& cd /opt/luals \
	&& git clone https://github.com/LuaLS/lua-language-server \
	&& cd lua-language-server \
	&& git checkout 21d20b1522d2e76cb511b016d90dbd89d2acdcbc \
	&& git submodule update --init --recursive \
	&& ./make.sh \
	&& echo "/opt/vscode-factoriomod-debug/luals-addon/factorio/plugin.lua" > /opt/luals/lua-language-server/log/trusted \
	&& mkdir -p /opt/ \
	&& git clone --depth 1 --branch 1.1.41 https://github.com/justarandomgeek/vscode-factoriomod-debug.git /opt/vscode-factoriomod-debug \
	&& mkdir /opt/factorio-api-gen \
	&& cd /opt/factorio-api-gen \
	&& npm i factoriomod-debug \
	&& wget -q "https://lua-api.factorio.com/$VERSION/runtime-api.json" \
	&& wget -q "https://lua-api.factorio.com/$VERSION/prototype-api.json" \
	&& ./node_modules/.bin/fmtk sumneko-3rd -d runtime-api.json -p prototype-api.json \
	&& cd / \
	&& mkdir /opt/factorio-check-examples

COPY docker/files/*.sh /usr/local/bin/
COPY docker/files/server-settings.json /opt/factorio/server-settings.json
COPY docker/files/config.ini /opt/factorio/config/config.ini
COPY docker/files/luarc.json /opt/factorio

COPY src/lua/factorio-check /opt/factorio/mods/factorio-check
COPY src/lua/simple-scenario /opt/factorio-check-examples/simple-scenario
COPY src/lua/simple-mod /opt/factorio-check-examples/simple-mod

COPY src/python/factorio_check /tmp/factorio_check

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir /tmp/factorio_check  \
	&& rm -rf /tmp/factorio_check

ENV VIRTUAL_ENV /opt/venv
ENV PATH="/opt/venv/bin:$PATH:/opt/luals/lua-language-server/bin"

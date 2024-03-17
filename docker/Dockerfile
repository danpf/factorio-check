
FROM debian:12-slim as pybuilder
RUN apt-get -qq update \
	&& DEBIAN_FRONTEND=noninteractive apt-get -qqy install python3 python3-pip python3-venv git

COPY . /tmp/factorio-check
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install pipx  \
    && /opt/venv/bin/pipx run build --sdist /tmp/factorio-check/src/python/factorio_check

FROM debian:12-slim

LABEL maintainer="https://github.com/danpf/factorio-check"

ARG USER=factorio
ARG GROUP=factorio
ARG PUID=845
ARG PGID=845
ARG BOX64_VERSION=v0.2.4

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
    && apt-get -qq update \
    && DEBIAN_FRONTEND=noninteractive apt-get -qqy install build-essential file ca-certificates curl jq pwgen xz-utils procps python3 python3-pip python3-venv vim wget git nodejs npm ninja-build \
    && if [[ "$(uname -m)" == "aarch64" ]]; then \
        echo "installing ARM compatibility layer" \
        && DEBIAN_FRONTEND=noninteractive apt-get -qqy install unzip --no-install-recommends \ 
        && curl -LO https://github.com/ptitSeb/box64/releases/download/${BOX64_VERSION}/box64-GENERIC_ARM-RelWithDebInfo.zip \
        && unzip box64-GENERIC_ARM-RelWithDebInfo.zip -d /bin \
        && rm -f box64-GENERIC_ARM-RelWithDebInfo.zip \
        && chmod +x /bin/box64; \
    fi \
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

COPY --from=pybuilder /tmp/factorio-check/src/python/factorio_check/dist /tmp/fc_dist
COPY docker/files/*.sh /usr/local/bin/
COPY docker/files/server-settings.json /opt/factorio/server-settings.json
COPY docker/files/config.ini /opt/factorio/config/config.ini
COPY docker/files/luarc.json /opt/factorio

COPY src/lua/factorio-check /opt/factorio/mods/factorio-check
COPY src/lua/simple-scenario /opt/factorio-check-examples/simple-scenario
COPY src/lua/simple-mod /opt/factorio-check-examples/simple-mod

COPY src/python/factorio_check /tmp/factorio_check

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir /tmp/fc_dist/*.tar.gz  \
	&& rm -rf /tmp/fc_dist/

ENV VIRTUAL_ENV /opt/venv
ENV PATH="/opt/venv/bin:$PATH:/opt/luals/lua-language-server/bin"
ENTRYPOINT ["entrypoint.sh"]

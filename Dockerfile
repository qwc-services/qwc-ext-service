ARG BASE_TAG=latest
FROM sourcepole/qwc-uwsgi-base:alpine-$BASE_TAG

ARG UPDATE_DEPS=false

WORKDIR /srv/qwc_service

COPY pyproject.toml uv.lock ./

# git: Required for pip with git repos
RUN \
    apk add --no-cache --update --virtual build-deps git && \
    if [ "${UPDATE_DEPS}" = "true" ]; then \
        uv lock --upgrade; \
    fi && \
    uv sync --frozen && \
    uv cache clean && \
    apk del build-deps

COPY src /srv/qwc_service/

ENV SERVICE_MOUNTPOINT=/api/v1/ext

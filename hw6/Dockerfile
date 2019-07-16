FROM python:3.7-slim

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

COPY ./requirements.txt ./scripts/* /
RUN DEPS="libpq-dev" \
    && BUILD_DEPS="build-essential libpcre3-dev" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $DEPS $BUILD_DEPS \
    && pip install --no-cache-dir -q -r requirements.txt \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false build-essential libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

EXPOSE 8000
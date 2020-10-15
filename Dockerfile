FROM tiangolo/meinheld-gunicorn:python3.8-alpine3.11
LABEL maintainer="Leonardo Tredese <leonardo.tredese@lnl.infn.it"
COPY . /app
RUN apk add build-base cmake libssh2-dev; \
	pip3 install -r /app/requirements.txt;\
    apk del build-base cmake libssh2-dev

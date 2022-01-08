FROM sourcepole/qwc-uwsgi-base:alpine-v2022.01.08

ADD . /srv/qwc_service
RUN pip3 install --no-cache-dir -r /srv/qwc_service/requirements.txt

ENV SERVICE_MOUNTPOINT=/api/v1/ext

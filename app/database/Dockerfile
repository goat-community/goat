FROM goatcommunity/database:12-3-2.6.11-custom-2.3.14

ENV APP_PATH /opt
WORKDIR ${APP_PATH}

COPY ./database $APP_PATH

RUN mkdir -p ${APP_PATH}/config
COPY ./config $APP_PATH/config

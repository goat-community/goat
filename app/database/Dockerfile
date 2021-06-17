FROM goatcommunity/database:test-release

ENV APP_PATH /opt
WORKDIR ${APP_PATH}

COPY ./database $APP_PATH

RUN mkdir -p ${APP_PATH}/config
COPY ./config $APP_PATH/config

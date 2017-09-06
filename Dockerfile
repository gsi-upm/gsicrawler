from node:7.10.0

ENV NODE_PATH=/tmp/node_modules APP_NAME=gsi-crawler

# Install dependencies first to use cache

RUN apt-get update && apt-get install -y gettext

RUN npm install -g http-server bower

WORKDIR /usr/src/app/

ADD bower.json /usr/src/app/bower.json

# Install the application, move the resulting libraries to /usr/src (so it doesn't get overwritten when
# mounting it as a volue, and link to it.
RUN bower install --allow-root  && mv bower_components .. && ln -s /usr/src/bower_components /usr/src/app/

ADD . /usr/src/app


CMD ["/usr/src/app/init.sh"]

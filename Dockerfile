FROM node:10
COPY web/package.json /code/package.json
RUN npm install --quiet
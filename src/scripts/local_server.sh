# Running migrations
cd ./src || exit
alembic upgrade head
cd - || exit


# Waiting for database service to be up
 # the image must match the currently used postgres image
IMAGE_NAME=postgres:17-alpine

# shellcheck disable=SC2046
until [ $(docker inspect -f '{{json .State.Status }}' $(docker ps -a --filter ancestor=$IMAGE_NAME --format="{{.ID}}" | head -n 1)) == '"running"' ];
do
    echo "Waiting for database container to start..." && sleep 1;
done


# Running fastapi dev server
if [[ $RELOAD = "True" ]]; then
  fastapi dev ./src/main.py --port "${PORT:-8000}" --host "${HOST:-127.0.0.1}"  --reload
else
  fastapi dev ./src/main.py --port "${PORT:-8000}" --host "${HOST:-127.0.0.1}"  --no-reload
fi;

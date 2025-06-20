# Running migrations
SRC_FOLDER=src

cd $SRC_FOLDER || true
alembic upgrade head
cd - || true


# Waiting for database service to be up
 # the image must match the currently used postgres image
IMAGE_NAME=postgres:17-alpine
db_container_id="$(docker ps -a --filter ancestor=$IMAGE_NAME --format="{{.ID}}" | head -n 1)"

# shellcheck disable=SC2046
until [ $(docker inspect -f '{{json .State.Status }}' $db_container_id) != "running" ];
do
    echo "Waiting for database container to start..." && sleep 1;
done

main_file=main.py
if [ -d "$SRC_FOLDER" ]; then
  main_file="$SRC_FOLDER/$main_file"
fi;

# Running fastapi dev server
if [[ $RELOAD = "True" ]]; then
  fastapi dev $main_file --port "${PORT:-8000}" --host "${HOST:-127.0.0.1}"  --reload
else
  fastapi dev $main_file --port "${PORT:-8000}" --host "${HOST:-127.0.0.1}"  --no-reload
fi;

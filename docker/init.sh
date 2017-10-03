mkdir -p kafka-ex/{data,logs} && cd kafka-ex
docker run -d --name zookeeper --publish 2181:2181 zookeeper:3.4
docker run -d \
    --hostname localhost \
    --name kafka \
    --publish 9092:9092 --publish 7203:7203 \
    --env KAFKA_ADVERTISED_HOST_NAME=127.0.0.1 \
    ches/kafka
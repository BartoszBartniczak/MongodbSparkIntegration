docker-machine create -d virtualbox --virtualbox-boot2docker-url=https://github.com/AkihiroSuda/boot2docker/releases/download/v1.9.1-fix1/boot2docker-v1.9.1-fix1.iso --virtualbox-memory 4096 --virtualbox-cpu-count 4 default

docker run --name mongo -d mongo
docker start mongo

docker run -it --net ist --rm mongo sh -c 'exec mongo "$MONGO_PORT_27017_TCP_ADDR:$MONGO_PORT_27017_TCP_PORT/test"'


docker run -d --name=master --hostname=master --net=ist ist_spark -dm
docker run -d --name=slave1 --hostname=slave1 --net=ist ist_spark -ds
docker run -d --name=slave2 --hostname=slave2 --net=ist ist_spark -ds
docker run -d --name=slave3 --hostname=slave3 --net=ist ist_spark -ds
docker run -d --name=slave4 --hostname=slave4 --net=ist ist_spark -ds

docker run -it --name=code --hostname=code --rm -v /Users/andrzej.nowicki/zed/MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter
docker run -it --rm -v /Users/andrzej.nowicki/zed/MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter python /code/countTweets.py


docker run -it --rm --net=ist ist_spark /usr/local/spark/bin/pyspark --packages com.stratio.datasource:spark-mongodb_2.10:0.10.3 --master spark://master:7077 --num-executors 5 --driver-memory 512m --executor-memory 512m
from pyspark.sql import SQLContext
sqlContext.sql("CREATE TEMPORARY TABLE tweets USING com.stratio.datasource.mongodb OPTIONS (host 'mongo:27017', database 'tweets', collection 'tweets')")
x = sqlContext.sql("SELECT text FROM tweets")
words=x.flatMap(lambda x: '' if x.text == None else x.text.split())
wordcounts = words.map(lambda x: (x, 1)).reduceByKey(lambda x,y:x+y).map(lambda x:(x[1],x[0])).sortByKey(False)
wordcounts.take(20)
#for i in x.collect():
#        print i

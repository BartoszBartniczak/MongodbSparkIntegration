# Spark SQL integration with MongoDB using docker

This is a project that enables you to perform SQL queries on MongoDB databases using Spark SQL.

We have also included a sample application that uses twitter API to collect tweets and use them as sample data.

There are two ways of running the application: using docker-compose or by manually running needed docker containers.

## Docker containers
* mongo -- this is a standard out-of-the box container that is running mongodb database
* ist_spark -- this is a container with libraries needed by spark tool, preconfigured for both master and slave workers
* ist_twitter -- this is a container with sample software that collects tweets and inserts them to mongodb

### Setup via docker-compose

You can run sample application by simply running:
```
docker network create ist
docker-compose up -d
```
This will automatically run mongo container, the tweeter collector as well as 3 spark containers - master and two slaves.

### Manual setup

#### Docker machine
First you need to set up the docker machine and network for the containers. You can run for example:
``` 
docker-machine create -d virtualbox --virtualbox-boot2docker-url=https://github.com/AkihiroSuda/boot2docker/releases/download/v1.9.1-fix1/boot2docker-v1.9.1-fix1.iso --virtualbox-memory 4096 --virtualbox-cpu-count 4 default
docker network create ist
```

#### MongoDB
Secondly, you need to start the mongodb container by running:
```
# if run for the first time
docker run --name mongo -d mongo --net ist
# to start already defined container
docker start mongo
```
If you want to connect to the mongo database directly, you can use the following command:
```
docker run -it --net ist --rm mongo sh -c 'exec mongo mongo:27017/tweets"'
```
#### Setting up the twitter collector
In order to run the twitter collector sample you need to setup the `MongodbSparkIntegration/config.yml` file with your twitter API keys. Then simply run the following command to start collecting the data:
```
docker build -t ist_twitter ist_twitter/
#to run it in background
docker run -d --name=code --hostname=code --rm -v MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter
#to leave it running in foreground
docker run -it --name=code --hostname=code --rm -v MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter
```

Let's have a look at the parameters:
- `-it` this enables the container to run interactively and emulate a terminal (tty), hence the name `it`
- `--rm` this parameter means that after the process finishes, the container will be destroyed
- `-v local:container` this enables a volume (shared filesystem between the host and container)
- `-w` sets the working directory
To check how many tweets you have already collected you can run:
```
docker run -it --rm -v MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter python /code/countTweets.py
```

#### Setting up the spark cluster
In order to setup the spark cluster simply run the following script:
```
docker build -t ist_spark ist_spark/

docker run -d --name=master --hostname=master --net=ist ist_spark -dm
docker run -d --name=slave1 --hostname=slave1 --net=ist ist_spark -ds
docker run -d --name=slave2 --hostname=slave2 --net=ist ist_spark -ds
docker run -d --name=slave3 --hostname=slave3 --net=ist ist_spark -ds
docker run -d --name=slave4 --hostname=slave4 --net=ist ist_spark -ds
...
```

Let's look into the parameters for this executions:
- `docker build -t tag_name directory/` command build the container from `directory/Dockerfile` and tags it with `tag_name` 
- `docker run` command creates a new container, if you want to start an existing container, simply run `docker start <container_name>`
- `-d` daemon mode (runs in background)
- `--name=master` set the name of the container
- `--hostname=master` sets the hostname of the container
- `--net=ist` sets the network to ist (all containers in the same network can be resolvable via hostname)
- `ist_spark` is the tag of the image used in container creation
- `-ds` or `-dm` is deciding if this container should act as a slave or master

## Example -- Let's have some fun

Let's assume that we have a running application and have already collected some tweets for analysis.
In order to run pyspark you can issue the following command:

```docker run -it --rm --net=ist ist_spark /usr/local/spark/bin/pyspark --packages com.stratio.datasource:spark-mongodb_2.10:0.10.3 --master spark://master:7077 --num-executors 5 --driver-memory 512m --executor-memory 512m```
Let's take a look at the command that will be executed in the container:
- `/usr/local/spark/bin/pyspark` we want to run the `pyspark` command
- `--packages com.stratio.datasource:spark-mongodb_2.10:0.10.3` we need to include a requirement for pyspark to load the spark<->mongodb connector
Before we move on to the rest of the commands let's have a look at spark architecture below:
[spark architecture](http://spark.apache.org/docs/latest/img/cluster-overview.png)
In our case, we'll use the spark standalone mode in which spark is also handling managing of the workers. Spark can also use mesos or YARN, but this is the simplest way for demonstration.
The driver program in our case is the `pyspark`, the cluster manager is the `master` container, and the worker nodes are the `slave<n>` containers.
- `--master spark://master:7077` we need to tell the driver program information about the cluster manager
- `--num-executors 5` we can modify the number of executors
- `--driver-memory 512m` we can limit memory used by the driver
- `--executor-memory 512m` we can also limit memory used by the workers

If everything went well, we should see some messages and finally an ipython prompt like that:
```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 1.5.2
      /_/

Using Python version 2.7.6 (default, Jun 22 2015 17:58:13)
SparkContext available as sc, HiveContext available as sqlContext.

In [1]:
```

We now have everything setup, let's get to work.
Let's assume we want to see what are the most popular words used in tweets from our collection of tweets.
We can run the following script:
```python
sqlContext.sql("CREATE TEMPORARY TABLE tweets USING com.stratio.datasource.mongodb OPTIONS (host 'mongo:27017', database 'tweets', collection 'tweets')")
x = sqlContext.sql("SELECT text FROM tweets WHERE lang='en'")
words=x.flatMap(lambda x: '' if x.text == None else x.text.split())
wordcounts = words.map(lambda x: (x, 1)).reduceByKey(lambda x,y:x+y).map(lambda x:(x[1],x[0])).sortByKey(False)
wordcounts.take(20)
```
What this code does it first sets up the sqlContext for spark SQL. We use the com.stratio.datasource.mongodb driver to create a temporary table that will be used by hive.

Next, we provide the query that will select the tweets for us - in our case we only filter the tweets that have attribute lang set to "en".
We then split the text of the tweet into separate words and then perform a map & reduce operations to count word occurences.
At last, we want to show the TOP20 words from our tweets collection.
# Spark SQL integration with MongoDB using docker

This is a project that enables you to perform SQL queries on MongoDB databases using Spark SQL.

Also included is a sample application that uses twitter API to collect tweets and use them as sample data.

There are two ways of running the application: using docker-compose or by manually running needed docker containers.

## Docker containers
* mongo - this is a standard out-of-the box container that is running mongodb database
* ist_spark - this is a container with libraries needed by spark tool, preconfigured for both master and slave workers
* ist_twitter - this is a container with sample software that collects tweets and inserts them to mongodb

### Setup via docker-compose

You can run the sample application by simply running:
```
docker network create ist
docker-compose up -d
```
This will automatically run mongo container, the tweeter collector as well as 3 spark containers - one master and two slaves.

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
docker run --name mongo --hostname mongo -d --net ist
# to start an already defined container
docker start mongo
```
If you want to connect to the mongo database directly, you can use the following command:
```
docker run -it --net ist --rm mongo sh -c 'exec mongo mongo:27017/tweets"'
```
#### Setting up the twitter collector
In order to run the twitter collector sample you need to setup the `MongodbSparkIntegration/config.yml` file with your twitter API keys. Then simply run the following command to start collecting the data:
```
# let's build the image for ist_twitter
docker build -t ist_twitter ist_twitter/

# to run the collection process in background
docker run -d --name=code --hostname=code --rm -v MongodbSparkIntegration/:/code --net=ist -w /code ist_twitter
 
# to run the collection process in foreground
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
# first we need to build the image
docker build -t ist_spark ist_spark/

# to run the containers for first time use:
docker run -d --name=master --hostname=master --net=ist ist_spark -dm
docker run -d --name=slave1 --hostname=slave1 --net=ist ist_spark -ds
docker run -d --name=slave2 --hostname=slave2 --net=ist ist_spark -ds
docker run -d --name=slave3 --hostname=slave3 --net=ist ist_spark -ds
docker run -d --name=slave4 --hostname=slave4 --net=ist ist_spark -ds
...

# to start the already existing containers simply run:
docker start <container_name>
```

Let's look into the parameters for this commands:
- `docker build -t tag_name directory/` build the container using `directory/Dockerfile` and tag it with `tag_name` 
- `docker run` create a new container
- `-d` daemon mode (runs in background)
- `--name=master` set the name of the container
- `--hostname=master` sets the hostname of the container
- `--net=ist` sets the network to ist (all containers in the same network can be resolvable via hostname)
- `ist_spark` is the tag of the image used in container creation
- `-ds` or `-dm` is deciding if this container should act as a slave or master

## Example - it's time to have some fun

Let's assume that we have a running application and have already collected some tweets for analysis.

We'll use `pyspark` command to run a interactive python shell that will allow us to use Spark, Spark SQL and connect to mongodb.

In order to run `pyspark` you can issue the following command:

```docker run -it --rm --net=ist ist_spark /usr/local/spark/bin/pyspark --packages com.stratio.datasource:spark-mongodb_2.10:0.10.3 --master spark://master:7077 --num-executors 5 --driver-memory 512m --executor-memory 512m```

Let's take a look at the command that will be executed in the container:
- `/usr/local/spark/bin/pyspark` we want to run the `pyspark` command
- `--packages com.stratio.datasource:spark-mongodb_2.10:0.10.3` we need to load the spark <-> mongodb connector

Before we move on to the rest of the arguments let's have a look at spark architecture below:

![spark architecture](http://spark.apache.org/docs/latest/img/cluster-overview.png)

In our case, we'll use the spark standalone mode in which spark is also managing the workers. Spark can also use Apache Mesos or YARN.

The driver program in our case is the `pyspark`, the cluster manager is the `master` container, and the worker nodes are the `slave<n>` containers.

- `--master spark://master:7077` set the cluster manager
- `--num-executors 5` set the number of executors
- `--driver-memory 512m` memory limit for the driver
- `--executor-memory 512m` memory limit for the workers (in our case 512MB each)

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

In this example we want to see what are the most popular words used in tweets from our collection.
We can run the following script:
```python
sqlContext.sql("CREATE TEMPORARY TABLE tweets USING com.stratio.datasource.mongodb OPTIONS (host 'mongo:27017', database 'tweets', collection 'tweets')")
x = sqlContext.sql("SELECT text FROM tweets WHERE lang='en'")
words=x.flatMap(lambda x: '' if x.text == None else x.text.split())
wordcounts = words.map(lambda x: (x, 1)).reduceByKey(lambda x,y:x+y).map(lambda x:(x[1],x[0])).sortByKey(False)
wordcounts.take(20)
```
While we wait for it to finish, let's dive in the commands we just issued:

```python
sqlContext.sql("CREATE TEMPORARY TABLE tweets USING com.stratio.datasource.mongodb OPTIONS (host 'mongo:27017', database 'tweets', collection 'tweets')")
```
What this code does it first sets up the table for Spark SQL using the `com.stratio.datasource.mongodb` driver. The temporary table will be accessible via Spark SQL.
```python
x = sqlContext.sql("SELECT text FROM tweets WHERE lang='en'")
```
Next we specify the query that we want to run on our set. In our case we want to get text of all tweets that have attribute lang set to "en".

```python
words=x.flatMap(lambda x: '' if x.text == None else x.text.split())
```
We need to split the text of the tweets into separate words.

```python
wordcounts = words.map(lambda x: (x, 1)).reduceByKey(lambda x,y:x+y).map(lambda x:(x[1],x[0])).sortByKey(False)
```
Next we use some magic to count the occurrences of words in the tweets.
Each word is replaced with a tuple `(word,1)`, then a reduce operation sums up occurrences of same word, so we get `(word, number_of_occurences)`.
We need to switch places, so it becomes `(number_of_occurences,word)` and then sort it descending. 

```python
wordcounts.take(20)
```
Finally, we want to show 20 most popular words from our tweets collection.



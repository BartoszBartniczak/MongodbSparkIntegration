FROM ubuntu:14.04

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update \
    && apt-get install -y python-pip python-dev
RUN apt-get install -y wget ipython build-essential python-dev python-pip openjdk-7-jdk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

ENV SPARK_VERSION 1.5.2
ENV HADOOP_VERSION 2.6

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64
ENV SPARK_HOME /usr/local/spark

ENV APACHE_MIRROR http://ftp.ps.pl/pub/apache
ENV SPARK_URL ${APACHE_MIRROR}/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz
ENV SPARK_DIR spark-${SPARK_VERSION}-bin-hadoop2.6


ENV PYSPARK_DRIVER_PYTHON /usr/bin/ipython
ENV PATH $PATH:$SPARK_HOME/bin

# Download  Spark
RUN wget -qO - ${SPARK_URL} | tar -xz -C /usr/local/ \
    && cd /usr/local && ln -s ${SPARK_DIR} spark

RUN apt-get update \
    && apt-get install -y git maven ssh
COPY pom.xml pom.xml
RUN mvn dependency:go-offline
COPY startup.sh /etc/startup.sh
RUN chown root.root /etc/startup.sh
RUN chmod 700 /etc/startup.sh
RUN mkdir /var/run/sshd

#RUN echo "spark.driver.extraClassPath   ${CLASSPATH}" > $SPARK_HOME/conf/spark-defaults.conf

ENTRYPOINT ["/etc/startup.sh"]


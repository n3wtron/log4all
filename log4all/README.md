# Log4All Server

Log management server

## Quick start with docker

### pull docker image

    docker pull n3wtron/log4all


### run docker
    
    docker run -d -e L4AL_DB_CONNECTION="mongodb://172.17.42.1/log4all" -p 9000:9000 n3wtron/log4all:latest

### Open log4all console 

[http://localhost:9000](http://localhost:9000)

## Clients

## Java
[https://github.com/n3wtron/log4all-client-java](https://github.com/n3wtron/log4all-client-java)

#### Maven

    <dependency>
        <groupId>net.log4all</groupId>
        <artifactId>log4all-client</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </dependency>

## Log4J
[https://github.com/n3wtron/log4all-client-log4j](https://github.com/n3wtron/log4all-client-log4j)

#### Maven

    <dependency>
        <groupId>net.log4all</groupId>
        <artifactId>log4all-client-log4j</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </dependency>

## AngularJS
[https://github.com/n3wtron/angular-log4all](angular-log4al)

## Python
[https://github.com/n3wtron/log4all-client-python](https://github.com/n3wtron/log4all-client-python)
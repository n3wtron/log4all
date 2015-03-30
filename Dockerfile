FROM google/golang

WORKDIR /gopath/src/log4all
ADD . /gopath/src/log4all

#ENV http_proxy="http://yyi3842:A3ides83@proxyic.icnet:38080"
#ENV https_proxy="http://yyi3842:A3ides83@proxyic.icnet:38080"

#ENV http_proxy="http://172.17.42.1:3128"
#ENV https_proxy="http://172.17.42.1:3128"


#RUN git config --global http.proxy http://172.17.42.1:3128
#RUN git config --global https.proxy http://172.17.42.1:3128
#RUN echo $http_proxy
#RUN echo $https_proxy

RUN go get -v github.com/revel/revel
RUN go get -v github.com/revel/cmd/revel
RUN go get -v github.com/dgrijalva/jwt-go
RUN go get -v gopkg.in/mgo.v2
RUN go get -v github.com/fatih/structs

ENV PATH /gopath/bin:$PATH

mkdir /log4all

RUN revel build log4all /log4all

EXPOSE 9000

ENTRYPOINT ["/log4all/run.sh"]
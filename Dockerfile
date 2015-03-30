FROM google/golang

WORKDIR /gopath/src/log4all
ADD . /gopath/src/log4all

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
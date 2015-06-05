FROM google/golang

WORKDIR /gopath/src/github.com/n3wtron/log4all/log4all
ADD . /gopath/src/github.com/n3wtron/log4all

RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get install -y nodejs
RUN npm install -g bower

RUN mkdir /log4all
RUN bower install --allow-root

RUN go get -v github.com/revel/cmd/revel
RUN go get /gopath/src/github.com/n3wtron/log4all/...

ENV PATH /gopath/bin:$PATH

RUN revel build github.com/n3wtron/log4all/log4ll /log4all

EXPOSE 9000

ENTRYPOINT ["/log4all/run.sh"]

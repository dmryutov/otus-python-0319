FROM golang:1.12-alpine as builder

RUN apk add --no-cache git

WORKDIR /go/src/app
COPY appsinstalled /go/src/appsinstalled
COPY memc_load.go .
# Dirty hack to fix relative import
RUN sed -i 's/".\/appsinstalled"/"appsinstalled"/g' memc_load.go

RUN go get -d ./...
RUN go install ./...

CMD ["app", "--pattern=/data/*.tsv.gz"]
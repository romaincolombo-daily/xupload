#!/bin/sh

xupload: *.go
	@export GOPATH=`pwd`; export GIT_SSL_NO_VERIFY=true; export CGO_ENABLED=0; go get -v -d && go build -o xupload *.go

run: xupload
	@./xupload xupload.conf

deb:
	@debuild -e GOROOT -e PATH -i -us -uc -b

clean:

distclean:
	@rm -rf xupload src

debclean:
	@debuild clean

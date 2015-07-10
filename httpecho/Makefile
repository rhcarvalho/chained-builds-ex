all: clean httpecho dockerbuild

clean:
	rm httpecho

httpecho:
	go build -ldflags "-s" -a httpecho.go

dockerbuild:
	docker build -t rhcarvalho/httpecho .

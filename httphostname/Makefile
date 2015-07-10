all: clean httphostname dockerbuild

clean:
	rm -vf httphostname

httphostname:
	go build -ldflags "-s" -a httphostname.go

dockerbuild:
	docker build -t rhcarvalho/httphostname .

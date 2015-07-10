package main

import (
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		log.Fatalf("usage: %s \"message to be echoed\"", os.Args[0])
	}
	msg := os.Args[1]
	if msg[len(msg)-1] != '\n' {
		msg += "\n"
	}
	http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
		log.Print(req.Method, req.URL)
		io.WriteString(w, msg)
	})
	log.Printf("Serving \"%s\"...", os.Args[1])
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal(err)
	}
}

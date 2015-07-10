package main

import (
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	hostname, err := os.Hostname()
	if err != nil {
		log.Fatal(err)
	}
	http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
		log.Print(req.Method, req.URL)
		io.WriteString(w, hostname)
		io.WriteString(w, "\n")
	})
	log.Printf("Serving on \"%s:8080\"...", hostname)
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal(err)
	}
}

package main

import (
	"fmt"
	"sync"
)

type Fetcher interface {
	// Fetch returns the body of URL and
	// a slice of URLs found on that page.
	Fetch(url string) (body string, urls []string, err error)
}

type fakeFetcher map[string]*fakeResult

type fakeResult struct {
	body string
	urls []string
}

func (f fakeFetcher) Fetch(url string) (string, []string, error) {
	if res, ok := f[url]; ok {
		return res.body, res.urls, nil
	}
	return "", nil, fmt.Errorf("not found: %s", url)
}

//////////////////////////////////////////////////
// three implementations of the Crawl method
//////////////////////////////////////////////////

// implementation 1, single goroutine
func CrawlSerial(url string, fetcher fakeFetcher, fetched map[string]bool) {
	if _, ok := fetched[url]; ok {
		return
	}
	fetched[url] = true
	body, urls, err := fetcher.Fetch(url)
	if err != nil {
		fmt.Println(err)
		return
	} else {
		fmt.Println("found:", url, body)
	}
	for _, u := range urls {
		CrawlSerial(u, fetcher, fetched)
	}
	return
}

//implementaion 2, parallel with mutex and waitgroup
type Record struct {
	mutex   sync.Mutex
	fetched map[string]bool
}

func (record *Record) Visited(url string) bool {
	defer record.mutex.Unlock()
	record.mutex.Lock()
	if _, ok := record.fetched[url]; ok {
		return true
	} else {
		record.fetched[url] = true
		return false
	}
}

func CrawlParallelMutex(url string, fetcher fakeFetcher, record *Record) {
	if record.Visited(url) {
		return
	}
	body, urls, err := fetcher.Fetch(url)
	if err != nil {
		fmt.Println(err)
		return
	} else {
		fmt.Println("found:", url, body)
	}
	var tasks sync.WaitGroup
	for _, url := range urls {
		tasks.Add(1)
		go func(url string) {
			defer tasks.Done()
			CrawlParallelMutex(url, fetcher, record)
		}(url)
	}
	tasks.Wait()
}

func main() {
	var f = fakeFetcher{
		"https://golang.org/": &fakeResult{
			"The Go Programming Language",
			[]string{
				"https://golang.org/pkg/",
				"https://golang.org/cmd/",
			},
		},
		"https://golang.org/pkg/": &fakeResult{
			"Packages",
			[]string{
				"https://golang.org/",
				"https://golang.org/cmd/",
				"https://golang.org/pkg/fmt/",
				"https://golang.org/pkg/os/",
			},
		},
		"https://golang.org/pkg/fmt/": &fakeResult{
			"Package fmt",
			[]string{
				"https://golang.org/",
				"https://golang.org/pkg/",
			},
		},
		"https://golang.org/pkg/os/": &fakeResult{
			"Package os",
			[]string{
				"https://golang.org/",
				"https://golang.org/pkg/",
			},
		},
	}

	fmt.Println("==========Serial Crawler=================")
	CrawlSerial("https://golang.org/", f, map[string]bool{})

	fmt.Println("==========Parallel Crawler With Mutex=================")
	CrawlParallelMutex("https://golang.org/", f, &Record{sync.Mutex{}, map[string]bool{}})
}

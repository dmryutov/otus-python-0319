package main

import (
	"bufio"
	"compress/gzip"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/bradfitz/gomemcache/memcache"
	"github.com/golang/protobuf/proto"

	"./appsinstalled"
)

const NORMAL_ERR_RATE = 0.01
const MEMCACHE_TIMEOUT = 1 * time.Second

type AppsInstalled struct {
	devType string
	devId   string
	lat     float64
	lon     float64
	apps    []uint32
}
type Options struct {
	logFile  string
	dry      bool
	pattern  string
	idfa     string
	gaid     string
	adid     string
	dvid     string
	attempts int
	buffer   int
}
type MemcacheClient struct {
	addr   string
	client *memcache.Client
}
type Result struct {
	processed int
	errors    int
}


func createMemcacheClients(options *Options) map[string]MemcacheClient {
	deviceMemc := map[string]string{
		"idfa": options.idfa,
		"gaid": options.gaid,
		"adid": options.adid,
		"dvid": options.dvid,
	}
	clients := make(map[string]MemcacheClient)
	for devType, memcAddr := range deviceMemc {
		clients[devType] = MemcacheClient{memcAddr, memcache.New(memcAddr)}
		clients[devType].client.Timeout = MEMCACHE_TIMEOUT
	}
	return clients
}


func memcacheWriter(memcCh <-chan *AppsInstalled, resultCh chan<- Result, memc *MemcacheClient,
	dryRun bool, attempts int) {
	processed, errors := 0, 0
	for ai := range memcCh {
		ok := insertAppsinstalled(memc, ai, dryRun, attempts)
		if ok {
			processed += 1
		} else {
			errors += 1
		}
	}
	resultCh <- Result{processed, errors}
	processed, errors = 0, 0
}


func memcacheSet(memc *memcache.Client, key string, value []byte, attempts int) bool {
	for i := 0; i < attempts; i++ {
		err := memc.Set(&memcache.Item{
			Key:   key,
			Value: value,
		})
		if err == nil {
			return true
		}
		time.Sleep(1 * time.Second)
	}
	return true
}


func insertAppsinstalled(memc *MemcacheClient, ai *AppsInstalled, dryRun bool, attempts int) bool {
	ua := &appsinstalled.UserApps{
		Lat:  proto.Float64(ai.lat),
		Lon:  proto.Float64(ai.lon),
		Apps: ai.apps,
	}
	key := fmt.Sprintf("%v:%v", ai.devType, ai.devId)

	packed, err := proto.Marshal(ua)
	if err != nil {
		log.Fatalf("Error: proto.Marshal")
	}

	if dryRun {
		log.Printf("%v - %v -> %v", memc.addr, key, ua.String())
	} else {
		ok := memcacheSet(memc.client, key, packed, attempts)
		if !ok {
			log.Fatalf("Cannot write to memc %v: %v", memc.addr, err)
			return false
		}
	}

	return true
}


func parseAppsinstalled(line string) (AppsInstalled, error) {
	var ai AppsInstalled
	lineParts := strings.Split(strings.TrimSpace(line), "\t")

	if len(lineParts) < 5 {
		return ai, errors.New("Invalid number of columns")
	}

	devType := lineParts[0]
	devId := lineParts[1]
	if devType == "" || devId == "" {
		return ai, errors.New("Invalid devType or devId")
	}

	var apps []uint32
	var appError bool
	for _, appStr := range strings.Split(lineParts[4], ",") {
		app, err := strconv.Atoi(appStr)
		if err != nil {
			appError = true
		} else {
			apps = append(apps, uint32(app))
		}
	}
	if appError {
		log.Fatalf("Not all user apps are digits: `%v`", line)
	}

	lat, latErr := strconv.ParseFloat(lineParts[2], 64)
	lon, lonErr := strconv.ParseFloat(lineParts[3], 64)
	if latErr != nil || lonErr != nil {
		log.Fatalf("Invalid geo coords: `%v`", line)
	}

	ai = AppsInstalled{
		devType: devType,
		devId:   devId,
		apps:    apps,
		lat:     lat,
		lon:     lon,
	}
	return ai, nil
}


func fileHandler(fn string, options *Options, clients map[string]MemcacheClient) bool {
	processed, errors := 0, 0
	log.Printf("Processing %v", fn)

	// Create channels
	resultCh := make(chan Result)
	memcCh := make(map[string]chan *AppsInstalled)
	for devType, memc := range clients {
		memcCh[devType] = make(chan *AppsInstalled, options.buffer)
		go memcacheWriter(memcCh[devType], resultCh, &memc, options.dry, options.attempts)
	}

	// Read archive
	file, err := os.Open(fn)
	if err != nil {
		log.Fatalf("Error while reading file: %v", err)
		return false
	}
	defer file.Close()
	gz, err := gzip.NewReader(file)
	if err != nil {
		log.Printf("Error while reading archive %v", err)
		return false
	}
	defer gz.Close()

	// Parse lines
	scanner := bufio.NewScanner(gz)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}

		ai, err := parseAppsinstalled(line)
		if err != nil {
			errors += 1
			continue
		}

		devType := ai.devType
		_, found := clients[devType]
		if !found {
			errors += 1
			log.Fatalf("Unknown device type: %v", devType)
			continue
		}

		memcCh[devType] <- &ai
	}

	// Close channels
	for devType := range clients {
		close(memcCh[devType])
	}
	for _ = range clients {
		result := <-resultCh
		processed += result.processed
		errors += result.errors
	}
	close(resultCh)

	// Calculate error rate
	errRate := 1.0
	if processed == 0 {
		if errors == 0 {
			errRate = 0
		}
	} else {
		errRate = float64(errors) / float64(processed)
	}

	if errRate < NORMAL_ERR_RATE {
		log.Printf("Acceptable error rate (%v). Successfull load", errRate)
		return true
	} else {
		log.Fatalf("High error rate (%v > %v). Failed load", errRate, NORMAL_ERR_RATE)
		return false
	}
}


func dotRename(path string) {
	head, fn := filepath.Split(path)

	err := os.Rename(path, filepath.Join(head, "." + fn))
	if err != nil {
		log.Fatalf("Error while renaming file: %v", path)
	}
}


func processFiles(options *Options, clients map[string]MemcacheClient) {
	files, err := filepath.Glob(options.pattern)
	if err != nil {
		log.Fatalf("No files for pattern `%v`", options.pattern)
		return
	}

	sort.Strings(files)
	var wg sync.WaitGroup
	for _, fname := range files {
		wg.Add(1)
		go func(fn string) {
			ok := fileHandler(fn, options, clients)
			if ok {
				dotRename(fn)
			}
			wg.Done()
		}(fname)
	}
	wg.Wait()	
}


func main() {
	// Parse arguments
	logFile := flag.String("log", "", "")
	dry := flag.Bool("dry", false, "")
	pattern := flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "")
	idfa := flag.String("idfa", "127.0.0.1:33013", "")
	gaid := flag.String("gaid", "127.0.0.1:33014", "")
	adid := flag.String("adid", "127.0.0.1:33015", "")
	dvid := flag.String("dvid", "127.0.0.1:33016", "")
	attempts := flag.Int("attempts", 3, "")
	buffer := flag.Int("buffer", 100, "")
	flag.Parse()

	options := &Options{
		logFile:  *logFile,
		dry:      *dry,
		pattern:  *pattern,
		idfa:     *idfa,
		gaid:     *gaid,
		adid:     *adid,
		dvid:     *dvid,
		attempts: *attempts,
		buffer:   *buffer,
	}

	if options.logFile != "" {
		f, err := os.OpenFile(options.logFile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
		if err != nil {
			log.Fatalf("Error while openning log file: %s", options.logFile)
			return
		}
		defer f.Close()
		log.SetOutput(f)
	}

	log.Printf("Memc loader started")
	clients := createMemcacheClients(options)
	processFiles(options, clients)
}

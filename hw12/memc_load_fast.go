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
    "reflect"
    "runtime"
    "sort"
    "strconv"
    "strings"
    "time"

    "github.com/bradfitz/gomemcache/memcache"
    "github.com/golang/protobuf/proto"

    "./appsinstalled"
)


const NORMAL_ERR_RATE = 0.01


type AppsInstalled struct {
    devType string
	devId string
	lat float64
	lon float64
	apps []uint32
}
type Options struct {
    dry bool
    pattern string
    idfa string
    gaid string
    adid string
    dvid string
    workers int
    attempts int
    buffer int
}
type MemcacheClient struct {
	addr string
	client *memcache.Client
}
type Result struct {
    processed int
    errors int
}


func memcacheWriter(jobQueue <-chan *AppsInstalled, resultQueue chan<- Result, memc MemcacheClient,
                    dryRun bool, attempts int) {
    processed, errors := 0, 0
	for ai := range jobQueue {
        if ai == nil {  // SENTINEL flag
            resultQueue <- Result{processed, errors}
            processed, errors = 0, 0
        } else {
            ok := insertAppsInstalled(&memc, ai, dryRun, attempts)
            if ok {
                processed += 1
            } else {
                errors += 1
            }
        }
    }
	
}


func memcacheSet(memc *memcache.Client, key string, value []byte, attempts int) bool {
    for i := 0; i < attempts; i++ {
        err := memc.Set(&memcache.Item{
            Key: key,
            Value: value,
        })
        if err == nil {
            return true
        }
        time.Sleep(1 * time.Second)
    }
    return true
}


func dotRename(path string) {
    head, fn := filepath.Split(path)

    err := os.Rename(path, filepath.Join(head, "." + fn))
    if err != nil {
        log.Fatalf("Error while renaming file: %v", path)
    }
}


func insertAppsInstalled(memc *MemcacheClient, ai *AppsInstalled, dryRun bool, attempts int) bool {
    ua := &appsinstalled.UserApps{
        Lat: proto.Float64(ai.lat),
        Lon: proto.Float64(ai.lon),
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
		devId: devId,
		apps: apps,
		lat: lat,
		lon: lon,
	}
    return ai, nil
}


func fileHandler(fileJobQueue <-chan string, fileResultQueue chan<- string, options *Options) {
    deviceMemc := map[string]string{
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }

    resultQueue := make(chan Result)
    defer close(resultQueue)

	jobPool := make(map[string]chan *AppsInstalled)
	for devType, memcAddr := range deviceMemc {
		jobPool[devType] = make(chan *AppsInstalled, options.buffer)
        memc := MemcacheClient{memcAddr, memcache.New(memcAddr)}
        go memcacheWriter(jobPool[devType], resultQueue, memc, options.dry, options.attempts)
        defer close(jobPool[devType])
	}

    for fn := range fileJobQueue {
        processed, errors := 0, 0
        log.Printf("Processing %v", fn)

        file, err := os.Open(fn)
        if err != nil {
            log.Fatalf("Error while reading file: %v", err)
            fileResultQueue <- fn
            continue
        }
        defer file.Close()
        gz, err := gzip.NewReader(file)
        if err != nil {
            log.Printf("Error while reading archive %v", err)
            fileResultQueue <- fn
            continue
        }
        defer gz.Close()
        
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
            _, found := deviceMemc[devType]
            if !found {
                errors += 1
                log.Fatalf("Unknown device type: %v", devType)
                continue
            }

            jobPool[devType] <- &ai
        }

        // Send SENTINEL flag
        for devType := range deviceMemc {
            jobPool[devType] <- nil
        }
        for _ = range deviceMemc {
            result := <-resultQueue
            processed += result.processed
            errors += result.errors
        }

        if processed == 0 {
            fileResultQueue <- fn
            continue
        }

        errRate := float64(errors) / float64(processed)
        if errRate < NORMAL_ERR_RATE {
            log.Printf("Acceptable error rate (%v). Successfull load", errRate)
        } else {
            log.Fatalf("High error rate (%v > %v). Failed load", errRate, NORMAL_ERR_RATE)
        }

        fileResultQueue <- fn
    }
}

func processFiles(options *Options) {
    files, err := filepath.Glob(options.pattern)
	if err != nil {
		log.Fatalf("No files for pattern `%v`", options.pattern)
		return
    }

    fileResultQueue := make(chan string, options.buffer)
    defer close(fileResultQueue)
    fileJobQueue := make(chan string, options.buffer)
    defer close(fileJobQueue)
	for i := 0; i < options.workers; i++ {
		go fileHandler(fileJobQueue, fileResultQueue, options)
    }
    
    sort.Strings(files)
    for _, fn := range files {
        fileJobQueue <- fn
    }
    for _ = range files {
        fn := <- fileResultQueue
        dotRename(fn)
    }
}


func prototest() {
    sample := "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\n" +
              "gaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for _, line := range strings.Split(sample, "\n") {
        ai, _ := parseAppsinstalled(line)

		ua := &appsinstalled.UserApps{
			Lat: proto.Float64(ai.lat),
			Lon: proto.Float64(ai.lon),
			Apps: ai.apps,
        }
        packed, err := proto.Marshal(ua)
        if err != nil {
            log.Fatalf("Error: proto.Marshal")
        }

        unpacked := &appsinstalled.UserApps{}
        err = proto.Unmarshal(packed, unpacked)
        if err != nil {
            log.Fatalf("Error: proto.Unmarshal")
        }

        equalLat := ua.GetLat() == unpacked.GetLat()
		equalLon := ua.GetLon() == unpacked.GetLon()
		equalApps := reflect.DeepEqual(ua.GetApps(), unpacked.GetApps())
		if !equalLat || !equalLon || !equalApps {
			log.Fatalf("Assertion error: ua and unpacked")
			os.Exit(1)
		}
    }
}


func main() {
    // Parse arguments
	test := flag.Bool("test", false, "")
    logFile := flag.String("log", "", "")
    dry := flag.Bool("dry", false, "")
    pattern := flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "")
    idfa := flag.String("idfa", "127.0.0.1:33013", "")
    gaid := flag.String("gaid", "127.0.0.1:33014", "")
    adid := flag.String("adid", "127.0.0.1:33015", "")
    dvid := flag.String("dvid", "127.0.0.1:33016", "")
    workers := flag.Int("workers", runtime.NumCPU() + 1, "")
    attempts := flag.Int("attempts", 3, "")
    buffer := flag.Int("buffer", 100, "")
    flag.Parse()

    options := &Options{
        dry: *dry,
        pattern: *pattern,
        idfa: *idfa,
        gaid: *gaid,
        adid: *adid,
        dvid: *dvid,
        workers: *workers,
        attempts: *attempts,
        buffer: *buffer,
    }

    if *logFile != "" {
        f, err := os.OpenFile(*logFile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
        if err != nil {
            log.Fatalf("Error while openning log file: %s", logFile)
            return
        }
        defer f.Close()
        log.SetOutput(f)
    }

    if *test {
        prototest()
        return
    }

    log.Printf("Memc loader started")
	processFiles(options)
}

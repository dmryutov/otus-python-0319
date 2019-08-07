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
	"strconv"
	"strings"

	"github.com/bradfitz/gomemcache/memcache"
	"github.com/golang/protobuf/proto"

	"./appsinstalled"
)

const NORMAL_ERR_RATE = 0.01

type AppsInstalled struct {
	devType string
	devId   string
	lat     float64
	lon     float64
	apps    []uint32
}
type Options struct {
	dry     bool
	pattern string
	idfa    string
	gaid    string
	adid    string
	dvid    string
}
type MemcacheClient struct {
	addr   string
	client *memcache.Client
}

func dotRename(path string) {
	head, fn := filepath.Split(path)

	err := os.Rename(path, filepath.Join(head, "."+fn))
	if err != nil {
		log.Fatalf("Error while renaming file: %v", path)
	}
}

func insertAppsinstalled(memc *MemcacheClient, ai *AppsInstalled, dryRun bool) bool {
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
		err := memc.client.Set(&memcache.Item{
			Key:   key,
			Value: packed,
		})
		if err != nil {
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

func processFiles(options *Options) {
	deviceMemc := map[string]MemcacheClient{
		"idfa": MemcacheClient{options.idfa, memcache.New(options.idfa)},
		"gaid": MemcacheClient{options.gaid, memcache.New(options.gaid)},
		"adid": MemcacheClient{options.adid, memcache.New(options.adid)},
		"dvid": MemcacheClient{options.dvid, memcache.New(options.dvid)},
	}

	files, err := filepath.Glob(options.pattern)
	if err != nil {
		log.Fatalf("No files for pattern `%v`", options.pattern)
		return
	}
	for _, fn := range files {
		processed, errors := 0, 0
		log.Printf("Processing %v", fn)

		file, err := os.Open(fn)
		if err != nil {
			log.Fatalf("Error while reading file: %v", err)
			return
		}
		defer file.Close()
		gz, err := gzip.NewReader(file)
		if err != nil {
			log.Printf("Error while reading archive %v", err)
			return
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

			memc, found := deviceMemc[ai.devType]
			if !found {
				errors += 1
				log.Fatalf("Unknown device type: %v", ai.devType)
				continue
			}

			ok := insertAppsinstalled(&memc, &ai, options.dry)
			if ok {
				processed += 1
			} else {
				errors += 1
			}
		}
		if processed == 0 {
			dotRename(fn)
			continue
		}

		errRate := float64(errors) / float64(processed)
		if errRate < NORMAL_ERR_RATE {
			log.Printf("Acceptable error rate (%v). Successfull load", errRate)
		} else {
			log.Fatalf("High error rate (%v > %v). Failed load", errRate, NORMAL_ERR_RATE)
		}
		dotRename(fn)
	}
}

func main() {
	// Parse arguments
	logFile := *flag.String("log", "", "")
	dry := *flag.Bool("dry", false, "")
	pattern := *flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "")
	idfa := *flag.String("idfa", "127.0.0.1:33013", "")
	gaid := *flag.String("gaid", "127.0.0.1:33014", "")
	adid := *flag.String("adid", "127.0.0.1:33015", "")
	dvid := *flag.String("dvid", "127.0.0.1:33016", "")
	flag.Parse()

	options := &Options{
		dry:     dry,
		pattern: pattern,
		idfa:    idfa,
		gaid:    gaid,
		adid:    adid,
		dvid:    dvid,
	}

	if logFile != "" {
		f, err := os.OpenFile(logFile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
		if err != nil {
			log.Fatalf("Error while openning log file: %s", logFile)
			return
		}
		defer f.Close()
		log.SetOutput(f)
	}

	log.Printf("Memc loader started")
	processFiles(options)
}

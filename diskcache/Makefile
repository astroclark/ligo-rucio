#!/bin/make


observations:
	nohup ./SimFrWrite> logs/SimFrWrite_stdout_stderr.log 2>&1 & echo $$! > SimFrWrite_pid

diskcache:
	./start_diskcache

clean:
	kill -9 $$(cat SimFrWrite_pid)
	kill -9 $$(cat diskcache_pid)
	rm -f logs/*
	rm -rf frames/*
	rm -f frame_cache_dump*
	rm -f diskcache_pid
	rm -f SimFrWrite_pid


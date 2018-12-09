#!/bin/make

all: observations diskcache

observations:
	nohup ./SimFrWrite> logs/SimFrWrite_stdout_stderr.log 2>&1 & echo $$! > SimFrWrite_pid

diskcache:
	./start_diskcache

stop:
ifneq ("$(wildcard SimFrWrite_pid)","") 
	kill -9 $$(cat SimFrWrite_pid)
	rm -f SimFrWrite_pid
endif 
ifneq ("$(wildcard diskcache_pid)","") 
	kill -9 $$(cat diskcache_pid)
	rm -f diskcache_pid
endif 

clean: stop
	rm -f logs/*
	rm -rf frames/*
	rm -f frame_cache_dump*

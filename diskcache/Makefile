#!/bin/make

all: observations diskcache

observations:
	$(info Generating observations)
	nohup ./SimFrWrite> logs/SimFrWrite_stdout_stderr.log 2>&1 & echo $$! > SimFrWrite_pid

diskcache:
	$(info Starting diskcache daemon)
	./start_diskcache

stop:
	$(info Stopping processes:)
ifneq ("$(wildcard SimFrWrite_pid)","") 
	kill -9 $$(cat SimFrWrite_pid)
	rm -f SimFrWrite_pid
	$(info SimFrWrite stopped)
else
	$(info SimFrWrite not running)
endif 
ifneq ("$(wildcard diskcache_pid)","") 
	kill -9 $$(cat diskcache_pid)
	rm -f diskcache_pid
	$(info diskcache stopped)
else
	$(info diskcache not running)
endif 

clean: stop
	rm -f logs/*
	rm -rf frames/*
	rm -f frame_cache_dump*

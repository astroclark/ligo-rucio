SERVER_PORT=11300
CONCURRENCY=4
OUTPUT_ASCII=/home/jclark/Projects/ligo-rucio/diskcache/frame_cache_dump
OUTPUT_ASCII_VERSION=0x00FF
OUTPUT_BINARY=/home/jclark/Projects/ligo-rucio/diskcache/.frame.cache
LOG=diskcache
LOG_DIRECTORY=/home/jclark/Projects/ligo-rucio/diskcache/logs
LOG_DEBUG_LEVEL=0
LOG_ROTATE_ENTRY_COUNT=10000
SCAN_INTERVAL=16000
STAT_TIMEOUT=600
#------------------------------------------------------------------------
# DIRECTORY_TIMEOUT
#   Number of seconds to wait for directory calls to complete
#   Default: 20 seconds
#------------------------------------------------------------------------
DIRECTORY_TIMEOUT=60

[EXTENSIONS]
.gwf
.sft

[EXCLUDED_DIRECTORIES]

[MOUNT_POINTS]
#/hdfs/frames/ER10/hoft_C02/H1
#/hdfs/frames/ER10/hoft_C02/L1
/home/jclark/Projects/ligo-rucio/diskcache/frames

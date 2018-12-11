#!/bin/bash -e
# What is the latency between the file creation and the epoch they report?

framedir="/archive/frames/postO2/raw/H1/H-H1_R-12285"

# Loop over the most recent files
for frame in `ls ${framedir}/*gwf | tail`; do

    frame_epoch_h=$(lalapps_tconvert --local $(echo ${frame} | awk -F- '{print $5}'))
    created_h=$(stat -c %y ${frame})

    frame_epoch=$(lalapps_tconvert --unix-epoch $(echo ${frame} | awk -F- '{print $5}'))
    created=$(stat -c %Y ${frame})

    echo "------------ ${frame} -------------"
    echo "Frame epoch: ${frame_epoch_h}"
    echo "File created: ${created_h}"
#    echo -e "${frame_epoch_h}\t|\t${created_h}"
#    #echo -e "${frame_epoch}\t|\t${created}"
    #echo "Seconds different: $((created-frame_epoch))"

    echo ""
done

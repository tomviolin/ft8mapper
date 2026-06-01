#!/bin/bash

decode_dir="decoding$$"
mkdir -p "$decode_dir"
while true; do
	if [ -d "segments" ]; then
		break
	else
		echo "Waiting for segments directory to be created..."
		sleep 5
	fi
done

while [ ! -f stop.flag ]; do
for segfile in segments/segment_*.wav; do
	if [ ! -f "$segfile" ]; then
		echo "File not found: "$segfile" -- skipping."
		continue
	fi
	segbase=$(basename "$segfile")
	# parse segment_0123456789.wav style filename to get timestamp
	if [ "${#segbase}" -eq 22 ]; then
		echo "Processing $segfile..."
		filetimestamp=${segbase:8:10}
		filedatestamp=$(date -u -d "@$filetimestamp" +"%Y%m%d_%H%M%S")
		mv "$segfile" "segments/segment_$filedatestamp.wav"
		wavfile="segments/segment_$filedatestamp.wav"
	elif [ "${#segbase}" -eq 27 ]; then
		echo "Processing $segfile..."
		filedatestamp=${segbase:8:15}
		wavfile=$segfile
	else
		echo "Skipping $segfile - filename does not match expected format."
		continue
	fi
	echo $filedatestamp
	# decode the file using wsjtx
	cd "$decode_dir"
	mkdir -p "../decoded"
	echo jt9 -8 -L 100 -H 5000 -d 3 "../$wavfile" \> "../decoded/console_$filedatestamp.txt"
	jt9 -8 -L 100 -H 5000 -d 3 "../$wavfile" > "../decoded/console_$filedatestamp.txt"
	echo mv decoded.txt "../decoded/decoded_$filedatestamp.txt"
	mv decoded.txt "../decoded/decoded_$filedatestamp.txt"
	echo mv "../$wavfile" ../trash
	mv "../$wavfile" ../trash
	cd ..
done
sleep 1
done 

rm -rf "$decode_dir"


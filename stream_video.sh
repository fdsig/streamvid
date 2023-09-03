#!/bin/bash
set -e

# Ensure 'expect', 'inotifywait', and 'lsof' are installed
for cmd in expect inotifywait lsof; do
    if ! command -v $cmd &> /dev/null; then
        echo "Please install '$cmd' to proceed."
        exit 1
    fi
done

FIFO_DIR="./mypipe_dir"
mkdir -p "$FIFO_DIR"
FIFO_PATH="$FIFO_DIR/mypipe"
[[ ! -p "$FIFO_PATH" ]] && mkfifo "$FIFO_PATH"

CAPTURE_DIR="./capture_output"
mkdir -p "$CAPTURE_DIR"

cleanup() {
    echo "Cleaning up..."
    rm -f "$FIFO_PATH"
    rmdir "$FIFO_DIR"
    rm -rf "$CAPTURE_DIR"
    pkill -f ffmpeg || true
    pkill -f tail || true
    pkill -f nvgstcapture-1.0 || true
}
trap cleanup EXIT

inotifywait -m -e create --format '%w%f' "$CAPTURE_DIR" | while read NEWFILE
do
    # Wait for a process to start writing to the file.
    while ! lsof "$NEWFILE" &>/dev/null; do
        sleep 0.5
    done
    tail -f "$NEWFILE" > "$FIFO_PATH" &
    break
done &

/usr/bin/expect <<EOD &
spawn nvgstcapture-1.0 --mode=2 --video-enc=1 --file-type=0 --capture-time=0 --file-name="$CAPTURE_DIR/capture"
# Let's add a sleep for a few seconds to ensure nvgstcapture is ready for commands.
sleep 5
send "1\r"
EOD

echo "nvgstcapture initialized."

ffmpeg -i "$FIFO_PATH" -an -c:v copy -f hls -hls_time 4 -hls_playlist_type event -hls_list_size 5 -hls_flags delete_segments /tmp/playlist.m3u8 &

echo "ffmpeg initialized."

if [ -f /tmp/playlist.m3u8 ]; then
    echo "/tmp/playlist.m3u8 was created successfully."
else
    echo "Failed to create /tmp/playlist.m3u8."
    exit 1
fi

cd /tmp


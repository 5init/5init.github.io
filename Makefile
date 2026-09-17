.PHONY: all fetch build clean

all: fetch build

# Fetch latest videos from YouTube RSS and update markdown source
fetch:
	python3 scripts/fetch_videos.py

# Convert markdown to HTML
build:
	bash scripts/build.sh

# Build without fetching (useful for local preview)
local:
	bash scripts/build.sh

clean:
	rm -f index.html

# youtuber-site

A minimal, fast personal site.

## Setup


### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/youtuber-site
cd youtuber-site
```

Edit `scripts/build.sh` to set:

- `CHANNEL_TITLE` — the creator's display name
- `SOCIALS` — links to their social profiles
- `AVATAR_IMG` — path to avatar image (or leave for placeholder)

Edit `scripts/fetch_videos.py` to set:

- `CHANNEL_ID` — the YouTube channel ID (find it at [commentpicker.com/youtube-channel-id.php](https://commentpicker.com/youtube-channel-id.php))
- `MAX_VIDEOS` — how many recent videos to show (default: 3)
- Livestreams and Shorts never appear: the channel's Videos tab is used to identify regular uploads (a per-video check is the fallback if that page is unavailable).

### 2. Add avatar (optional)

Drop a `avatar.jpg` in the repo root. Crop it to square beforehand.

### 3. Build

```bash
make local      # build without fetching (uses current markdown)
make            # fetch latest videos, then build
```

Open `index.html` in your browser.

### 4. Deploy to GitHub Pages

1. Push the repo to GitHub
2. Go to **Settings → Pages**
3. Set source to **Deploy from branch → main → / (root)**
4. GitHub Pages will serve `index.html` at `https://YOUR_USERNAME.github.io/youtuber-site/`

The GitHub Action (`.github/workflows/update.yml`) will run automatically every 6 hours. You can also trigger it manually from the **Actions** tab.


## Customising content

Edit `markdown/index.md` freely — the About section and social links in the sidebar are controlled via `build.sh`. The `<!-- VIDEOS_START -->` / `<!-- VIDEOS_END -->` block is managed automatically. don't remove those comments.

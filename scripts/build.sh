#!/usr/bin/env bash
set -euo pipefail

OUT="index.html"
HEADER_MD="markdown/header.md"
CONTENT_MD="markdown/index.md"
TITLE="5init"

echo "Building $OUT..."

HEADER_HTML=$(perl Markdown.pl "$HEADER_MD")
MAIN_HTML=$(perl Markdown.pl "$CONTENT_MD")

TMP=$(mktemp -d)

cat > "$TMP/head.html" << HTML
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${TITLE}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

<div id="wrap">

<header>
${HEADER_HTML}
</header>

<section>
HTML

printf '%s\n' "$MAIN_HTML" > "$TMP/body.html"

cat > "$TMP/foot.html" << HTML
</section>

</div>

</body>
</html>
HTML

cat "$TMP/head.html" "$TMP/body.html" "$TMP/foot.html" > "$OUT"
rm -rf "$TMP"

echo "Done → $OUT"

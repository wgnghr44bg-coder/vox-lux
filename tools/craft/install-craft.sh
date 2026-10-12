#!/bin/bash
# Installs the free ArtCraft "Crafting Apps" (Linux builds) + Python video libs.
# Idempotent: apps that are already installed are skipped.
# Apps: FilmCraft (Premiere), EffectCraft (After Effects), PhotoCraft (Photoshop),
#       VectorCraft (Illustrator), LightCraft (Lightroom), DesignCraft (InDesign), PdfCraft (Acrobat),
#       SoundCraft (Pro Tools), WordCraft (Word), GridCraft (Excel), DeckCraft (PowerPoint).
set -uo pipefail
DEST="${CRAFT_DIR:-/opt/craft}"
mkdir -p "$DEST" && cd "$DEST" || exit 1
# repo:binary (some repos were renamed: sheetcraft ships GridCraft, slidecraft ships DeckCraft)
for pair in filmcraft:filmcraft effectcraft:effectcraft photocraft:photocraft vectorcraft:vectorcraft \
            lightcraft:lightcraft designcraft:designcraft pdfcraft:pdfcraft soundcraft:soundcraft \
            wordcraft:wordcraft sheetcraft:gridcraft slidecraft:deckcraft; do
  repo=${pair%%:*}; app=${pair#*:}
  if command -v "$app-cli" >/dev/null 2>&1; then continue; fi
  tag=$(git ls-remote --tags --sort=-v:refname "https://github.com/storytold/$repo" 2>/dev/null \
        | grep -v '\^{}' | head -1 | sed 's#.*refs/tags/##')
  [ -z "$tag" ] && { echo "craft: $app - no release found" >&2; continue; }
  f="$app-${tag#v}-linux-x86_64.tar.gz"
  base="https://github.com/storytold/$repo/releases/download/$tag"
  if curl -fsSL -o "$f" "$base/$f" && curl -fsSL -o sums.txt "$base/SHA256SUMS.txt" \
     && grep " \*\?$f\$" sums.txt | sha256sum -c - >/dev/null 2>&1; then
    tar xzf "$f" && ln -sf "$DEST"/"$app"-*/bin/* /usr/local/bin/ && echo "craft: $app $tag installed"
  else
    echo "craft: $app $tag - download or checksum failed" >&2
  fi
  rm -f "$f" sums.txt
done
python3 -c "import cv2, numpy, PIL" 2>/dev/null || pip install -q opencv-python-headless numpy pillow 2>/dev/null
exit 0

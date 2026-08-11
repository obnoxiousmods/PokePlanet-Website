#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <release-archive.tar.gz>" >&2
  exit 2
fi

archive=$(realpath "$1")
release_id=$(date -u +%Y%m%d%H%M%S)
root=/srv/pokeplanet-website
release="$root/releases/$release_id"
previous=""
if [[ -L "$root/current" ]]; then
  previous=$(readlink -f "$root/current" 2>/dev/null || true)
fi

install -d -o pokeplanet-web -g pokeplanet-web "$release"
tar -xzf "$archive" -C "$release"
chown -R pokeplanet-web:pokeplanet-web "$release"
sudo -u pokeplanet-web uv sync --project "$release/backend" --frozen --no-dev
ln -sfn "$release" "$root/current.next"
mv -Tf "$root/current.next" "$root/current"
systemctl restart pokeplanet-website

if ! curl -fsS --retry 10 --retry-delay 1 --retry-connrefused \
  http://127.0.0.1:8791/api/health >/dev/null; then
  if [[ -n "$previous" && -d "$previous" ]]; then
    ln -sfn "$previous" "$root/current.next"
    mv -Tf "$root/current.next" "$root/current"
    systemctl restart pokeplanet-website
  fi
  echo "deployment failed health check; previous release restored" >&2
  exit 1
fi

find "$root/releases" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -nr | tail -n +6 | cut -d' ' -f2- | xargs -r rm -rf --

#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-only
# NIN-VAVE: build nin.chapter23.uk from the newest firmware and every built pack, check it, publish it.
#   tools/deploy_nin_site.sh VERSION [FIRMWARE.fwsc] [--dry-run]
# FIRMWARE: default build/nin-vave.fwsc (./build.sh). The packs: build/nin/packs/* (tools/nin_pack.py build).
# Needs: python3, node, and `npx wrangler login` once (Cloudflare account holding chapter23.uk).
set -e
cd "$(dirname "$0")/.."
VERSION="$1"; FW="${2:-build/nin-vave.fwsc}"; DRY=""
for a in "$@"; do [ "$a" = "--dry-run" ] && DRY="--dry-run"; done
[ -n "$VERSION" ] || { echo "usage: tools/deploy_nin_site.sh VERSION [FIRMWARE.fwsc] [--dry-run]"; exit 1; }
[ "$FW" = "--dry-run" ] && FW=build/nin-vave.fwsc
PY="${PYTHON:-python3}"
rm -rf build/site
"$PY" tools/make_nin_site.py "$FW" "$VERSION" build/site
node web/test_nin_packs.mjs build/site
npx -y wrangler@4.153.0 deploy --config site/wrangler.jsonc $DRY

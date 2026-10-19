#!/bin/bash
# Cloud sessions only: install the free Craft video apps so every session can use them.
set -uo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
"$CLAUDE_PROJECT_DIR/tools/craft/install-craft.sh"
exit 0

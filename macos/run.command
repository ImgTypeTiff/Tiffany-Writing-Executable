#!/bin/bash

chmod +x "$0"

APP="tiffany writing executable.app"
cd "$(dirname "$0")"

if [ ! -d "$APP" ]; then
  echo "Error: $APP not found in this folder."
  exit 1
fi

echo "Removing quarantine..."
xattr -dr com.apple.quarantine "$APP"

echo "Launching app..."
open "$APP"

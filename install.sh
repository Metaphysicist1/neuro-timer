#!/bin/bash

# Neuro Timer - Desktop Installation
# Installs the app to your Ubuntu applications menu

set -e

echo "🧠 Installing Neuro Timer..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create assets directory if needed
mkdir -p "$SCRIPT_DIR/assets"

# Update desktop file with correct paths
sed -i "s|Exec=.*|Exec=python3 $SCRIPT_DIR/neuro_timer.py|g" "$SCRIPT_DIR/neuro-timer.desktop"
sed -i "s|Icon=.*|Icon=$SCRIPT_DIR/assets/icon.png|g" "$SCRIPT_DIR/neuro-timer.desktop"

# Copy to applications folder
mkdir -p ~/.local/share/applications
cp "$SCRIPT_DIR/neuro-timer.desktop" ~/.local/share/applications/

# Make executable
chmod +x ~/.local/share/applications/neuro-timer.desktop
chmod +x "$SCRIPT_DIR/neuro_timer.py"

# Update desktop database
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "✅ Installation complete!"
echo ""
echo "📌 To pin to your dock:"
echo "   1. Press Super key (Windows key)"
echo "   2. Search 'Neuro Timer'"
echo "   3. Right-click → 'Add to Favorites'"
echo ""
echo "🎵 To add NSDR music:"
echo "   Copy your audio file to: $SCRIPT_DIR/assets/nsdr_music.mp3"
echo ""
echo "🎨 To add custom icon:"
echo "   Add a 256x256 PNG to: $SCRIPT_DIR/assets/icon.png"
echo ""
echo "🚀 Run now: python3 $SCRIPT_DIR/neuro_timer.py"
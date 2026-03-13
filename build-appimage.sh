#!/bin/bash

# Build AppImage for Neuro Timer
# This creates a portable .AppImage file

set -e

APP_NAME="Neuro-Timer"
APP_VERSION="1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Building AppImage for $APP_NAME..."

# Create AppDir structure
APP_DIR="$SCRIPT_DIR/AppDir"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy main script
cp "$SCRIPT_DIR/neuro_timer.py" "$APP_DIR/usr/bin/"
chmod +x "$APP_DIR/usr/bin/neuro_timer.py"

# Copy assets
mkdir -p "$APP_DIR/usr/share/neuro-timer/assets"
cp -r "$SCRIPT_DIR/assets/"* "$APP_DIR/usr/share/neuro-timer/assets/" 2>/dev/null || true

# Copy icon
if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
    cp "$SCRIPT_DIR/assets/icon.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/neuro-timer.png"
    cp "$SCRIPT_DIR/assets/icon.png" "$APP_DIR/neuro-timer.png"
fi

# Create desktop file
cat > "$APP_DIR/neuro-timer.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Neuro Timer
GenericName=Productivity Timer
Comment=Productivity timer with focus protocols
Exec=neuro-timer
Icon=neuro-timer
Terminal=false
Categories=Utility;Office;GTK;
Keywords=timer;pomodoro;productivity;focus;
StartupNotify=true
EOF

cp "$APP_DIR/neuro-timer.desktop" "$APP_DIR/usr/share/applications/"

# Create AppRun launcher
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/bin:${PYTHONPATH}"

# Set assets path for the app
export NEURO_TIMER_ASSETS="${HERE}/usr/share/neuro-timer/assets"

exec python3 "${HERE}/usr/bin/neuro_timer.py" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

echo "✅ AppDir created at: $APP_DIR"
echo ""
echo "📦 To create the final AppImage, you need appimagetool:"
echo ""
echo "   # Download appimagetool (one time)"
echo "   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
echo "   chmod +x appimagetool-x86_64.AppImage"
echo ""
echo "   # Build the AppImage"
echo "   ./appimagetool-x86_64.AppImage AppDir Neuro-Timer-x86_64.AppImage"
echo ""
echo "   # Run it"
echo "   ./Neuro-Timer-x86_64.AppImage"
echo ""
echo "🎉 Or just run the app directly:"
echo "   $APP_DIR/AppRun"
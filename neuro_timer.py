#!/usr/bin/env python3
"""
Neuro Timer - GTK3 Desktop Application
Productivity timer with focus protocols
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf
import threading
import time
import subprocess
import os
import signal

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class NeuroTimer(Gtk.Window):
    """GTK3 Timer Application"""
    
    def __init__(self):
        super().__init__(title="Neuro Timer")
        
        # Timer state
        self.timer_running = False
        self.timer_paused = False
        self.remaining_seconds = 5400  # 90 minutes default
        self.total_seconds = 5400
        self.current_protocol = "deep_work"
        self.session_count = 0
        self.total_focus_minutes = 0
        
        # Audio processes
        self.nsdr_process = None
        self.brown_noise_process = None
        self.brown_noise_enabled = False
        
        # Setup window
        self.set_default_size(520, 500)
        self.set_border_width(25)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Set window icon
        self.set_icon()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Build UI
        self.build_ui()
        
        # Connect events
        self.connect("destroy", self.on_destroy)
    
    def set_icon(self):
        """Set window icon"""
        icon_path = os.path.join(SCRIPT_DIR, "assets", "icon.png")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)
        else:
            self.set_icon_name("preferences-system-time")
    
    def apply_dark_theme(self):
        """Apply dark theme CSS"""
        css = b"""
        window {
            background-color: #0D1117;
        }
        label {
            color: #E2E8F0;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #E2E8F0;
        }
        .subtitle {
            font-size: 11px;
            color: #64748B;
        }
        .timer {
            font-size: 56px;
            font-weight: bold;
            color: #38BDF8;
            font-family: monospace;
        }
        .timer-amber {
            font-size: 56px;
            font-weight: bold;
            color: #FDBA74;
            font-family: monospace;
        }
        .protocol-name {
            font-size: 14px;
            font-weight: bold;
            color: #94A3B8;
        }
        .status {
            font-size: 12px;
            color: #64748B;
        }
        .protocol-btn {
            background: #161B22;
            color: #E2E8F0;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
        }
        .protocol-btn:hover {
            background: #38BDF8;
            border-color: #38BDF8;
        }
        .start-btn {
            background: #10B981;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
            font-size: 14px;
        }
        .start-btn:hover {
            background: #059669;
        }
        .pause-btn {
            background: #F59E0B;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
            font-size: 14px;
        }
        .pause-btn:hover {
            background: #D97706;
        }
        .reset-btn {
            background: #EF4444;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
            font-size: 14px;
        }
        .reset-btn:hover {
            background: #DC2626;
        }
        .preset-btn {
            background: #21262D;
            color: #E2E8F0;
            border: 1px solid #30363D;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
        }
        .preset-btn:hover {
            background: #38BDF8;
            border-color: #38BDF8;
        }
        .stats-label {
            font-size: 11px;
            color: #64748B;
        }
        .stats-value {
            font-size: 16px;
            font-weight: bold;
            color: #38BDF8;
        }
        .audio-section {
            background: #161B22;
            border-radius: 8px;
            padding: 10px;
        }
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def build_ui(self):
        """Build the user interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(main_box)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        header_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(header_box, False, False, 5)
        
        # Logo
        icon_path = os.path.join(SCRIPT_DIR, "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 48, 48, True)
                logo = Gtk.Image.new_from_pixbuf(pixbuf)
                header_box.pack_start(logo, False, False, 5)
            except:
                pass
        
        title = Gtk.Label(label="🧠 Neuro Timer")
        title.get_style_context().add_class("title")
        header_box.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Focus & Productivity Protocols")
        subtitle.get_style_context().add_class("subtitle")
        header_box.pack_start(subtitle, False, False, 0)
        
        # Protocol buttons
        protocol_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        protocol_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(protocol_box, False, False, 10)
        
        protocols = [
            ("🎯 Deep Work", "deep_work", 90),
            ("🧘 NSDR", "nsdr", 10),
            ("🌊 Focus", "focus", 1),
            ("☀️ Morning", "morning", 10),
            ("🌙 Evening", "evening", 15),
        ]
        
        for label, mode, minutes in protocols:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("protocol-btn")
            btn.connect("clicked", self.on_protocol_clicked, mode, minutes)
            protocol_box.pack_start(btn, False, False, 0)
        
        # Protocol name
        self.protocol_label = Gtk.Label(label="Deep Work Protocol")
        self.protocol_label.get_style_context().add_class("protocol-name")
        main_box.pack_start(self.protocol_label, False, False, 5)
        
        # Timer display
        self.timer_label = Gtk.Label(label="01:30:00")
        self.timer_label.get_style_context().add_class("timer")
        main_box.pack_start(self.timer_label, True, True, 15)
        
        # Status
        self.status_label = Gtk.Label(label="Ready for deep work session")
        self.status_label.get_style_context().add_class("status")
        main_box.pack_start(self.status_label, False, False, 5)
        
        # Preset buttons
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        preset_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(preset_box, False, False, 8)
        
        preset_label = Gtk.Label(label="Quick set:")
        preset_label.get_style_context().add_class("status")
        preset_box.pack_start(preset_label, False, False, 5)
        
        for mins in [5, 10, 25, 45, 90]:
            btn = Gtk.Button(label=f"{mins}m")
            btn.get_style_context().add_class("preset-btn")
            btn.connect("clicked", self.on_preset_clicked, mins)
            preset_box.pack_start(btn, False, False, 0)
        
        # Control buttons
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        control_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(control_box, False, False, 15)
        
        self.start_btn = Gtk.Button(label="▶  Start")
        self.start_btn.get_style_context().add_class("start-btn")
        self.start_btn.connect("clicked", self.on_start_clicked)
        control_box.pack_start(self.start_btn, False, False, 0)
        
        self.pause_btn = Gtk.Button(label="⏸  Pause")
        self.pause_btn.get_style_context().add_class("pause-btn")
        self.pause_btn.set_sensitive(False)
        self.pause_btn.connect("clicked", self.on_pause_clicked)
        control_box.pack_start(self.pause_btn, False, False, 0)
        
        self.reset_btn = Gtk.Button(label="⏹  Reset")
        self.reset_btn.get_style_context().add_class("reset-btn")
        self.reset_btn.connect("clicked", self.on_reset_clicked)
        control_box.pack_start(self.reset_btn, False, False, 0)
        
        # Audio controls section
        audio_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        audio_frame.set_halign(Gtk.Align.CENTER)
        audio_frame.get_style_context().add_class("audio-section")
        main_box.pack_start(audio_frame, False, False, 10)
        
        audio_label = Gtk.Label(label="🎧 Audio:")
        audio_label.get_style_context().add_class("status")
        audio_frame.pack_start(audio_label, False, False, 10)
        
        self.brown_noise_check = Gtk.CheckButton(label="Brown Noise")
        self.brown_noise_check.connect("toggled", self.on_brown_noise_toggled)
        audio_frame.pack_start(self.brown_noise_check, False, False, 5)
        
        # Stats row
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
        stats_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(stats_box, False, False, 10)
        
        # Sessions counter
        session_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        session_box.set_halign(Gtk.Align.CENTER)
        stats_box.pack_start(session_box, False, False, 0)
        
        session_title = Gtk.Label(label="Sessions")
        session_title.get_style_context().add_class("stats-label")
        session_box.pack_start(session_title, False, False, 0)
        
        self.session_label = Gtk.Label(label="0")
        self.session_label.get_style_context().add_class("stats-value")
        session_box.pack_start(self.session_label, False, False, 0)
        
        # Focus time
        focus_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        focus_box.set_halign(Gtk.Align.CENTER)
        stats_box.pack_start(focus_box, False, False, 0)
        
        focus_title = Gtk.Label(label="Focus Time")
        focus_title.get_style_context().add_class("stats-label")
        focus_box.pack_start(focus_title, False, False, 0)
        
        self.focus_label = Gtk.Label(label="0h 0m")
        self.focus_label.get_style_context().add_class("stats-value")
        focus_box.pack_start(self.focus_label, False, False, 0)
    
    def on_protocol_clicked(self, button, mode, minutes):
        """Handle protocol button click"""
        self.current_protocol = mode
        
        names = {
            "deep_work": "Deep Work Protocol",
            "nsdr": "NSDR Session (10 min)",
            "focus": "Focus Reset",
            "morning": "Morning Protocol",
            "evening": "Evening Wind-Down"
        }
        
        self.protocol_label.set_text(names.get(mode, mode))
        self.set_time(minutes)
        
        # Change color for relaxation modes
        ctx = self.timer_label.get_style_context()
        if mode in ["nsdr", "evening"]:
            ctx.remove_class("timer")
            ctx.add_class("timer-amber")
            self.status_label.set_text("🧘 Relaxation mode")
        else:
            ctx.remove_class("timer-amber")
            ctx.add_class("timer")
            self.status_label.set_text(f"Ready for {names.get(mode, mode)}")
    
    def on_preset_clicked(self, button, minutes):
        """Handle preset button click"""
        self.set_time(minutes)
    
    def set_time(self, minutes):
        """Set timer to specified minutes"""
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.update_display()
    
    def update_display(self):
        """Update timer display"""
        hours = self.remaining_seconds // 3600
        mins = (self.remaining_seconds % 3600) // 60
        secs = self.remaining_seconds % 60
        self.timer_label.set_text(f"{hours:02d}:{mins:02d}:{secs:02d}")
    
    def on_start_clicked(self, button):
        """Start the timer"""
        if self.timer_running:
            return
        
        self.timer_running = True
        self.timer_paused = False
        
        self.start_btn.set_sensitive(False)
        self.pause_btn.set_sensitive(True)
        self.status_label.set_text("🚀 Session started!")
        
        # Start NSDR music if in NSDR mode
        if self.current_protocol == "nsdr":
            self.play_nsdr_audio()
        
        # Start timer in background thread
        thread = threading.Thread(target=self.run_timer, daemon=True)
        thread.start()
    
    def on_pause_clicked(self, button):
        """Pause/resume timer"""
        self.timer_paused = not self.timer_paused
        
        if self.timer_paused:
            self.pause_btn.set_label("▶  Resume")
            self.status_label.set_text("⏸ Paused")
            self.pause_audio()
        else:
            self.pause_btn.set_label("⏸  Pause")
            self.status_label.set_text("▶ Resumed")
            self.resume_audio()
    
    def on_reset_clicked(self, button):
        """Reset timer"""
        self.timer_running = False
        self.timer_paused = False
        
        # Stop NSDR audio
        self.stop_nsdr_audio()
        
        self.set_time(90)
        self.start_btn.set_sensitive(True)
        self.pause_btn.set_sensitive(False)
        self.pause_btn.set_label("⏸  Pause")
        
        # Reset to blue theme
        ctx = self.timer_label.get_style_context()
        ctx.remove_class("timer-amber")
        ctx.add_class("timer")
        
        self.current_protocol = "deep_work"
        self.protocol_label.set_text("Deep Work Protocol")
        self.status_label.set_text("Ready for deep work session")
    
    def run_timer(self):
        """Timer countdown loop (runs in thread)"""
        while self.remaining_seconds > 0 and self.timer_running:
            if not self.timer_paused:
                GLib.idle_add(self.update_display)
                self.remaining_seconds -= 1
            
            time.sleep(1)
        
        if self.timer_running:
            GLib.idle_add(self.timer_complete)
    
    def timer_complete(self):
        """Handle timer completion"""
        self.timer_running = False
        self.remaining_seconds = 0
        self.update_display()
        
        # Stop NSDR audio
        self.stop_nsdr_audio()
        
        # Update stats
        self.session_count += 1
        self.session_label.set_text(str(self.session_count))
        
        # Track focus time (only for work protocols)
        if self.current_protocol in ["deep_work", "morning", "focus"]:
            self.total_focus_minutes += self.total_seconds // 60
            hours = self.total_focus_minutes // 60
            mins = self.total_focus_minutes % 60
            self.focus_label.set_text(f"{hours}h {mins}m")
        
        self.start_btn.set_sensitive(True)
        self.pause_btn.set_sensitive(False)
        self.pause_btn.set_label("⏸  Pause")
        self.status_label.set_text("🎉 Session complete! Take a break.")
        
        # Show notification
        self.show_notification()
    
    # === Audio Controls ===
    
    def on_brown_noise_toggled(self, button):
        """Toggle brown noise"""
        if button.get_active():
            self.start_brown_noise()
        else:
            self.stop_brown_noise()
    
    def start_brown_noise(self):
        """Start brown noise playback"""
        audio_path = os.path.join(SCRIPT_DIR, "assets", "brown.mp3")
        
        if not os.path.exists(audio_path):
            self.status_label.set_text("⚠️ brown.mp3 not found in assets/")
            self.brown_noise_check.set_active(False)
            return
        
        self.brown_noise_process = self._play_audio(audio_path, loop=True)
        if self.brown_noise_process:
            self.brown_noise_enabled = True
            self.status_label.set_text("🌊 Brown noise playing")
    
    def stop_brown_noise(self):
        """Stop brown noise"""
        if self.brown_noise_process:
            try:
                self.brown_noise_process.terminate()
                self.brown_noise_process.wait(timeout=2)
            except:
                try:
                    self.brown_noise_process.kill()
                except:
                    pass
            self.brown_noise_process = None
        self.brown_noise_enabled = False
    
    def play_nsdr_audio(self):
        """Play NSDR music"""
        audio_path = os.path.join(SCRIPT_DIR, "assets", "nsdr.mp3")
        
        if not os.path.exists(audio_path):
            self.status_label.set_text("🧘 NSDR started (no audio file)")
            return
        
        self.nsdr_process = self._play_audio(audio_path, loop=False)
        if self.nsdr_process:
            self.status_label.set_text("🧘 NSDR started with music")
    
    def stop_nsdr_audio(self):
        """Stop NSDR audio"""
        if self.nsdr_process:
            try:
                self.nsdr_process.terminate()
                self.nsdr_process.wait(timeout=2)
            except:
                try:
                    self.nsdr_process.kill()
                except:
                    pass
            self.nsdr_process = None
    
    def _play_audio(self, audio_path, loop=False):
        """Play audio file using available player"""
        players = [
            ('mpv', ['mpv', '--no-video', '--really-quiet'] + (['--loop'] if loop else []) + [audio_path]),
            ('ffplay', ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet'] + (['-loop', '0'] if loop else []) + [audio_path]),
            ('cvlc', ['cvlc', '--play-and-exit', '--quiet'] + (['--loop'] if loop else []) + [audio_path]),
        ]
        
        for name, cmd in players:
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return process
            except FileNotFoundError:
                continue
        
        self.status_label.set_text("⚠️ Install mpv for audio: sudo apt install mpv")
        return None
    
    def pause_audio(self):
        """Pause all audio"""
        for proc in [self.nsdr_process, self.brown_noise_process]:
            if proc:
                try:
                    proc.send_signal(signal.SIGSTOP)
                except:
                    pass
    
    def resume_audio(self):
        """Resume all audio"""
        for proc in [self.nsdr_process, self.brown_noise_process]:
            if proc:
                try:
                    proc.send_signal(signal.SIGCONT)
                except:
                    pass
    
    def show_notification(self):
        """Show desktop notification"""
        try:
            icon_path = os.path.join(SCRIPT_DIR, "assets", "icon.png")
            icon_arg = icon_path if os.path.exists(icon_path) else "appointment-soon"
            
            subprocess.run([
                'notify-send',
                'Neuro Timer',
                'Session complete! Take a break.',
                f'--icon={icon_arg}'
            ], timeout=5)
        except:
            pass
    
    def on_destroy(self, widget):
        """Clean up on window close"""
        self.stop_nsdr_audio()
        self.stop_brown_noise()
        Gtk.main_quit()


def main():
    """Main entry point"""
    os.environ['NO_AT_BRIDGE'] = '1'
    
    # Create assets directory if needed
    assets_dir = os.path.join(SCRIPT_DIR, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    app = NeuroTimer()
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
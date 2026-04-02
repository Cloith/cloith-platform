import subprocess
import time
import os
from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import Header, Static, LoadingIndicator
from textual.containers import Vertical
from screens.core.login_screen import LoginScreen

class LoadingScreen(Screen):
    CSS_PATH = "loading_screen.tcss"
    status_text = reactive("Initializing...")

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="screen-container"):
            yield Static("PLATFORM MANAGER: SECURE BOOT", id="title")
            yield LoadingIndicator()
            yield Static("", id="sub-title") 
            

    def watch_status_text(self, message: str) -> None:
        """Update the UI label whenever the reactive variable changes."""
        try:
            self.query_one("#sub-title", Static).update(message)
        except: pass

    def on_mount(self) -> None:
        """The UI is now visible, so we start the background worker."""
        self.run_secure_boot()

    @work(thread=True)
    def run_secure_boot(self) -> None:
        """
        This is our Assistant Chef (Separate Thread).
        It can run blocking 'subprocess.run' without freezing the UI.
        """
        tasks = [
            ("Logging out of Bitwarden...", ["bw", "logout"]),
            ("Stopping VPN (Tailscale)...", ["sudo", "pkill", "tailscaled"]),
            ("Cleaning Docker PID...", ["sudo", "rm", "-f", "/var/run/docker.pid"]),
            ("Cleaning Docker Socket...", ["sudo", "rm", "-f", "/var/run/docker.sock"]),
        ]

        subprocess.Popen(["sudo", "dockerd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

        for description, command in tasks:
            # We use 'call_from_thread' to safely update the UI from our thread
            self.app.call_from_thread(setattr, self, "status_text", description)
            
            # This is 'Blocking' code, but it's okay because it's in a thread!
            subprocess.run(command, capture_output=True)
            
            # Give the user a moment to see the progress
            time.sleep(0.6)

        self.app.call_from_thread(setattr, self, "status_text", "Igniting Docker Engine...")
        subprocess.Popen(
            ["sudo", "dockerd"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            start_new_session=True
        )

        max_retries = 10
        for i in range(max_retries):
            self.app.call_from_thread(setattr, self, "status_text", f"Waiting for Docker ({i+1}/{max_retries})...")
            # Check if the socket file exists
            if os.path.exists("/var/run/docker.sock"):
                break
            time.sleep(1)
        else:
            self.app.call_from_thread(setattr, self, "status_text", "[bold red]Docker failed to start![/bold red]")
            time.sleep(2)

        # Final message
        self.app.call_from_thread(setattr, self, "status_text", "Secure Boot Complete!")
        time.sleep(1)
        
        # Tell the Main Chef to remove the screen
        #self.app.call_from_thread(self.app.switch_screen, LoginScreen())
        self.app.call_from_thread(self.action_show_login)
    
    def action_show_login(self):
        self.app.push_screen(LoginScreen())
import fcntl, os, sys
from rich.console import Console

console = Console()

class InstanceLock:
    def __init__(self, lock_path="/tmp/platform_manager.lock"):
        self.lock_path = lock_path

    def acquire(self):
        """Ensures only one instance runs, with stale lock detection."""
        self.lock_file = open(self.lock_path, 'a+')
        
        try:
            fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            self.lock_file.seek(0)
            content = self.lock_file.read().strip()
            
            if content.isdigit():
                old_pid = int(content)
                try:
                    os.kill(old_pid, 0) 
                except OSError:
                    console.print(f"[yellow]Detected stale lock from dead PID {old_pid}. Cleaning up...[/yellow]")
                    self.lock_file.close()
                    try:
                        os.remove(self.lock_path)
                    except: pass
                    return None

            console.print(f"[bold red]Error: Another instance (PID {content}) is already running![/bold red]")
            sys.exit(1)

        self.lock_file.seek(0)
        self.lock_file.truncate()
        self.lock_file.write(str(os.getpid()))
        self.lock_file.flush()
        os.fsync(self.lock_file.fileno()) 
        return self.lock_file


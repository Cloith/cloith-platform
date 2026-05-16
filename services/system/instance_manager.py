import fcntl, os, sys
from rich.console import Console

console = Console()

class InstanceLock:
    def __init__(self, lock_path="/tmp/platform_manager.lock"):
        self.lock_path = lock_path
        self.lock_file = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_UN)
                self.lock_file.close()
                if os.path.exists(self.lock_path):
                    os.remove(self.lock_path)
            except Exception:
                pass

    def acquire(self):
        try:
            self.lock_file = open(self.lock_path, 'a+')
            fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            self.lock_file.seek(0)
            content = self.lock_file.read().strip()
            
            if content.isdigit():
                old_pid = int(content)
                try:
                    os.kill(old_pid, 0) 
                except OSError:
                    
                    self.lock_file.close()
                    if os.path.exists(self.lock_path):
                        os.remove(self.lock_path)
                    return self.acquire()

            console.print(f"[bold red]Error: Another instance (PID {content}) is already running![/bold red]")
            sys.exit(1)


        self.lock_file.seek(0)
        self.lock_file.truncate()
        self.lock_file.write(str(os.getpid()))
        self.lock_file.flush()
        os.fsync(self.lock_file.fileno()) 
        return self
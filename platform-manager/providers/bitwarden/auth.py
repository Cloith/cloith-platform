import pexpect
import re
from rich.console import Console

console = Console()

def login_to_bitwarden(email, password, otp_getter):

    # Spawn inside the loop so each attempt is fresh
    child = pexpect.spawn("bw login", encoding='utf-8', timeout=20)
    
    try:
        child.expect("Email address:")
        child.sendline(email)
        child.expect("Master password:")
        child.sendline(password)
       
        next_step = child.expect([
            "You are logged in!",
            "Enter OTP sent to login email:", 
            "Two-step login code:",
            "Invalid master password",
            "The Email field is not a valid e-mail address.",
            pexpect.EOF
        ])
        if next_step in [1, 2]:
            otp_code = otp_getter()
            child.sendline(otp_code)
            sub_step = child.expect(["You are logged in!", "invalid new device otp", pexpect.TIMEOUT])
            if sub_step == 1: return 5, None
            if sub_step == 2: return 8, None
        elif next_step == 3: return 3, None
        elif next_step == 4: return 4, None
        elif next_step == 5: return 8, None

        # Step 3: Capture the Key
        child.expect(pexpect.EOF)  
 
        output = child.before 
        match = re.search(r'BW_SESSION="([^"]+)"', output)
        
        if match:
            session_key = match.group(1)
            return 1, session_key 
        else:
            return 8, None

    except (pexpect.TIMEOUT, pexpect.EOF):
        return 8, None
    finally:
        child.close()
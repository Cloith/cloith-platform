# 🖥️ Platform Manager (`manager.py`)

## Overview
The central entry point for the Cloith Platform. It coordinates between Authentication and Configuration (Ansible).

## Key Technical Decisions
- **Interactive UX:** Uses `questionary` to prevent "Command-Line Fatigue" and reduce human error during resource selection.
- **Session Scoping:** The `session_key` is passed as a variable to sub-modules, ensuring that sub-processes (like Terraform) only have access to secrets when explicitly invoked.
- **Visual Feedback:** Integrated `rich` for clear, color-coded status updates.

## Logic Flow
1. **Auth:** Calls `auth.py` to retrieve a temporary JWT session from Bitwarden.
2. **Loop:** Enters a stateful loop where the user selects the "Scenario."
3. **Cleanup:** On exit, triggers a vault lock to ensure no persistent access is left on the host.

🔐 Authentication Module (auth.py)
Overview
The auth.py module serves as the Secure Gateway for the Cloith Platform Manager. It handles interactive authentication with the Bitwarden Vault using the Bitwarden CLI (bw), ensuring that the manager operates in a "Zero-Knowledge" environment where no master passwords or API keys are ever stored on the local filesystem.

Key Technical Decisions
1. The "Pre-Flight Reset" Policy
Decision: Every login attempt begins with a mandatory bw logout.

Reasoning: This clears any stale session keys or half-authenticated states left on the machine. It ensures that the environment is "Clean" before the user enters sensitive credentials.

2. Interactive Pexpect Automation
Decision: Using the pexpect library to wrap the Bitwarden CLI.

Reasoning: The Bitwarden CLI is designed for human interaction. pexpect allows the Python script to "talk" to the CLI, watching for specific prompts (like Enter OTP... or Invalid master password) and responding in real-time. This provides a seamless, "app-like" experience while keeping the security of the official CLI.

3. Multi-Factor Authentication (MFA) Support
Decision: Explicitly handling expect patterns for both Email OTP and 2FA Authenticator codes.

Reasoning: In a professional environment (like LSEG), MFA is non-negotiable. This module ensures that even if the user has 2FA enabled, the Manager can handle the extra step without crashing or requiring the user to drop out to a raw terminal.

4. Memory-Only Session Capture
Decision: Extracting the BW_SESSION key using Regular Expressions (re) and returning it directly to the manager.py runtime memory.

Reasoning: By capturing the key in a variable and never writing it to a file, we significantly reduce the attack surface. If the computer is powered off or the process is killed, the key vanishes instantly.

Logic Flow Breakdown
Spawn Process: Starts a fresh bw login instance.

Interactive Prompts: Uses questionary to collect email/password. Note that questionary.password() is used so characters are not echoed to the screen.

State Detection:

If Success: Captures the session key.

If MFA Required: Pauses and asks the user for their code.

If Failure: Provides a clean "Try Again" loop or exits gracefully.

Cleanup: The finally block ensures the pexpect child process is closed to prevent "zombie" processes from hanging in the background.

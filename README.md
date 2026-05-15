# Platform Manager
> **Bridging the "Ops Gap": Professional-grade automation for secure, low-cost VPS orchestration.**

[![Security: Zero-Leak](https://img.shields.io/badge/Security-Zero--Leak-red.svg)](#security-philosophy)
[![Infrastructure: Agnostic](https://img.shields.io/badge/Infra-Agnostic-blue.svg)](#the-problem-the-ops-gap)
[![UI: Textual](https://img.shields.io/badge/UI-Textual-green.svg)](https://textual.textualize.io/)

### Current Limitations (Scope)
* **Solo-Developer / Single-Machine Scope:** The lock mechanism utilizes a local file path (`/tmp/platform_manager.lock`). Therefore, it only prevents concurrent execution *on the same machine*. 
* **Team Deployment Warning:** If multiple developers run this tool from different machines simultaneously against the same remote infrastructure, the local lock will not prevent overlapping changes.

## The Mission: Democratizing Secure Hosting
Modern developers face a "Time vs. Money" dilemma: pay a massive premium for managed cloud platforms (AWS/Heroku) or struggle with the manual security "hustle" of a raw VPS.

**Cloith Platform** makes the "cheap naked VPS" option a professional reality. By automating critical provisioning and "Zero-Leak" security steps, this tool allows developers to maintain full control of their hardware without sacrificing the operational convenience of a managed service.


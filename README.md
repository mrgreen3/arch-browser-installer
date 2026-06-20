# arch-browser-installer (ABI)

A browser-based installer for Arch Linux derived distributions. No GUI toolkit required — uses Python stdlib HTTP server and the system's existing Firefox instance to serve a simple HTML wizard.

## How it works

`abi-installer.py` starts a local HTTP server on port 7777. A bash launcher opens Firefox pointing at it. The wizard walks the user through disk selection, partitioning, and system configuration, then runs the install in a background thread with live progress updates.

## Requirements

- Booted from an Arch-based live ISO
- Firefox installed on the live system
- Python 3 (stdlib only — no pip dependencies)
- `rsync`, `arch-chroot`, `genfstab`, `grub`

## Usage

```bash
sudo python3 abi-installer.py
```

Or via the launcher script:

```bash
fb-install
```

## Architecture

| File | Role |
|------|------|
| `abi-installer.py` | HTTP server, API routes, install logic, embedded HTML/CSS/JS |

Pure helper functions (`validate_name`, `parse_lsblk`, `parse_rsync_progress`, `step_percent`) are importable and unit-testable without running the server.

## Licence

MIT

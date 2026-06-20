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
| `abi-installer.py` | Entry point — starts HTTP server |
| `lib/ui.py` | Embedded HTML/CSS/JS wizard |
| `lib/parse.py` | Pure helpers: `validate_name`, `parse_lsblk*`, `parse_rsync_progress`, `validate_install_cfg` |
| `lib/state.py` | Shared install state, step weights, log path, `set_state`, `step_percent` |
| `lib/system.py` | All install operations: partition, copy, configure, bootloader, cleanup |
| `lib/server.py` | `Handler` — HTTP routes wiring the wizard to the install logic |

Pure helpers in `lib/parse.py` and `lib/state.py` are importable and unit-testable without running the server or a live system.

## Adapting for another distro

Two things in `lib/system.py` are FruitBang-specific:

**Live username** — `configure_user` renames the user `live`. If your ISO uses a different live username (e.g. `archie`, `user`), change the `live = "live"` line in that function.

**Keymap / WM config** — `configure_keymap` writes `vconsole.conf` (generic) but also patches the xkb layout in `~/.config/mango/config.conf` (MangoWM-specific). Remove or replace that `sed` line if you're using a different window manager.

## Licence

MIT

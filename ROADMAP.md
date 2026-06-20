# ROADMAP

## Done

- [x] Browser-based wizard (disk select, partition, configure, install, reboot)
- [x] Auto-partition mode (UEFI GPT and BIOS MBR)
- [x] Manual partition selection
- [x] Live rsync progress bar
- [x] Hostname, timezone, locale, keymap configuration
- [x] User creation (rename live user, set password)
- [x] GRUB install (UEFI and BIOS)
- [x] Post-install cleanup (live services, sudo hardening)
- [x] Bash launcher (`abi-install`) with Firefox open and server teardown
- [x] Split monolith into `lib/` modules (ui, parse, state, system, server)

## Near-term

- [ ] Unit tests for pure helpers (`parse.py`, `state.py`) — no live system needed
- [ ] Decouple `configure_keymap` from MangoWM — make WM config path configurable or pluggable
- [ ] Update `README.md` architecture table to reflect `lib/` split
- [ ] Validate `root_part` is not the live medium before formatting
- [ ] Better error display: show last N lines of `/tmp/fb-install.log` in the browser on failure

## Medium-term

- [ ] Support for swap partition (optional, selectable in wizard)
- [ ] EFI partition format validation before install (warn if not vfat)
- [ ] Distro-agnostic config: move FruitBang-specific paths (`/run/archiso`, `airootfs`) to a config dict
- [ ] Configurable live username (currently hardcoded as `live`)
- [ ] Browser-compatible fallback if Firefox not found (e.g. Chromium, Epiphany)

## Backlog / Ideas

- [ ] Encrypt root with LUKS (optional wizard step)
- [ ] Btrfs root with subvolumes as alternative to ext4
- [ ] Log viewer panel in the browser (tail `/tmp/fb-install.log` via polling)
- [ ] Dry-run mode for testing wizard flow without a real disk
- [ ] Package as a standalone installable script (no repo clone required)

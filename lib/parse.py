import json
import re

NAME_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
RSYNC_PCT_RE = re.compile(r"\s(\d{1,3})%")

VALID_LAYOUTS = {
    "us", "gb", "de", "fr", "es", "it", "pt", "br",
    "nl", "pl", "ru", "se", "no", "dk", "fi", "be", "ch",
}

VALID_TIMEZONES = {
    "Europe/London", "Europe/Dublin", "Europe/Lisbon", "Europe/Paris",
    "Europe/Brussels", "Europe/Amsterdam", "Europe/Berlin", "Europe/Vienna",
    "Europe/Zurich", "Europe/Madrid", "Europe/Rome", "Europe/Warsaw",
    "Europe/Stockholm", "Europe/Oslo", "Europe/Copenhagen", "Europe/Helsinki",
    "Europe/Athens", "Europe/Bucharest", "Europe/Moscow", "Europe/Istanbul",
    "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
    "America/Toronto", "America/Vancouver", "America/Sao_Paulo", "America/Mexico_City",
    "America/Argentina/Buenos_Aires", "Asia/Dubai", "Asia/Kolkata", "Asia/Bangkok",
    "Asia/Singapore", "Asia/Shanghai", "Asia/Tokyo", "Asia/Seoul", "Asia/Jerusalem",
    "Africa/Johannesburg", "Africa/Cairo", "Australia/Sydney", "Pacific/Auckland", "UTC",
}

VALID_LOCALES = {
    "en_GB.UTF-8", "en_US.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8", "es_ES.UTF-8",
    "it_IT.UTF-8", "pt_PT.UTF-8", "pt_BR.UTF-8", "nl_NL.UTF-8", "pl_PL.UTF-8",
    "ru_RU.UTF-8", "sv_SE.UTF-8", "nb_NO.UTF-8", "da_DK.UTF-8", "fi_FI.UTF-8",
    "zh_CN.UTF-8", "ja_JP.UTF-8", "ko_KR.UTF-8",
}


def validate_name(s):
    """True if s is a safe hostname/username (lowercase, no shell metachars)."""
    return bool(NAME_RE.match(s))


def parse_lsblk(json_str):
    """Parse `lsblk -J` output into a flat list of partitions.

    Returns list of {"path": "/dev/sda1", "size": "512M"}.
    Only type=="part" entries are returned (disks excluded).
    """
    data = json.loads(json_str)
    out = []

    def walk(node):
        if node.get("type") == "part":
            out.append({"path": "/dev/" + node["name"], "size": node.get("size", "")})
        for child in node.get("children", []):
            walk(child)

    for dev in data.get("blockdevices", []):
        walk(dev)
    return out


def parse_lsblk_disks(json_str):
    """Parse `lsblk -J` output, return whole disks only (type==disk)."""
    data = json.loads(json_str)
    out = []
    for dev in data.get("blockdevices", []):
        if dev.get("type") == "disk":
            out.append({"path": "/dev/" + dev["name"], "size": dev.get("size", "")})
    return out


def parse_rsync_progress(line):
    """Extract integer percent from an rsync --info=progress2 line, or None."""
    m = RSYNC_PCT_RE.search(line)
    if not m:
        return None
    pct = int(m.group(1))
    return pct if 0 <= pct <= 100 else None


def validate_install_cfg(cfg):
    """Return error string if cfg invalid, else None."""
    if not cfg.get("root_part"):
        return "root partition required"
    if not validate_name(cfg.get("hostname", "")):
        return "invalid hostname"
    if not validate_name(cfg.get("username", "")):
        return "invalid username"
    if not cfg.get("password"):
        return "password required"
    if cfg.get("timezone", "UTC") not in VALID_TIMEZONES:
        return "invalid timezone"
    if cfg.get("locale", "en_GB.UTF-8") not in VALID_LOCALES:
        return "invalid locale"
    if cfg.get("keymap", "us") not in VALID_LAYOUTS:
        return "invalid keyboard layout"
    return None

import json
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.parse import (
    validate_name,
    parse_lsblk,
    parse_lsblk_disks,
    parse_rsync_progress,
    validate_install_cfg,
    validate_custom_layout,
)
from lib.system import build_sfdisk_script


class TestValidateName(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate_name("kev"))
        self.assertTrue(validate_name("fruit-bang"))
        self.assertTrue(validate_name("user_01"))

    def test_invalid(self):
        self.assertFalse(validate_name(""))
        self.assertFalse(validate_name("Kev"))
        self.assertFalse(validate_name("ke v"))
        self.assertFalse(validate_name("ke;v"))
        self.assertFalse(validate_name("a" * 33))


class TestParseLsblk(unittest.TestCase):
    LSBLK_JSON = json.dumps({
        "blockdevices": [{
            "name": "sda", "type": "disk", "size": "500G",
            "children": [
                {"name": "sda1", "type": "part", "size": "512M"},
                {"name": "sda2", "type": "part", "size": "499.5G"},
            ],
        }]
    })

    def test_returns_partitions_only(self):
        parts = parse_lsblk(self.LSBLK_JSON)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0]["path"], "/dev/sda1")
        self.assertEqual(parts[1]["path"], "/dev/sda2")

    def test_no_partitions(self):
        data = json.dumps({"blockdevices": [{"name": "sda", "type": "disk", "size": "500G"}]})
        self.assertEqual(parse_lsblk(data), [])


class TestParseLsblkDisks(unittest.TestCase):
    LSBLK_JSON = json.dumps({
        "blockdevices": [
            {"name": "sda", "type": "disk", "size": "500G",
             "children": [{"name": "sda1", "type": "part", "size": "500G"}]},
            {"name": "sdb", "type": "disk", "size": "1T"},
        ]
    })

    def test_returns_disks_only(self):
        disks = parse_lsblk_disks(self.LSBLK_JSON)
        self.assertEqual(len(disks), 2)
        self.assertEqual(disks[0]["path"], "/dev/sda")
        self.assertEqual(disks[1]["path"], "/dev/sdb")


class TestParseRsyncProgress(unittest.TestCase):
    def test_extracts_percent(self):
        self.assertEqual(parse_rsync_progress("    1,234,567  42%  10.00MB/s"), 42)
        self.assertEqual(parse_rsync_progress("  100%  done"), 100)
        self.assertEqual(parse_rsync_progress("    0%  starting"), 0)

    def test_no_match(self):
        self.assertIsNone(parse_rsync_progress("sending incremental file list"))
        self.assertIsNone(parse_rsync_progress(""))


class TestValidateInstallCfg(unittest.TestCase):
    BASE = {
        "root_part": "/dev/sda1",
        "hostname": "fruitbang",
        "username": "kev",
        "password": "secret",
        "timezone": "Europe/London",
        "locale": "en_GB.UTF-8",
        "keymap": "gb",
    }

    def test_valid(self):
        self.assertIsNone(validate_install_cfg(self.BASE))

    def test_missing_root_part(self):
        cfg = {**self.BASE, "root_part": ""}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_bad_hostname(self):
        cfg = {**self.BASE, "hostname": "Bad Host!"}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_bad_username(self):
        cfg = {**self.BASE, "username": "Root User"}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_empty_password(self):
        cfg = {**self.BASE, "password": ""}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_invalid_timezone(self):
        cfg = {**self.BASE, "timezone": "Moon/Base"}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_invalid_locale(self):
        cfg = {**self.BASE, "locale": "xx_XX.UTF-8"}
        self.assertIsNotNone(validate_install_cfg(cfg))

    def test_invalid_keymap(self):
        cfg = {**self.BASE, "keymap": "zz"}
        self.assertIsNotNone(validate_install_cfg(cfg))


class TestValidateCustomLayout(unittest.TestCase):
    def test_valid_uefi_minimal(self):
        parts = [{"size": "512M", "role": "efi"},
                 {"size": "", "role": "root", "fs": "ext4"}]
        self.assertIsNone(validate_custom_layout(parts, True))

    def test_valid_uefi_full(self):
        parts = [{"size": "512M", "role": "efi"},
                 {"size": "4G", "role": "swap"},
                 {"size": "30G", "role": "root", "fs": "btrfs"},
                 {"size": "", "role": "home", "fs": "ext4"}]
        self.assertIsNone(validate_custom_layout(parts, True))

    def test_valid_bios(self):
        self.assertIsNone(
            validate_custom_layout([{"size": "", "role": "root", "fs": "ext4"}], False))

    def test_empty(self):
        self.assertIsNotNone(validate_custom_layout([], True))

    def test_no_root(self):
        self.assertIsNotNone(
            validate_custom_layout([{"size": "512M", "role": "efi"}], True))

    def test_two_roots(self):
        parts = [{"size": "10G", "role": "root"}, {"size": "", "role": "root"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))

    def test_efi_in_bios(self):
        parts = [{"size": "512M", "role": "efi"}, {"size": "", "role": "root"}]
        self.assertIsNotNone(validate_custom_layout(parts, False))

    def test_missing_efi_in_uefi(self):
        self.assertIsNotNone(
            validate_custom_layout([{"size": "", "role": "root"}], True))

    def test_blank_size_not_last(self):
        parts = [{"size": "", "role": "root"}, {"size": "512M", "role": "efi"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))

    def test_bad_size(self):
        parts = [{"size": "512MB", "role": "efi"}, {"size": "", "role": "root"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))

    def test_efi_too_small(self):
        parts = [{"size": "100M", "role": "efi"}, {"size": "", "role": "root"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))

    def test_bad_fs(self):
        parts = [{"size": "512M", "role": "efi"},
                 {"size": "", "role": "root", "fs": "zfs"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))

    def test_bad_role(self):
        parts = [{"size": "1G", "role": "bogus"}, {"size": "", "role": "root"}]
        self.assertIsNotNone(validate_custom_layout(parts, True))


class TestBuildSfdiskScript(unittest.TestCase):
    def test_uefi_full(self):
        parts = [{"size": "512M", "role": "efi"},
                 {"size": "4G", "role": "swap"},
                 {"size": "30G", "role": "root"},
                 {"size": "", "role": "home"}]
        script = build_sfdisk_script(parts, True)
        self.assertEqual(
            script,
            "label: gpt\n,512M,U\n,4G,S\n,30G,L\n,,L\n")

    def test_bios_root_remainder(self):
        script = build_sfdisk_script([{"size": "", "role": "root"}], False)
        self.assertEqual(script, "label: dos\n,,83,*\n")

    def test_bios_swap_then_root(self):
        parts = [{"size": "4G", "role": "swap"}, {"size": "", "role": "root"}]
        script = build_sfdisk_script(parts, False)
        self.assertEqual(script, "label: dos\n,4G,82\n,,83,*\n")


if __name__ == "__main__":
    unittest.main()

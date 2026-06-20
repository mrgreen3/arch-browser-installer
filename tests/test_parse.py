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
)


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


if __name__ == "__main__":
    unittest.main()

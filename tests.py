#!/usr/bin/env python3
#
# Copyright (C) 2024-2025 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
from os.path import dirname
import os
import subprocess
import unittest
import shutil
import json


SUCCESS = 93
ERROR = 94
NONE = 95


sevenzip = os.environ.get("7z", "7z")
sevenzip_args = "e -aos"

unrar = os.environ.get("unrar", "unrar")
unrar_args = "e -idp -ai -o-"

root = dirname(__file__)

test_data_dir = root + "/test_data"
tmp_dir = root + "/tmp"

test_zips = ["test1.zip", "test2.zip", "test3.zip"]
test_partitioned_zips = ["test4.zip", "test4.z01", "test4.z02"]
test_rars = ["test1.rar", "test2.rar", "test3.rar"]
test_partitioned_rars = ["test4.r01", "test4.r02", "test4.r03"]
result_files = [tmp_dir + "/test1.txt", tmp_dir + "/test2.txt", tmp_dir + "/test3.txt"]
test_partitioned_result_files = ["test4.bin"]
test_partitioned_result_files = [tmp_dir + "/test4.bin"]

host = "127.0.0.1"
username = "TestUser"
password = "TestPassword"
port = "6789"


def get_python():
    if os.name == "nt":
        return "python"
    return "python3"


def run_script():
    sys.stdout.flush()
    proc = subprocess.Popen(
        [get_python(), root + "/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    out, err = proc.communicate()
    proc.pid
    ret_code = proc.returncode
    return (out.decode(), int(ret_code), err.decode())


def set_default_env():
    # NZBGet global options
    os.environ["NZBNA_EVENT"] = "FILE_DOWNLOADED"
    os.environ["NZBPP_DIRECTORY"] = tmp_dir
    os.environ["NZBOP_ARTICLECACHE"] = "8"
    os.environ["NZBPO_PASSACTION"] = "PASSACTION"
    os.environ["NZBOP_CONTROLPORT"] = port
    os.environ["NZBOP_CONTROLIP"] = host
    os.environ["NZBOP_CONTROLUSERNAME"] = username
    os.environ["NZBOP_CONTROLPASSWORD"] = password
    os.environ["NZBPR_PASSWORDDETECTOR_HASPASSWORD"] = "no"
    os.environ["NZBOP_EXTENSIONS"] = ""
    os.environ["NZBOP_UNPACK"] = "yes"
    os.environ["NZBPP_TOTALSTATUS"] = "SUCCESS"

    # script options
    os.environ["NZBNA_CATEGORY"] = "Movies"
    os.environ["NZBNA_DIRECTORY"] = tmp_dir
    os.environ["NZBNA_NZBNAME"] = "TestNZB"
    os.environ["NZBPR_FAKEDETECTOR_SORTED"] = "yes"
    os.environ["NZBOP_TEMPDIR"] = tmp_dir
    os.environ["NZBOP_SEVENZIPCMD"] = sevenzip
    os.environ["NZBPO_SEVENZIPCMD"] = sevenzip
    os.environ["NZBPO_SEVENZIPARGS"] = sevenzip_args
    os.environ["NZBOP_UNRARCMD"] = unrar
    os.environ["NZBPO_UNRARCMD"] = unrar
    os.environ["NZBPO_UNRARARGS"] = unrar_args
    os.environ["NZBPO_WAITTIME"] = "0"
    os.environ["NZBPO_DELETELEFTOVER"] = "no"
    os.environ["NZBOP_UNPACKCLEANUPDISK"] = "no"


class Tests(unittest.TestCase):

    def test_sevenzip(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()

        shutil.copytree(
            test_data_dir,
            tmp_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.r*"),
        )

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_unrar(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()

        shutil.copytree(
            test_data_dir,
            tmp_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.z*"),
        )

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_sevenzip_with_empty_sevenzipcmd_option(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()
        os.environ["NZBPO_SEVENZIPCMD"] = ""

        shutil.copytree(
            test_data_dir,
            tmp_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.r*"),
        )

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_unrar_with_empty_unrarcmd_option(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()
        os.environ["NZBPO_UNRARCMD"] = ""

        shutil.copytree(
            test_data_dir,
            tmp_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("*.z*"),
        )

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_multiple_folders_zips(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()

        for index, zip in enumerate(test_zips):
            os.mkdir(str(f"{tmp_dir}/{index}"))
            shutil.copyfile(f"{test_data_dir}/{zip}", f"{tmp_dir}/{index}/{zip}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_multiple_folders_rars(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()

        for index, rar in enumerate(test_rars):
            os.mkdir(str(f"{tmp_dir}/{index}"))
            shutil.copyfile(f"{test_data_dir}/{rar}", f"{tmp_dir}/{index}/{rar}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_delete_leftovers_zips(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()
        os.environ["NZBPO_DELETELEFTOVER"] = "yes"

        for zip in test_partitioned_zips:
            shutil.copyfile(f"{test_data_dir}/{zip}", f"{tmp_dir}/{zip}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in test_partitioned_zips:
            self.assertFalse(os.path.exists(file))

        for file in test_partitioned_result_files:
            self.assertTrue(os.path.exists(file))
        shutil.rmtree(tmp_dir)

    def test_delete_leftovers_rars(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()
        os.environ["NZBPO_DELETELEFTOVER"] = "yes"

        for rar in test_partitioned_rars:
            shutil.copyfile(f"{test_data_dir}/{rar}", f"{tmp_dir}/{rar}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in test_partitioned_rars:
            self.assertFalse(os.path.exists(file))

        for file in test_partitioned_result_files:
            self.assertTrue(os.path.exists(file))
        shutil.rmtree(tmp_dir)

    def test_manifest(self):
        with open(root + "/manifest.json", encoding="utf-8") as file:
            try:
                json.loads(file.read())
            except ValueError as e:
                self.fail("manifest.json is not valid.")


if __name__ == "__main__":
    unittest.main()

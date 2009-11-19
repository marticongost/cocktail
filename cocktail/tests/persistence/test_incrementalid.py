#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from unittest import TestCase
from cocktail.tests.persistence.tempstoragemixin import TempStorageMixin


class IncrementalIdTestCase(TempStorageMixin, TestCase):

    python_cmd = "python"
    zeo_cmd = "runzeo"
    db_host = "127.0.0.1"
    db_port = "43784"

    def test_acquisition(self):

        from cocktail.persistence import incremental_id
       
        n = 100
        ids = set(incremental_id() for i in range(n))

        self.assertEqual(len(ids), n)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))
 
    def test_multithreaded_acquisition(self):
 
        from cocktail.tests.utils import run_concurrently
        from cocktail.persistence import incremental_id
        
        thread_count = 100
        ids_per_thread = 50
        ids = set()

        def acquisition_thread():
            for i in range(ids_per_thread):
                ids.add(incremental_id())

        run_concurrently(thread_count, acquisition_thread)

        self.assertEqual(len(ids), thread_count * ids_per_thread)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))

    def test_multiprocess_acquisition(self):

        from tempfile import mkdtemp
        from subprocess import Popen, PIPE
        from os import kill
        from os.path import join
        from signal import SIGKILL
        from shutil import rmtree

        process_count = 10
        ids_per_process = 100
        ids = set()

        temp_dir = mkdtemp()

        try:
            subprocess_file = join(temp_dir, "childprocess.py")
            subprocess_code = """
from ZEO.ClientStorage import ClientStorage
from cocktail.persistence import datastore, incremental_id
datastore.storage = ClientStorage(("%s", %s))

try:
    for i in range(%d):
        print incremental_id()
finally:
    datastore.close()
            """ % (self.db_host, self.db_port, ids_per_process)
            f = open(subprocess_file, "w")
            f.write(subprocess_code)
            f.close()

            zeo_storage_file = join(temp_dir, "database.fs")
            zeo_invocation = "%s -f %s -a %s:%s" % (
                self.zeo_cmd,
                zeo_storage_file,
                self.db_host,
                self.db_port
            )
            zeo_proc = Popen(
                zeo_invocation,
                shell = True
            )
            try:
                processes = []

                for p in range(process_count):

                    proc = Popen(
                        self.python_cmd + " " + subprocess_file,
                        shell = True,
                        stdout = PIPE,
                        stderr = PIPE
                    )
                    processes.append(proc)
                
                done = False

                while not done:
                    done = True
                    for proc in processes:
                        return_code = proc.poll()
                        if return_code is None:
                            done = False
                        elif return_code == 0:
                            ids.update(map(int, proc.stdout.read().split()))
                        else:
                            raise OSError(
                                "Error running child process: "
                                + proc.stderr.read()
                            )
            finally:
                kill(zeo_proc.pid, SIGKILL)
        finally:
            rmtree(temp_dir)

        # Validate generated ids
        self.assertEqual(len(ids), process_count * ids_per_process)

        for id in ids:
            self.assertTrue(id)
            self.assertTrue(isinstance(id, int))

    def test_conflict_resolution(self):
        
        from cocktail.persistence import datastore, incremental_id
        datastore.root["foo"] = "bar"
        incremental_id()
        datastore.commit()


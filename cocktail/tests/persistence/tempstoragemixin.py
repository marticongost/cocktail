#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""

class TempStorageMixin(object):

    def setUp(self):
        from os.path import join        
        from tempfile import mkdtemp
        from ZODB.FileStorage import FileStorage
        from cocktail.persistence import datastore
        self._temp_dir = mkdtemp()
        datastore.abort()
        datastore.close()
        datastore.storage = FileStorage(join(self._temp_dir, "testdb.fs"))

    def tearDown(self):
        from cocktail.persistence import datastore
        from shutil import rmtree
        datastore.abort()
        datastore.close()
        rmtree(self._temp_dir)


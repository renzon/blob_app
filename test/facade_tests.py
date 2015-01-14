# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.ext.ndb.blobstore import BlobInfo

from base import BlobstoreTestCase
from blob_app import blob_facade as facade
from blob_app.blob_model import BlobFile
from gaegraph.model import Node


class SaveAndListTests(BlobstoreTestCase):
    def test_save_without_owner(self):
        blob_key = self.save_blob()
        blob_info = BlobInfo.get(blob_key)
        facade.save_blob_files_cmd([blob_info]).execute()
        blob_file = BlobFile.query().get()
        self.assertIsNotNone(blob_file)
        files = facade.list_blob_files_cmd()()
        self.assertListEqual([blob_file], files)

    def test_save_with_owner(self):
        owner = Node()
        owner.put()
        blob_key = self.save_blob()
        blob_info = BlobInfo.get(blob_key)
        facade.save_blob_files_cmd([blob_info], str(owner.key.id())).execute()
        blob_file = BlobFile.query().get()
        self.assertIsNotNone(blob_file)
        files = facade.list_blob_files_cmd(owner)()
        self.assertListEqual([blob_file], files)


class DeleteTests(BlobstoreTestCase):
    def test_delete_without_owner(self):
        blob_key = self.save_blob()

        blob_info = BlobInfo.get(blob_key)
        facade.save_blob_files_cmd([blob_info]).execute()
        blob_file = BlobFile.query().get()
        facade.delete_blob_file_cmd(blob_file).execute()
        files = facade.list_blob_files_cmd()()
        self.assertListEqual([], files)
        files = facade.list_blob_files_cmd('1')()
        self.assertListEqual([], files)


    def test_delete_with_owner(self):
        owner = Node()
        owner.put()
        blob_key = self.save_blob()

        blob_info = BlobInfo.get(blob_key)
        facade.save_blob_files_cmd([blob_info]).execute()
        blob_file = BlobFile.query().get()
        facade.delete_blob_file_cmd(blob_file).execute()
        files = facade.list_blob_files_cmd()()
        self.assertListEqual([], files)
        files = facade.list_blob_files_cmd(owner)()
        self.assertListEqual([], files)


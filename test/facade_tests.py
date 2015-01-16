# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from google.appengine.ext.ndb.blobstore import BlobInfo

from base import BlobstoreTestCase
from blob_app import blob_facade as facade
from blob_app.blob_commands import CreateOwnerToBlob
from blob_app.blob_model import BlobFile
from gaebusiness.business import CommandParallel
from gaegraph.business_base import CreateArc
from gaegraph.model import Node
from mommygae import mommy


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


class ListImageTests(BlobstoreTestCase):
    def test_list_without_owner_and_img_url_none(self, img_url=None):
        blob_key = self.save_blob()
        blobs = [mommy.save_one(BlobFile, img_url=img_url, blob_key=blob_key) for i in xrange(3)]
        blobs.reverse()  # The search is on desc order on back, this is the reason of this reversing
        SOME = 'https://some.image.com'
        blobs[0].img_url = SOME
        blobs[0].put()
        ANOTHER = 'https://default.image.com'
        imgs = facade.list_imgs_cmd(default=ANOTHER)()
        self.assertListEqual([SOME, ANOTHER, ANOTHER], imgs)

    def test_list_without_owner_and_img_url_empyt(self):
        self.test_list_without_owner_and_img_url_none('')

    def test_list_with_owner_and_img_url_empty(self):
        self.test_list_with_owner_and_img_url_none('')

    def test_list_with_owner_and_img_url_none(self, img_url=None):
        owner = Node()
        owner.put()
        blob_key = self.save_blob()
        blobs = [mommy.save_one(BlobFile, img_url=img_url, blob_key=blob_key) for i in xrange(3)]

        CommandParallel(*(CreateOwnerToBlob(owner, b) for b in blobs)).execute()
        blobs.reverse()  # The search is on desc order on back, this is the reason of this reversing
        SOME = 'https://some.image.com'
        blobs[0].img_url = SOME
        blobs[0].put()
        ANOTHER = 'https://default.image.com'
        imgs = facade.list_imgs_cmd(owner=owner, default=ANOTHER)()
        self.assertListEqual([SOME, ANOTHER, ANOTHER], imgs)


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


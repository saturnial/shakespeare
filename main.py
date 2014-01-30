import cgi
import os
import urllib

from collections import defaultdict

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb

import jinja2
import webapp2

import models

import map_reduce

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

  def get(self):
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render())


class Search(webapp2.RequestHandler):

  def get(self):
    query = self.request.get('query')
    result = models.Word.query(models.Word.word == query)
    template_values = {'result': result.get()}
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))


class AdminHandler(webapp2.RequestHandler):

  def get(self):
    template_values = {'upload_url': blobstore.create_upload_url('/upload')}
    template = JINJA_ENVIRONMENT.get_template('upload.html')
    self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

  def post(self):
    upload_files = self.get_uploads('file')
    book_title = self.request.get('book_title')
    user = users.get_current_user()
    blob_key = upload_files[0].key()
    uploaded_file = blobstore.BlobReader(blob_key)
    book = models.Book(uploaded_by=user, title=book_title,
        blob_key=str(blob_key))
    book.put()
    pipeline = map_reduce.WordCountPipeline(book_title, str(blob_key))
    pipeline.start()
    self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)
    # lines = uploaded_file.read().splitlines()
    # mapping = defaultdict(list)
    # for line in lines:
    #   words = line.split(' ')
    #   for word in words:
    #     if line not in mapping[word]:
    #       mapping[word].append(line)
    # for word, sentences in mapping.iteritems():
    #   sentence_instances = []
    #   for sentence in sentences:
    #     sentence_instances.append(models.Sentence(book=book_title, sentence=sentence))
    #   db_object = models.Word(word=word, sentences=sentence_instances)
    #   db_object.put()
    # self.redirect('/serve/%s' % blob_key)


class DeleteHandler(webapp2.RequestHandler):

  def get(self):
    ndb.delete_multi(models.Word.query().fetch(keys_only=True))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):

  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)


application = webapp2.WSGIApplication([
    ('/serve/([^/]+)?', ServeHandler),
    ('/search', Search),
    ('/upload', UploadHandler),
    ('/admin/delete', DeleteHandler),
    ('/admin', AdminHandler),
    ('/', MainPage),
], debug=True)

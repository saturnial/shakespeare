import cgi
import os
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import jinja2
import webapp2

from models import Word


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
    result = Word.query(Word.word == query)
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
    blob_info = upload_files[0]
    self.redirect('/serve/%s' % blob_info.key())


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)


application = webapp2.WSGIApplication([
    ('/serve/([^/]+)?', ServeHandler),
    ('/search', Search),
    ('/upload', UploadHandler),
    ('/admin', AdminHandler),
    ('/', MainPage),
], debug=True)

import cgi
import os
import urllib

from google.appengine.ext import ndb
from google.appengine.api import users

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


application = webapp2.WSGIApplication([
    ('/search', Search),
    ('/', MainPage),
], debug=True)

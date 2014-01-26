import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

  def get(self):
    template = JINJA_ENVIRONMENT.get_template('index.html')
    template_values = {}
    self.response.write(template.render(template_values))


class Search(webapp2.RequestHandler):

  def get(self):
    query = self.request.get('query')


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

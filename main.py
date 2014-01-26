import cgi
import os
import urllib

from google.appengine.ext import ndb
from google.appengine.api import users

import jinja2
import webapp2

import models


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

  def get(self):
    template_values = {'result': models.Word.query()}
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))


class Search(webapp2.RequestHandler):

  def get(self):
    query = self.request.get('query')
    sentence1 = models.Sentence(book="Waiting For The Barbarians", sentence="Pain is truth; all else is subject to doubt.")
    sentence2 = models.Sentence(book="Heart of Darkness", sentence="Your strength is just an accident owed to the weakness of others.")
    word = models.Word(word=query, sentences=[sentence1, sentence2])
    word.put()
    self.redirect('/')


application = webapp2.WSGIApplication([
    ('/search', Search),
    ('/', MainPage),
], debug=True)

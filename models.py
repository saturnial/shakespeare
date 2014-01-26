from google.appengine.ext import ndb


class Word(ndb.Model):
  word = ndb.StringProperty(required=True)
  sentence = ndb.StringProperty(repeated=True)
  book = ndb.StringProperty(required=True)



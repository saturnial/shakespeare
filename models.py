from google.appengine.ext import ndb


class Sentence(ndb.Model):
  sentence = ndb.StringProperty(required=True)
  book = ndb.StringProperty(required=True)


class Word(ndb.Model):
  word = ndb.StringProperty(required=True)
  sentences = ndb.StructuredProperty(Sentence, repeated=True)



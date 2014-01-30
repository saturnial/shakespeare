from google.appengine.ext import ndb


class Sentence(ndb.Model):
  sentence = ndb.StringProperty(required=True)
  book = ndb.StringProperty(required=True)


class Word(ndb.Model):
  word = ndb.StringProperty(required=True)
  sentences = ndb.StructuredProperty(Sentence, repeated=True)


class Book(ndb.Model):
  uploaded_by = ndb.UserProperty(required=True)
  uploaded_on = ndb.DateTimeProperty(auto_now_add=True)
  title = ndb.StringProperty(required=True)
  blob_key = ndb.StringProperty(required=True)
  wordcount_link = ndb.StringProperty()

from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from mapreduce import context

from google.appengine.ext import ndb

import models

import logging
import re


class WordCountPipeline(base_handler.PipelineBase):

  def run(self, filekey, blobkey):
    logging.debug("filename is %s" % filekey)
    output = yield mapreduce_pipeline.MapreducePipeline(
        "word_count",
        "map_reduce.word_count_map",
        "map_reduce.word_count_reduce",
        "mapreduce.input_readers.BlobstoreLineInputReader",
        "mapreduce.output_writers.FileOutputWriter",
        mapper_params={
            "input_reader": {
                "blob_keys": [blobkey]
            },
        },
        reducer_params={
            "output_writer": {
                "mime_type": "text/plain",
                "output_sharding": "input",
                "filesystem": "blobstore",
                "book_title": filekey,
            },
        },
        shards=16)
    yield StoreOutput(filekey, output)

def split_into_sentences(s):
  """Split text into list of sentences."""
  s = re.sub(r"\s+", " ", s)
  s = re.sub(r"[\\.\\?\\!]", "\n", s)
  return s.split("\n")


def split_into_words(s):
  """Split a sentence into list of words."""
  s = re.sub(r"\W+", " ", s)
  s = re.sub(r"[_0-9]+", " ", s)
  return s.split()

def word_count_map(data):
  """Word count map function."""
  (byte_offset, line_value) = data
  for s in split_into_sentences(line_value):
    for w in split_into_words(s.lower()):
      yield (w, s)


def word_count_reduce(key, values):
  """Word count reduce function."""
  sentences = []
  ctx = context.get()
  title = ctx.mapreduce_spec.mapper.params['output_writer']['book_title']
  for sentence in values:
    sentences.append(models.Sentence(sentence=sentence, book=title))
  word = models.Word(word=key, sentences=sentences)
  word.put()


class StoreOutput(base_handler.PipelineBase):
  """A pipeline to store the result of the MapReduce job in the database.

  Args:
    encoded_key: the DB key corresponding to the metadata of this job
    output: the blobstore location where the output of the job is stored
  """

  def run(self, encoded_key, output):
    book = models.Book.query(models.Book.title == encoded_key).get()
    link = output[0]
    book.wordcount_link = link
    book.put()

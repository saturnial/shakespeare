from mapreduce import base_handler
from mapreduce import mapreduce_pipeline

class WordCountPipeline(base_handler.PipelineBase):

  def run(self, filekey, blobkey):
    logging.debug("filename is %s" % filekey)
    output = yield mapreduce_pipeline.MapreducePipeline(
        "word_count",
        "mapreduce.word_count_map",
        "mapreduce.word_count_reduce",
        "mapreduce.input_readers.BlobstoreZipInputReader",
        "mapreduce.output_writers.FileOutputWriter",
        mapper_params={
            "input_reader": {
                "blob_key": blobkey,
            },
        },
        reducer_params={
            "output_writer": {
                "mime_type": "text/plain",
                "output_sharding": "input",
                "filesystem": "blobstore",
            },
        },
        shards=16)
    yield StoreOutput("WordCount", filekey, output)


def word_count_map(data):
  """Word count map function."""
  (entry, text_fn) = data
  text = text_fn()

  logging.debug("Got %s", entry.filename)
  for s in split_into_sentences(text):
    for w in split_into_words(s.lower()):
      yield (w, "")


def word_count_reduce(key, values):
  """Word count reduce function."""
  yield "%s: %d\n" % (key, len(values))


class StoreOutput(base_handler.PipelineBase):
  """A pipeline to store the result of the MapReduce job in the database.

  Args:
    mr_type: the type of mapreduce job run (e.g., WordCount, Index)
    encoded_key: the DB key corresponding to the metadata of this job
    output: the blobstore location where the output of the job is stored
  """

  def run(self, mr_type, encoded_key, output):
    logging.debug("output is %s" % str(output))
    key = db.Key(encoded=encoded_key)
    m = FileMetadata.get(key)

    if mr_type == "WordCount":
      m.wordcount_link = output[0]
    elif mr_type == "Index":
      m.index_link = output[0]
    elif mr_type == "Phrases":
      m.phrases_link = output[0]

    m.put()

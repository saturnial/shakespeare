from mapreduce import base_handler
from mapreduce import mapreduce_pipeline

class WordCountPipeline(base_handler.PipelineBase):

  def run(self, filekey, blobkey):
    logging.debug("filename is %s" % filekey)
    output = yield mapreduce_pipeline.MapreducePipeline(
        "word_count",
        "main.word_count_map",
        "main.word_count_reduce",
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

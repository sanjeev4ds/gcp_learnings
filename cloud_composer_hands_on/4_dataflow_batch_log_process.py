import argparse
import logging
import apache_beam as beam
import re
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.transforms.sql import SqlTransform
from apache_beam.options.pipeline_options import PipelineOptions
import json
import ast

#setting up the apache beam pipeline options
beam_options = PipelineOptions(
    save_main_session = True,
    runner = "DataflowRunner",
    project="sanjeevyoutubefirstapi",
    temp_location="cloud_composer_learning/temp_location",
    region= "asia-south2"
)

class ParseJSON(beam.DoFn):
    def process(self, element):
        try:
            dict_line = json.load(element)
            sub_str = dict_line['protoPayLoad']['methodName']
            if 'google.cloud' in sub_str:
                sub_str = sub_str.split('.')[4] + '.' + sub_str.split('.')[5]
            st = '{' + "'user':'" + dict_line['protoPayLoad']['authenticationInfo']['principleEmail'] + "', 'job_type':'" + sub_str.lower().rstrip('job') + "'}"
            return st
        except:
            logging.info("some error occured")

def run():
    with beam.Pipeline(options= beam.options) as p:
        result = (
            p | 'read from GCS' >> ReadFromText('gs://cloud_composer_learning/sample_json.json')
            | 'Parse logs to string representation of dict' >> beam.ParDo(ParseJSON())
            | 'convert string to dict' >> beam.Map(lambda  x: json.loads(x))

        )

        write_to_gcs =  (
            result | 'get job type tuple' >> beam.Map(lambda x: ( x['job_type'] + ',' + x['info_type'], 1))
            | 'combine per key and sum' >> beam.CombinePerKey(sum)
            | 'format to JSON' >> beam.Map( lambda x : "{'job_type':'")
        )


import io
import sys

import boto3

from collage.fasta import parse_fasta
from collage.generator import beam_generator
from collage.model import initialize_collage_model

# TODO(auberon): Make these configurable
MODEL_FILE_PATH = "/models/Ecoli.pt"
USE_GPU = True
BEAM_SIZE = 100

def download_predict_upload(bucket, object_name, input_prefix, output_prefix, model_file_path, beam_size, use_gpu):
    print(f"{bucket=} {object_name=} {input_prefix=} {output_prefix=}")
    s3_client = boto3.client('s3')
    input_key = input_prefix+object_name
    print(f"{input_key=}")
    resp = s3_client.get_object(
                                Bucket=bucket,
                                Key=input_key,
                            )
    
    input_stream = resp["Body"]
    with io.TextIOWrapper(input_stream, encoding="utf-8") as input_fasta:
        seq_dict = parse_fasta(input_fasta, True)

    print(seq_dict)
    # Currently only makes predictions for first protein in FASTA
    # TODO(auberon): Allow multi-protein predictions?
    first_protein = list(seq_dict.values())[0]
    model = initialize_collage_model(model_file_path, use_gpu)
    predictions = beam_generator(model, first_protein, max_seqs=beam_size)

    output_object = str(predictions)
    output_key = output_prefix+object_name
    print(f"{output_key=}")
    s3_client.put_object(
        Body=output_object,
        Bucket=bucket,
        Key=output_key,
    )
    print("Predictions uploaded")

def main(args):
    print(f"The arguments I got were: {args}")
    # TODO(auberon): Make more robust with argparse?
    if len(args) != 4:
        raise TypeError("Expected 4 arguments. Got: ", args)
    download_predict_upload(*args, MODEL_FILE_PATH, BEAM_SIZE, USE_GPU)

if __name__ == "__main__":
    main(sys.argv[1:])

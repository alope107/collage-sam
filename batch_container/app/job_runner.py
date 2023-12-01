import argparse
import io
import sys

import boto3

from collage.fasta import parse_fasta, to_fasta
from collage.generator import beam_generator, seq_scores_to_seq_dict
from collage.model import initialize_collage_model


def download_predict_upload(bucket, object_name, input_prefix, output_prefix, model_path, beam_size, use_cpu):
    print(f"{bucket=} {object_name=} {input_prefix=} {output_prefix=}")
    s3_client = boto3.client('s3')
    input_key = input_prefix + object_name
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
    model = initialize_collage_model(model_path, not use_cpu)
    negLLs = beam_generator(model, first_protein, max_seqs=beam_size)

    seq_dict = seq_scores_to_seq_dict(negLLs)
    output_fasta = to_fasta(seq_dict)
    output_key = output_prefix + object_name
    print(f"{output_key=}")
    s3_client.put_object(
        Body=output_fasta,
        Bucket=bucket,
        Key=output_key,
    )
    print("Predictions uploaded")


def parse_args(args: list):
    '''
    Read in arguments
    '''

    parser = argparse.ArgumentParser(usage='job_runner.py [optional arguments] bucket_name object_name input_prefix output_prefix',
                                     description='Downloads an input FASTA from s3, runs a collage prediction on it, and uploads the result.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('bucket',
                        type=str,
                        help='Name of the s3 bucket to download/upload from/to')
    parser.add_argument('object_name',
                        type=str,
                        help='Name of the input object in s3 WITHOUT any prefix')
    parser.add_argument('input_prefix',
                        type=str,
                        help='Prefix of the input object in s3')
    parser.add_argument('output_prefix',
                        type=str,
                        help='Prefix of where to store the output object in s3')
    parser.add_argument('--model_path',
                        type=str,
                        default="/models/Ecoli.pt",
                        help='Path to the pretrained model file on the local machine')
    parser.add_argument('--beam_size',
                        type=int,
                        default=100,
                        help='Number of beams to use in beam search')
    parser.add_argument('--use_cpu',
                        action='store_true',
                        help='Use CPU for CoLLAGE training instead of GPU')

    return parser.parse_args(args)


def main(args):
    print(f"The arguments I got were: {args}")
    download_predict_upload(**vars(parse_args(args)))


if __name__ == "__main__":
    main(sys.argv[1:])

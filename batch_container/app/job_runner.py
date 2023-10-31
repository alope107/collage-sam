import sys
import boto3

def upload_download(bucket, object_name, input_prefix, output_prefix):
    print(f"{bucket=} {object_name=} {input_prefix=} {output_prefix=}")
    s3_client = boto3.client('s3')
    input_key = input_prefix+object_name
    print(f"{input_key=}")
    resp = s3_client.get_object(
                                Bucket=bucket,
                                Key=input_key,
                            )
    input_object = resp["Body"].read()
    print(f"Here's the object: {input_object}")
    output_key = output_prefix+object_name
    print(f"{output_key=}")
    s3_client.put_object(
        Body=input_object,
        Bucket=bucket,
        Key=output_key,
    )
    print("All done!")

def main(args):
    print(f"The arguments I got were: {args}")
    # TODO(auberon): Make more robust with argparse?
    if len(args) != 4:
        raise TypeError("Expected 4 arguments. Got: ", args)
    upload_download(*args)

if __name__ == "__main__":
    main(sys.argv[1:])

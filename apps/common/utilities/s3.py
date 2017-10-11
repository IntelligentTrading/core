import boto
import typing


def get_readable_stream(s3_key):
    s3_key.open_read()
    return s3_key.read()


def get_s3_key(bucket_name: str, key_name: str):
    # returns boto.s3.key
    return boto.connect_s3().get_bucket(bucket_name).get_key(key_name)


def get_s3_readable_key(bucket_name: str, key_name: str):
    return get_readable_stream(get_s3_key(bucket_name, key_name))


def create_public_url(s3_key) -> str:
    s3_key.set_acl('public-read')
    return s3_key.generate_url(expires_in=0, query_auth=False)

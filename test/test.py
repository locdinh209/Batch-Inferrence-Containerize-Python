import boto3
import pandas as pd
import io
from io import StringIO

s3 = boto3.client('s3')
bucket = 'stb-ml-cross-sale'
key = 'inputs/sample1.csv'
obj = s3.get_object(Bucket=bucket, Key=key)

data = pd.read_csv(io.BytesIO(obj['Body'].read()), sep=';', encoding='utf-8')
print (data.head(10))



csv_buffer = StringIO()
data.to_csv(csv_buffer, sep=';', encoding='utf-8', index=False)
# s3_resource = boto3.resource('s3')
s3.Object(bucket, 'outputs/sample1_output.csv').put(Body=csv_buffer.getvalue())
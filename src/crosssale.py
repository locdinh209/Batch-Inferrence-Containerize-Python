import sys
import io
import tensorflow
from tensorflow import keras
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from sklearn.preprocessing import StandardScaler
import time
import boto3
from io import StringIO

# Start run job
start_time = time.time()

#Constants
BUCKET = str(sys.argv[1])
INPUT_NAME = str(sys.argv[2])
MODEL_NAME = str(sys.argv[3])
OUTPUT_NAME = str(sys.argv[4])
BATCH_SIZE = 2048*5

print(f'Bucket: {BUCKET}')
print(INPUT_NAME)
print(f'Output path: {OUTPUT_NAME}')

#Credential Key:
ACCESS_KEY = 'AKIAUPZ52XK23E2NK3VG'
SECRET_KEY = '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'
REGION = 'ap-southeast-1'

s3 = boto3.client('s3',region_name=REGION,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

#Import Data
input_object = s3.get_object(Bucket=BUCKET, Key=INPUT_NAME)
data = pd.read_csv(io.BytesIO(input_object['Body'].read()), sep=';', encoding='utf-8')
print ("Data loaded")

#Create features 2 model
features = data[['MARIAL_STATUS', 'ACCOUNT_TYPE', 'EMAIL', 'LOAN_ACCOUNT', 'CURRENT_ACCOUNT', 'DEPOSIT_ACCOUNT', 'CLOSE_DT', 'AVG_LAST3MONTH',
                     'S_T24_DEBIT', 'S_T24_CREDIT', 'S_T24_DEBIT_TRANSACTION', 'INCREASE_3_MONTH', 'CONSECUTIVE_3_MONTH', 'AGE_GROUP', 'GENDER', 'TC_INDEX']]

eps=0.001 # 0 => 0.1¢
features['AVG_LAST3MONTH'] = np.log(features['AVG_LAST3MONTH']+eps)
features['S_T24_DEBIT'] = np.log(features['S_T24_DEBIT']+eps)
features['S_T24_CREDIT'] = np.log(features['S_T24_CREDIT']+eps)

scaler = StandardScaler()
np_features = np.array(features)
np_features = scaler.fit_transform(np_features)
np_features = np.clip(np_features, -5, 5)

print('Features shape:', np_features.shape)

#Load model and classify
model = keras.models.load_model(MODEL_NAME)
predict_results = model.predict(np_features, batch_size=BATCH_SIZE)

#Add predict class Target column
data['TARGET_PREDICT'] = np.rint(predict_results).astype('uint8')

# Sync result to S3 output folder
csv_buffer = StringIO()
data.to_csv(csv_buffer, sep=';', encoding='utf-8', index=False)
s3_resource = boto3.resource('s3',region_name=REGION,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3_resource.Object(BUCKET, OUTPUT_NAME).put(Body=csv_buffer.getvalue())

# End job
print("--- %s seconds ---" % (time.time() - start_time))
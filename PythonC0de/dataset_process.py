import json
import os
import uuid

import boto3
import pandas as pd

os.environ['docUrl'] = "http://doc-bank-bot-k4byqmxrpqcw2q4yevtz6aenoy.us-east-1.cloudsearch.amazonaws.com"
os.environ['region'] = "us-east-1"
client = boto3.client('cloudsearchdomain', endpoint_url=os.environ['docUrl'], region_name=os.environ['region'])

dataset = pd.read_csv("./BankFAQs.csv")

data = []
print("iterating rows")
for i, row in dataset.iterrows():
    data.append({
        "type": "add",
        "id": str(uuid.uuid4()),
        "fields": {
            "questions": row['Question'],
            "answer": row['Answer'],
            "id": str(uuid.uuid4()),
        }
    })
print(len(data))
print("cloudsearch api logic start")
doclist = json.dumps(data)
print("calling cloudsearch api")
response = client.upload_documents(documents=doclist, contentType="application/json")
print(response)
print("cloudsearch api logic end")

from botocore.exceptions import ClientError
from apify_client import ApifyClient

from datetime import datetime
import requests
import logging
import boto3
import json
import os



def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name="us-east-1")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        acl = s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
    except ClientError as e:
        logging.error(e)
        return False
    return True



now = datetime.now()
timestamp = datetime.timestamp(now)

with open("/home/scrapeops/ex-politica-scrape/Apify/Results/Facebook/Facebook_Posts_Urls.json", "r") as f:
    input = json.load(f)

input = [{"url": url} for url in input]

client = ApifyClient(os.environ['FACEBOOK_APIFY_KEY'])

run_input = {
    "includeNestedComments": False,
    "resultsLimit": 20,
    "startUrls": input
}

run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)

json_array = []
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    json_data = json.dumps(item, ensure_ascii=False)
    json_array.append(json.loads(json_data))
    
    json_str = json.dumps(json_array, indent=4, ensure_ascii=False)
    
with open("/home/scrapeops/ex-politica-scrape/Apify/Results/Facebook/Facebook_Comments.json", "w") as f:
    f.write(json_str)
    
upload_file(f"/home/scrapeops/ex-politica-scrape/Apify/Results/Facebook/Facebook_Comments.json", "axioon", f"Apify/Facebook/Comments/Facebook_Comments_{timestamp}.json")

file_name = requests.post(f"{os.environ['API_IP']}/webhook/facebook/comments", json={"records": f"Apify/Facebook/Comments/Facebook_Comments_{timestamp}.json"})

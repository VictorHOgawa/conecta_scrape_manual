from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError
from apify_client import ApifyClient
from dotenv import load_dotenv
import requests
import logging
import boto3
import json
import os

load_dotenv()

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name="us-east-1")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        acl = s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
    except ClientError as e:
        logging.error(e)
        return False
    return True

load_dotenv()

now = datetime.now()
timestamp = datetime.timestamp(now)
yesterday = date.today() - timedelta(days=1)

# input = requests.get(f"{os.getenv('API_IP')}/scrape/instagram")

# input = input.json()
input = {
  "instagram": [
    {
      "instagram": "alessandroobarcelos",
      "id": "56005c1b-daa4-4450-8065-66ba871bf83e"
    }
  ]
}

input = input["instagram"]

instagram_names = [item["instagram"] for item in input]

instagram_ids = [item["id"] for item in input]

# client = ApifyClient(os.getenv("APIFY_KEY"))

client = ApifyClient("apify_api_DBrvEynIe09EOVyxrNzDeq3k7YFB7V0YYWHc")

run_input = {
    "directUrls": [f"https://www.instagram.com/{instagram_name}/" for instagram_name in instagram_names],
    "resultsType": "posts",
    "resultsLimit": 100,
    "addParentData": False,
    "searchType": "hashtag",
    "searchLimit": 1,
    # "untilDate": yesterday
}

run = client.actor("shu8hvrXbJbY3Eb9W").call(run_input=run_input)

json_array = []
posts_set = set()
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    json_data = json.dumps(item, ensure_ascii=False)
    json_array.append(json.loads(json_data))
    
    for item in json_array:
        if item["url"]:
            posts_set.add(item["url"])
        for instagram_name, instagram_id in zip(instagram_names, instagram_ids):
            if item["ownerUsername"].lower() == instagram_name.lower():
                item["instagram_id"] = instagram_id
                
    json_str = json.dumps(json_array, indent=4, ensure_ascii=False)
    posts_array = list(posts_set)
    posts_str = json.dumps(posts_array, indent=4, ensure_ascii=False)

with open("Apify/Results/Instagram/Instagram_Posts.json", "w") as f:
    f.write(json_str)
    
with open("Apify/Results/Instagram/Instagram_Posts_Urls.json", "w") as f:
    f.write(posts_str)
    
upload_file("Apify/Results/Instagram/Instagram_Posts.json", "axioon", f"Apify/Instagram/Posts/Instagram_Posts_{timestamp}.json")

file_name = requests.post(f"{os.getenv('API_IP')}/webhook/instagram/posts", json={"records": f"Apify/Instagram/Posts/Instagram_Posts_{timestamp}.json"})

from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError
from apify_client import ApifyClient
import requests
import logging
import boto3
import json
import os

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 "bucket"

    :param file_name: File to upload
    :param "bucket": "bucket" to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id="AKIA6MOM3OQOF7HA5AOG", aws_secret_access_key="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")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        acl = s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
    except ClientError as e:
        logging.error(e)
        return False
    return True

now = datetime.now()
timestamp = datetime.timestamp(now)

input = requests.get("http://18.231.150.215/scrape/tiktok")

input = input.json()

input = input["tiktok"]

tiktok_names = [item["tiktok"] for item in input]
# tiktok_names = ["mauromendesoficial", "lulaoficial", "prefeitorobertodorner"]

tiktok_ids = [item["id"] for item in input]
# tiktok_ids = ["12", "34", "56"]

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_cJsB3f5hwtrpVwa37WSq4MA1yZuogt49Ewq1")

# Prepare the Actor input
run_input = {
    "disableCheerioBoost": False,
    "disableEnrichAuthorStats": False,
    "profiles": [f"{tiktok_name}" for tiktok_name in tiktok_names],
    "shouldDownloadCovers": False,
    "shouldDownloadSlideshowImages": False,
    "shouldDownloadVideos": False
}
# Run the Actor and wait for it to finish
run = client.actor("OtzYfK1ndEGdwWFKQ").call(run_input=run_input)

json_array = []
posts_set = set()
# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    json_data = json.dumps(item, ensure_ascii=False)
    json_array.append(json.loads(json_data))
    
    for item in json_array:
        if item["webVideoUrl"]:
            posts_set.add(item["webVideoUrl"])
        for tiktok_name, tiktok_id in zip(tiktok_names, tiktok_ids):
            if tiktok_name.lower() in item["webVideoUrl"].lower():
                item["tiktok_id"] = tiktok_id

    json_str = json.dumps(json_array, ensure_ascii=False, indent=4)
    posts_array = list(posts_set)
    posts_str = json.dumps(posts_array, ensure_ascii=False, indent=4)

with open("/home/scrapeops/Axioon/Apify/Results/TikTok/TikTok_Posts.json", "w") as f:
    f.write(json_str)

with open("/home/scrapeops/Axioon/Apify/Results/TikTok/TikTok_Posts_Urls.json", "w") as f:
    f.write(posts_str)
    
upload_file("/home/scrapeops/Axioon/Apify/Results/TikTok/TikTok_Posts.json", "nightapp", f"Apify/TikTok/TikTok_Posts_{timestamp}.json")
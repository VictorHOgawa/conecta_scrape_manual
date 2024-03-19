# from datetime import date, datetime, timedelta
# from botocore.exceptions import ClientError
# from ..items import articleItem
# from scrapy.http import Request

# import requests
# import logging
# import locale
# import scrapy
# import boto3
# import json
# import os

# def upload_file(file_name, bucket, object_name=None):
#     """Upload a file to an S3 "bucket"

#     :param file_name: File to upload
#     :param "bucket": "bucket" to upload to
#     :param object_name: S3 object name. If not specified then file_name is used
#     :return: True if file was uploaded, else False
#     """

#     # If S3 object_name was not specified, use file_name
#     if object_name is None:
#         object_name = os.path.basename(file_name)

#     # Upload the file
#     s3_client = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
#     try:
#         response = s3_client.upload_file(file_name, bucket, object_name)
#         acl = s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True

# locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# now = datetime.now()
# timestamp = datetime.timestamp(now)

# today = date.today().strftime("%d/%m/%Y")
# today = datetime.strptime(today, "%d/%m/%Y")

# search_limit = date.today() - timedelta(days=60)
# search_limit = datetime.strptime(search_limit.strftime("%d/%m/%Y"), "%d/%m/%Y")

# site_id = "dce5b2dd-194b-4a6b-b06a-354b217c2510"

# request = requests.get(f"{os.environ['API_IP']}/scrape/news/{site_id}")
# search_words = request.json()

# with open("Spiders/CSS_Selectors/PE/Pe_PoliticaPernambucana.json") as f:
#     search_terms = json.load(f)

# main_url = ""

# class PoliticaPernambucanaSpider(scrapy.Spider):
#     name = "Init_Pe_PoliticaPernambucana"
#     start_urls = ["https://blog.politicapernambucana.com.br/"]
    
#     def parse(self, response):
#         for article in response.css(search_terms['article']):
#             link = article.css(search_terms['link']).get()
#             print("link: ", link)
#             yield Request(link, callback=self.parse_article, priority=1)
#         next_page = response.css(search_terms['next_page']).get()
#         print("next_page: ", next_page)
#         if next_page is not None:
#             yield response.follow(next_page, callback=self.parse)
#         else:
#             print("NÃO TEM NEXT BUTTON")
            
#     def parse_article(self, response):
#         updated = response.css(search_terms['updated']).get()
#         updated = updated.replace(" de ", "/")
#         updated = datetime.strptime(updated, "%d/%B/%Y").strftime("%d/%m/%Y")
#         updated = datetime.strptime(updated, "%d/%m/%Y")
#         print("updated: ", updated)
#         title = response.css(search_terms['title']).get()
#         print("title: ", title)
#         content = response.css(search_terms['content']).getall()
#         print("content: ",content)
#         if search_limit <= updated <= today:
#             found_names = []
#             for paragraph in content:
#                 for user in search_words['users']:
#                     if user['social_name'] in paragraph:
#                         found_names.append({'name': user['social_name'], 'id': user['id']})
#                         item = articleItem(
#                             updated=updated,
#                             title=title,
#                             content=content,
#                             link=response.url,
#                             users=found_names,
#                             site_id=site_id
#                         )
#                         yield item
#                         if item is not None:
#                             article_dict = {
#                                "updated": item['updated'].strftime("%d/%m/%Y"),
#                                "title": item['title'],
#                                "content": item['content'],
#                                "link": item['link'],
#                                "users": item['users'],
#                                "site_id": item['site_id']
#                             }
#                             file_path = f"Spiders/Results/{self.name}_{timestamp}.json"
#                             if not os.path.isfile(file_path):
#                                 with open(file_path, "w") as f:
#                                     json.dump([], f)

#                             with open(file_path, "r") as f:
#                                 data = json.load(f)

#                             data.append(article_dict)

#                             with open(file_path, "w") as f:
#                                 json.dump(data, f, ensure_ascii=False)
                                
#                             upload_file(f"Spiders/Results/{self.name}_{timestamp}.json", "axioon", f"News/PE/{self.name}_{timestamp}.json")
#                             file_name = requests.post(f"{os.environ['API_IP']}/webhook/news", json={"records": f"News/PE/{self.name}_{timestamp}.json"})
                     
#         else:
#             raise scrapy.exceptions.CloseSpider
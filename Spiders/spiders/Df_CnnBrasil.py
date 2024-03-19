# from datetime import date, datetime, timedelta
# from botocore.exceptions import ClientError
# from ..items import articleItem
# from scrapy.http import Request
# from bs4 import BeautifulSoup

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

# request = requests.get(f"{os.environ['API_IP']}/scrape/news/2ca836a5-1996-4c81-a76f-921b44265276")
# search_words = request.json() 

# 
# with open("Spiders/CSS_Selectors/Df/Df_CnnBrasil.json") as f:
#     search_terms = json.load(f)

# main_url = "https://www.cnnbrasil.com.br/tudo-sobre/ibaneis-rocha/"
         
# class CnnBrasilSpider(scrapy.Spider):
#     name = "Df_CnnBrasil"
#     start_urls = ["https://www.cnnbrasil.com.br/tudo-sobre/ibaneis-rocha/"]
    
#     def parse(self, response):
#         for article in response.css(search_terms['article']):
#             link = article.css(search_terms['link']).get()
#             print("link: ", link)
#             yield Request(link, callback=self.parse_article, priority=1)
#         next_page = response.css(search_terms['next_page'])[-1].get()
#         print("next_page: ", next_page)
#         if next_page is not None:
#             yield response.follow(next_page, callback=self.parse)
#         else:
#             print("NÃO TEM NEXT BUTTON")
            
#     def parse_article(self, response):
#         updated = response.css(search_terms['updated']).get()
#         updated = updated.split(" ")[1]
#         updated = updated.strip()
#         updated = datetime.strptime(updated, "%d/%m/%Y").strftime("%d/%m/%Y")
#         updated = datetime.strptime(updated, "%d/%m/%Y")
#         print("updated: ", updated)
#         title = response.css(search_terms['title']).get()
#         print("title: ", title)
#         content = response.css(search_terms['content']).getall()
#         content = BeautifulSoup(" ".join(content), "html.parser").text
#         content = content.replace("\n", " ")        
#         print("content: ", content)
#         found_names = []
#         found_names.append({'name': search_words['users'][0]['social_name'], 'id': search_words['users'][0]['id']})
#         item = articleItem(
#             updated=updated,
#             title=title,
#             content=content,
#             link=response.url,
#             users=found_names
#         )
#         yield item
#         if item is not None:
#             article_dict = {
#                 "updated": item['updated'].strftime("%d/%m/%Y"),
#                 "title": item['title'],
#                 "content": [item['content']],
#                 "link": item['link'],
#                 "users": item['users']
#             }
#             file_path = f"Spiders/Results/{self.name}_{timestamp}.json"
#             if not os.path.isfile(file_path):
#                 with open(file_path, "w") as f:
#                     json.dump([], f)

#             with open(file_path, "r") as f:
#                 data = json.load(f)

#             data.append(article_dict)

#             with open(file_path, "w") as f:
#                 json.dump(data, f, ensure_ascii=False)
                
                
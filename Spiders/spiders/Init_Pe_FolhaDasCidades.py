from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError
from ..items import articleItem
from scrapy.http import Request
from bs4 import BeautifulSoup
import requests
import logging
import locale
import scrapy
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
    s3_client = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        acl = s3_client.put_object_acl(Bucket=bucket, Key=object_name, ACL='public-read')
    except ClientError as e:
        logging.error(e)
        return False
    return True

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

now = datetime.now()
timestamp = datetime.timestamp(now)

today = date.today().strftime("%d/%m/%Y")
today = datetime.strptime(today, "%d/%m/%Y")

search_limit = date.today() - timedelta(days=60)
search_limit = datetime.strptime(search_limit.strftime("%d/%m/%Y"), "%d/%m/%Y")

request = requests.get(f"{os.environ['API_IP']}/scrape/news/12d7e023-794d-49e1-96a8-5a2bbb7f57e6")
search_words = request.json()

with open("/home/scrapeops/ex-politica-scrape/Spiders/CSS_Selectors/PE/Pe_FolhaDasCidades.json") as f:
    search_terms = json.load(f)

main_url = "https://www.afolhadascidades.com.br/"

class FolhaDasCidadesSpider(scrapy.Spider):
    name = "Init_Pe_FolhaDasCidades"
    allowed_domains = ["afolhadascidades.com.br"]
    start_urls = ["https://www.afolhadascidades.com.br/"]
    INCREMENT = 1
    
    def parse(self, response):
        for article in response.css(search_terms['article']):
            link = article.css(search_terms['link']).get()
            yield Request(link, callback=self.parse_article, priority=1)
        self.INCREMENT += 1
        next_page = f"https://www.blogdofabiocardoso.com/page/{self.INCREMENT}"
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        else:
            print("NÃO TEM NEXT BUTTON")
            
    def parse_article(self, response):
        updated = response.css(search_terms['updated']).get()
        updated = updated.split(", ")[1]
        updated = updated.replace(" de ", "/")
        updated = updated.strip()
        updated = datetime.strptime(updated, "%d/%B/%Y").strftime("%d/%m/%Y")
        updated = datetime.strptime(updated, "%d/%m/%Y")
        title = response.css(search_terms['title']).get()
        content = response.css(search_terms['content']).getall()
        content = BeautifulSoup(" ".join(content), "html.parser").text
        content = content.replace("\n", " ")
        if search_limit <= updated <= today:
            found_names = []
            for paragraph in content:
                for user in search_words['users']:
                    if user['social_name'] in paragraph:
                        found_names.append({'name': user['social_name'], 'id': user['id']})
                        item = articleItem(
                            updated=updated,
                            title=title,
                            content=content,
                            link=response.url,
                            users=found_names
                        )
                        yield item
                        if item is not None:
                            article_dict = {
                               "updated": item['updated'].strftime("%d/%m/%Y"),
                               "title": item['title'],
                               "content": [item['content']],
                               "link": item['link'],
                               "users": item['users']
                            }
                            file_path = f"Spiders/Results/{self.name}_{timestamp}.json"
                            if not os.path.isfile(file_path):
                                with open(file_path, "w") as f:
                                    json.dump([], f)

                            with open(file_path, "r") as f:
                                data = json.load(f)

                            data.append(article_dict)

                            with open(file_path, "w") as f:
                                json.dump(data, f, ensure_ascii=False)
                                
                            upload_file(f"/home/scrapeops/ex-politica-scrape/Spiders/Results/{self.name}_{timestamp}.json", "axioon", f"News/STATE/{self.name}_{timestamp}.json")
                            file_name = requests.post(f"{os.environ['API_IP']}/webhook/news", json={"records": f"News/STATE/{self.name}_{timestamp}.json"})
                     
        else:
            raise scrapy.exceptions.CloseSpider
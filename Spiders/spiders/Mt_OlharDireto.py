from datetime import date, datetime, timedelta
from scrapy.item import Item, Field
from urllib.parse import urljoin
from scrapy.http import Request
import scrapy
import json

class articleItem(Item):
    title = Field()
    updated = Field()
    content = Field()
    link = Field()
    users = Field()

now = datetime.now()
timestamp = datetime.timestamp(now)

today = date.today().strftime("%d/%m/%Y")
today = datetime.strptime(today, "%d/%m/%Y")

search_limit = date.today() - timedelta(days=1)
search_limit = datetime.strptime(search_limit.strftime("%d/%m/%Y"), "%d/%m/%Y")

with open("/home/scrapeops/Axioon/Spiders/CSS_Selectors/MT/Mt_OlharDireto.json") as f:
    search_terms = json.load(f)
    
search_words = {'users': [{'id': 'c57d379e-42d4-4878-89be-f2e7b4d61590', 'social_name': 'Roberto Dorner'}, {'id': '3023f094-6095-448a-96e3-446f0b9f46f2', 'social_name': 'Mauro Mendes'}, {'id': '2b9955f1-0991-4aed-ad78-ea40ee3ce00a', 'social_name': 'Emanuel Pinheiro'}]}

main_url = "https://www.olhardireto.com.br/noticias/"

class MtOlhardiretoSpider(scrapy.Spider):
    name = "Mt_OlharDireto"
    allowed_domains = ["olhardireto.com.br"]
    start_urls = ["https://www.olhardireto.com.br/noticias/index.asp?id=33&editoria=politica-mt&pagina=1"]
    custom_settings = {
        "FEEDS": {
            f"s3://nightapp/News/MT/{name}_{timestamp}.json": {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "indent": 4
            }
        }
    }
    
    def parse(self, response):
        for article in response.css(search_terms['article']):
            link = article.css(search_terms['link']).get()
            link = urljoin(main_url, link)
            yield Request(link, callback=self.parse_article, priority=1)
        next_page = response.css(search_terms['next_page'])[-1].get()
        next_page = urljoin(main_url, next_page)
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
        else:
            print("NÃO TEM NEXT BUTTON")
    
    def parse_article(self, response):
        updated = response.css(search_terms['updated']).get()
        updated = updated.split('-')
        updated = updated[0]
        updated = updated.strip()
        updated = datetime.strptime(updated, "%d %b %Y").strftime("%d/%m/%Y")
        updated = datetime.strptime(updated, "%d/%m/%Y")
        title = response.css(search_terms['title']).get()
        content = response.css(search_terms['content']).getall()
        cleaned_list = [line.replace('\r\n', '').strip() for line in content if line.strip()]
        if search_limit <= updated <= today:
            # found_names = []
            # for paragraph in content:
            #     for user in search_words['users']:
            #         if user['social_name'] in paragraph:
            #             found_names.append({'name': user['social_name'], 'id': user['id']})
            #             item = articleItem(
            #                 updated=updated,
            #                 title=title,
            #                 content=cleaned_list,
            #                 link=response.url,
            #                 users=found_names
            #             )
            #             yield item
            item = articleItem(
                updated=updated,
                title=title,
                content=cleaned_list,
                link=response.url,
                # users=found_names
            )
            yield item
        else:
            raise scrapy.exceptions.CloseSpider
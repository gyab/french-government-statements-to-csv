import scrapy
from datetime import datetime

class ViePubliqueDiscours(scrapy.Spider):
    name = 'speeches'

    start_urls = ['https://www.vie-publique.fr/discours']

    def parse(self, response):
        statements = {
            'links': response.css('.teaserSimple--title a'),
            'dates': response.css('time::attr(datetime)').getall()
        }
        statements_links = []
        for i, statement_date in enumerate(statements['dates']):
            if datetime.strptime(statement_date, "%Y-%m-%dT%H:%M:%SZ").date() == datetime.now().date():
                statements_links.append(statements['links'][i])
        yield from response.follow_all(statements_links, self.parse_speech)

        if datetime.strptime(response.css('time::attr(datetime)').getall()[-1], "%Y-%m-%dT%H:%M:%SZ").date() == datetime.now().date():
            pagination_links = response.css('li.pager__item a')
            yield from response.follow_all(pagination_links, self.parse)

    def parse_speech(self, response):
        yield {
            'title': response.css('h1::text').get().strip(),
            'date': response.css('time::attr(datetime)').get(),
            'text': response.css('.field--name-field-texte-integral p').get(),
            'tags': response.css("div.tagsBox a::text").getall(),
            'topics': [x.strip() for x in response.css("div.thematicBox a::text").getall()],
            'speakers': response.css("ul.line-intervenant a::text").getall()
        }

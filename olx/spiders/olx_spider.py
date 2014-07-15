__author__ = 'rahul'

from scrapy.spider import Spider
from scrapy.selector import Selector

from scrapy.http import Request

from olx.items import olxItem

from re import search, sub, MULTILINE, DOTALL
from sets import Set

from datetime import datetime, timedelta
from olx.database.persist import get_date, get_items_from
from olx.utils import date_today


class OlxSpider(Spider):
    name = "olx"
    allowed_domains = ["olx.in"]
    start_urls = [
        "http://newdelhi.olx.in/computers-laptops-cat-835"
    ]
    parsed_date = date_today() - timedelta(1)
    parsed_url_list = None

    def __init__(self, category=None, *args, **kwargs):
        super(OlxSpider, self).__init__(*args, **kwargs)
        d = get_date()
        if d:
            self.parsed_date = d

        self.parsed_url_list = Set(get_items_from(self.parsed_date))

    def extract_page_list_urls(self, selector):
        item_list=selector.css('div#itemListContent .adListDetails')
        for item in item_list:
            date=self.get_list_page_date(item.css('.fourth-column-container ::text').extract())
            print("Rahul" + str(date))
            url=item.css('.second-column-container a').xpath("@href").extract()
            print("Rahul" + str(url))
            yield (url[0], date)

    def get_time(self, date_string):
        if 'Today' in date_string:
            return date_today()
        elif 'Yesterday' in date_string:
            return date_today() - timedelta(1)

        return datetime.strptime(date_string,'%d/%m/%Y').date()

    def get_list_page_date(self, date_string_list):
        date_string = ' \n '.join(date_string_list)
        if 'Today' in date_string:
            return date_today()
        elif 'Yesterday' in date_string:
            return date_today() - timedelta(1)
        else:
            date=search(r"[^0-9]*([0-9]+\s[a-zA-Z]+)", "\n12 June", flags=DOTALL)
            if date:
                date_without_year = datetime.strptime(date.group(1), '%d %b').date()
                return date_without_year.replace(year=self.get_year(date_without_year))
            else:
                raise ValueError("Did not find the date")

    def get_year(self, date):
        today = date_today()
        date_with_this_year = date.replace(year=today.year)
        if date_with_this_year > today:
            return today.year - 1
        return today.year

    def extract_item_detail(self, selector, path):
        item = olxItem()

        item['url'] = path

        title = selector.css('div#item-title-top::text').extract()
        if title:
            item['title'] = title[0].strip()
        else:
            item['title'] = ''

        phone = selector.css('li.phone ::text').re(r'[0-9\+]+')
        if phone:
            item['phone'] = int(phone[0].replace('+', ''))
        else:
            item['phone'] = 0

        name = selector.css('.name ::text').re(r"[^ \n]+")
        if name:
            item['name'] = name[0]
        else:
            item['name'] = ''

        price = selector.css('div.price ::text').re(r'[0-9][0-9,]+')
        if price:
            item['price'] = int(price[0].replace(',', ''))
        else:
            item['price'] = 0

        time = selector.css('.time-info ::text').extract()
        if time:
            item['time'] = self.get_time(time[0])
        else:
            item['time'] = date_today()

        types = selector.css('#description-text .optionals ::text').re('^(?!Type).+$')
        if types:
            item['types'] = types
        else:
            item['types'] = []

        image = selector.css('#big-viewer a').xpath("@href").extract()
        image = map(unicode.strip, image)
        if image:
            item['image'] = image
        else:
            item['image'] = []

        desc = selector.css('#description-text ::text').extract()
        desc = ''.join(desc)
        desc = sub(r"When you call.*OLX.in", '', desc)
        desc = sub(r"Type:$\n.*$", "", desc, flags=MULTILINE)
        desc = sub(r' +', ' ', desc)
        desc = sub(r'\n+','\n', desc)
        desc = sub(r"(^\n+|\n+$)", "", desc)

        if desc:
            item['desc'] = desc
        else:
            item['desc'] = ''

        return item


    def parse(self, response):
        sel = Selector(response)
        done = False
        for url, date in self.extract_page_list_urls(sel):
            if date < self.parsed_date:
                done = True
            path = url.split('/')[-1]
            if path not in self.parsed_url_list and date >= self.parsed_date:
                yield Request(url, callback=self.parse_item, dont_filter=True, meta={'url': url})

        next = sel.css('a.next-page-wrapper').xpath("@href").extract()
        if next and not done:
            yield self.make_requests_from_url(next[0])

    def parse_item(self, response):
        sel = Selector(response)
        path = response.meta['url'].split('/')[-1]
        return self.extract_item_detail(sel, path)






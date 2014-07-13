# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class olxItem(Item):
    # define the fields for your item here like:
    url = Field()
    title = Field()
    phone = Field()
    name = Field()
    price = Field()
    time = Field()
    types = Field()
    desc = Field()
    image = Field()




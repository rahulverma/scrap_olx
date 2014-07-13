from olx.database.persist import persist_item, close_connection, persist_largest_date
from datetime import datetime

class TutorialPipeline(object):
    def close_spider(self, spider):
        persist_largest_date()
        close_connection()

    def process_item(self, item, spider):
        persist_item(item)
        return item




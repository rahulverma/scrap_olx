# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tutorial'

SPIDER_MODULES = ['olx.spiders']
NEWSPIDER_MODULE = 'olx.spiders'
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22 AlexaToolbar/alxg-3.1"
ITEM_PIPELINES = {
    'olx.pipelines.TutorialPipeline': 300
    }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tutorial (+http://www.yourdomain.com)'

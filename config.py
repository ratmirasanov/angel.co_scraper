"""Module Config with applicable configuration information."""

import os

DOMAIN = os.environ.get('DOMAIN', 'https://angel.co')
EMAIL = os.environ.get('EMAIL', 'gfautotesting1@gmail.com')
PASSWORD = os.environ.get('PASSWORD', 'qwerty12345')
DELAY1 = 30
DELAY2 = 5
DELAY_COMPANY = 15
TIMER = 2700

SCROLL_PAUSE_TIME = 2

SCRAPER_URL = os.environ.get('SCRAPER_URL', 'https://api-email.growthfountain.com')
AUTHORIZATION = os.environ.get(
    'AUTHORIZATION', 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2'
    'VyX2lkIjozMTQsImZpcnN0X25hbWUiOiJBYnJhaGFtIiwibGFz'
    'dF9uYW1lIjoiT3JkZW4iLCJ1c2VyX2lwIjoiMTcyLjE3LjAuMS'
    'IsInNpdGVfaWQiOjIzfQ.X2q-wrCy8xrtHCOeX04ZlxR7b92ny'
    'UnOZBWfHh_KenA'
)
SLACK_URL = os.environ.get(
    'SLACK_TOKEN',
    'https://hooks.slack.com/services/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'
)

"""Module for sending emails of the Scraper Leads."""

import asyncio
import time
import json
from urllib.parse import urlencode
import urllib.request as urlrequest
import aiohttp

import config


async def init(loop):
    """A method for sending emails of the Scraper Leads."""

    while True:
        async with aiohttp.ClientSession(loop=loop) as session:
            response = await session.put(
                config.SCRAPER_URL + "/lead/send",
                headers={'authorization': config.AUTHORIZATION}
            )
            data = await response.json()

            if data['email']:
                msg = "Send email to {email}, \n" \
                      " Company: \'{company}\', \n" \
                      " Info: {note}".format(**data)
                payload_json = json.dumps({
                    "channel": "#scraper_nofitication",
                    "username": "webhookbot",
                    "text": msg,
                    "icon_emoji": ":ghost:"
                })
                data = urlencode({"payload": payload_json})
                opener = urlrequest.build_opener(urlrequest.HTTPHandler())
                req = urlrequest.Request(config.SLACK_URL)
                response = opener.open(req, data.encode("utf-8")).read()
                """
                print("R: ", response.decode("utf-8"))
                response = await session.post(
                    config.SLACK_URL,
                    data=bytes(data, "ascii"),
                    headers={'Content-Encoding': 'application/x-www-form-urlencoded'}
                )
                print("S: ", session.body)
                print("Slack response: ", await response.text())
                """
            else:
                print("Error no info about lead: ", data)
            time.sleep(config.DELAY1 * 2)


def main():
    """The main-method."""

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))


if __name__ == '__main__':
    main()

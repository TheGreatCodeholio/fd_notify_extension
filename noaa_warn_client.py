import json

import dateutil.parser
from threading import Thread
from lib.redis_handler import RedisCache
from lib.facebook_handler import connect_and_post_page
from lib.twitter_handler import post_to_twitter
import etc.config as config
import requests
from lxml import etree
import time

threads = []

noaa_link = f'https://alerts.weather.gov/cap/wwaatmget.php?x={config.noaa_warn["zone"]}&y=1'


def main_loop():
    while True:
        req = requests.get(noaa_link)
        xml = req.content
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        atom = etree.fromstring(xml)
        alerts = {}
        for element in atom.xpath('//atom:entry', namespaces=ns):
            warn_id = False
            title = False
            summary = False
            status = False
            urgency = False
            certainty = False
            expires = False
            expires_hrt = False
            category = False
            updated = False
            for node in element.iterchildren():
                if node.tag.find("event") > -1:
                    title = node.text
                elif node.tag.find("summary") > -1:
                    summary = node.text
                elif node.tag.find("status") > -1:
                    status = node.text
                elif node.tag.find("urgency") > -1:
                    urgency = node.text
                elif node.tag.find("certainty") > -1:
                    certainty = node.text
                elif node.tag.find("expires") > -1:
                    e = dateutil.parser.parse(node.text)
                    expires = (time.mktime(e.timetuple()) * 1e3 + e.microsecond / 1e3) / 1e3
                    expires_hrt = node.text
                elif node.tag.find("category") > -1:
                    category = node.text
                elif node.tag.find("id") > -1:
                    warn_id = node.text
                elif node.tag.find("updated") > -1:
                    u = dateutil.parser.parse(node.text)
                    updated = (time.mktime(u.timetuple()) * 1e3 + u.microsecond / 1e3) / 1e3
            if not title:
                continue
            else:
                result = RedisCache().get_warn_from_redis(warn_id.split("?x=")[1].split(".")[0])
                if result:
                    continue
                else:
                    alerts[warn_id.split("?x=")[1].split(".")[0]] = {"warn_id": warn_id.split("?x=")[1].split(".")[0],
                                                                     "event": title, "summary": summary,
                                                                     "status": status,
                                                                     "urgency": urgency, "certainty": certainty,
                                                                     "expires": expires, "expires_hrt": expires_hrt,
                                                                     "category": category, "updated": updated,
                                                                     "posted": time.time()}
                    RedisCache().add_warn_to_redis(alerts[warn_id.split("?x=")[1].split(".")[0]])
                    message = f'Weather Alert: {title}  \n'
                    message += f'Urgency: {urgency}     \n'
                    message += f'Certainty: {certainty} \n'
                    message += f'Expires: {expires_hrt} \n'
                    message += f'Link: {config.base_url}/wx_summary.php \n'
                    message += f'Summary: \n'
                    message += summary

                    if config.facebook_page_settings["enabled"] == 1:
                        facebook_page_list = config.facebook_page_settings["facebook_page_ids"]
                        for page in facebook_page_list:
                            Thread(target=connect_and_post_page, args=(message, page)).start()
                    if config.twitter_settings["enabled"] == 1:
                        Thread(target=post_to_twitter, args=message).start()
                    if config.discord_settings["enabled"] == 1:
                        if config.discord_settings["text"] == 1:
                            post_noaa_discord(alerts[warn_id.split("?x=")[1].split(".")[0]])

        if len(alerts) >= 1:
            print(alerts)
        else:
            print("No Alerts")
        time.sleep(600)


def expire_loop():
    while True:
        now = time.time()
        warnings = RedisCache().get_all_warn_from_redis()
        for warn in warnings:
            data = json.loads(str(warnings[warn].decode('utf-8')))
            if now >= data["expires"]:
                print("expired")
                RedisCache().rem_warn_from_redis(warn.decode('utf-8'))
            # if warnings[warn]["expires".encode('utf-8')]:
        time.sleep(600)


def post_noaa_discord(alert_data):
    r = requests.post(config.discord_settings["client_url"] + "/noaa", json=alert_data)
    if r.status_code == 200:
        print("Discord Client Accepted NOAA Post")
    else:
        print("Discord Client NOAA Post Error: " + str(r.status_code))


try:
    el = Thread(target=expire_loop)
    el.start()
    threads.append(el)
    ml = Thread(target=main_loop)
    ml.start()
    threads.append(ml)
except Exception as e:
    for th in threads:
        th.join()

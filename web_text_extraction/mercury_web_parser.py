# -*- coding: utf-8 -*-
import requests
import json


def extract_text(api_endpoint, web_url, retry=False):
    text = raw_text(api_endpoint, web_url)
    while text.find("<") >= 0:
        text = text.split("<", 1)[0] + text.split(">", 1)[1]
    text = text.replace("\n", " ")
    text = text.replace("&#xE4;", "ä").replace("&#xF6;", "ö").replace("&#xFC;", "ü").replace("&#xDF;", "ß")\
        .replace("&#xC4;", "Ä").replace("&#xD6;", "Ö").replace("&#xDC;", "Ü").replace("&#x201E;", '"')\
        .replace("&#x201C;", '"').replace("&#x2013;", '-').replace("&amp;", '&').replace("&#xA0", ' ')\
        .replace("&#xE6;", "æ").replace("&#xE5;", "å")
    len_of_text = len(text)
    while len_of_text > len(text.replace("  ", " ")):
        text = text.replace("  ", " ")
        len_of_text = len(text)
    print("after: " + text)
    if not retry:
        if text.find(" ") < 0 and "http://" in text:
            extract_text(api_endpoint, text, retry=True)
    return text


def raw_text(api_endpoint, web_url):
    headers = {"x-api-key": None}

    url = "{}?url={}".format(api_endpoint, web_url)
    response = requests.get(url, headers=headers)
    return response.json()['content']

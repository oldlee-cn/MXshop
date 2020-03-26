# -*- coding: utf-8 -*-
__author__ = 'oldlee'
__date__ = '2020-01-26 11:32'

import json
import requests


class Alisms(object):

    def __init__(self, apikey):
        self.apikey = apikey
        self.singe_sent_url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, code, moblie):
        parmas={
            'apikey': self.apikey,
            'mobile': moblie,
            'text': '【oldlee】您的验证码是{code}。如非本人操作，请忽略本短信。'.format(code=code)
        }

        respones = requests.post(self.singe_sent_url, data=parmas)
        re_dict = json.loads(respones.text)
        return re_dict


# if __name__ == '__mian__':
#     aliyunsms = Alisms(API_KEY)
#     aliyunsms.send_sms('1234', '18306160612')

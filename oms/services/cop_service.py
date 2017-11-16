# -*- coding: utf-8 -*-

import datetime
import time
import hashlib
import json
import xmltodict
import requests
from django.conf import settings
from oms.extension.exception import CopException
import logging
from oms_server.tasks import cop_retry

logger = logging.getLogger('custom.oms.cop_interface')


# 对接Cop的接口
class Interface(object):

    def __init__(self, method, custom_id, id=None):
        self.app_key = settings.OMS_APP_KEY
        self.app_secret = settings.OMS_APP_SECRET
        self.cop_url = settings.COP_URL
        self.callbacl_url = settings.OMS_CALLBACK_URL
        self.method = settings.METHOD_PRE + method
        self.custom_id = custom_id
        self.public_param = None
        self.id = id

    # 消息预处理：公共请求参数构造和签名
    def _pre_process_message(self, body):
        timestamp = datetime.datetime.\
            now().strftime('%Y-%m-%d %H:%M:%S')
        public_param = {
            'method': self.method,
            'customerId': self.custom_id,
            'app_key': self.app_key,
            'timestamp': timestamp,
            'format': 'xml',
            'v': '2.0',
            'sign_method': 'md5'
        }
        body = self._json_to_xml(body)
        self._sign(public_param, body)
        return public_param, body

    # 对外暴露的唯一接口
    def process_message(self, body):
        if not self.public_param:
            self.public_param, body = self._pre_process_message(body)
        assert self.public_param is not None, '处理公共请求参数出错'
        return self._post(self.public_param, body)

    # json转xml
    def _json_to_xml(self, j):
        x = xmltodict.unparse(j, pretty=False, full_document=False)
        return x

    # xml转json
    def _xml_to_json(self, x):
        j = json.loads(json.dumps(xmltodict.parse(x)))
        return j

    # 对请求参数签名
    def _sign(self, public_param, body):
        sorted_keys = sorted(public_param.keys())
        ret = self.app_secret
        for key in sorted_keys:
            if key == 'sign':
                continue
            ret += key + str(public_param[key])
        if body is not None:
            ret += body
        ret += self.app_secret
        sign = hashlib.md5(ret.encode("utf-8")).hexdigest()
        public_param['sign'] = sign.upper()
        return public_param

    # 构建请求url
    def _build_url(self, public_param):
        url = self.cop_url
        return url

    # 解析响应
    def unparse_response(self, response):
        r = None
        if response.headers['Content-Type'] == 'application/json':
            r = response.json()
        elif response.headers['Content-Type'] == 'text/xml':
            r = self._xml_to_json(response.text)
        else:
            # r = response.text
            r = self._xml_to_json(response.text)
        return r

    # http请求
    def _post(self, public_param, body):
        headers = {'Content-Type': 'text/xml;charset=utf-8'}
        url = self.cop_url
        # 失败 间隔10毫秒 重试
        # interval = 1

        logger.debug("-----send to cop  body-----------")
        logger.debug(body)
        logger.debug("------send to cop ------------")
        # while True:
        #     if interval > 5:
        #         raise CopException(self.method, '处理超时')
        #     try:
        resp = requests.\
            post(url=url, headers=headers,
                 params=public_param,
                 data=body.encode('utf-8'))
        r = self.unparse_response(resp)
        print(r['response']['code'], type(r['response']['code']))
        if r and int(r['response']['code']) == 0:
            logger.debug("处理成功")
            return r
        else:
            logger.debug("=========================")
            logger.debug(r)
            logger.debug("=========================")
            cop_retry.apply_async(
                (url, json.dumps(headers), json.dumps(public_param),
                 str(body.encode('utf-8')), self.id),
                retry=True, max_retries=3)
            # raise CopException(self.method, r)
            # except Exception as e:
            #     print(e)
            #     interval = interval * 2
            #     time.sleep(interval)
            #     continue

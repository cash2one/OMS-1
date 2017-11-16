# -*- coding: utf-8 -*-
import xmltodict
import json
from rest_framework.decorators import api_view, renderer_classes
from oms_api.services.wms_interface import WmsInterface
# from oms.extension.response_wrapper import JsonResponse
# from rest_framework_xml.parsers import XMLParser
# from rest_framework_xml.renderers import XMLRenderer
from oms_api.extension.renderers import XMLRenderer
from rest_framework.response import Response
import logging

logger = logging.getLogger('custom.oms.wms_message')

# test xml
@api_view(['GET'])
@renderer_classes((XMLRenderer,))
def test(request):
    result = {'test': '123', '123': 'test'}
    return Response(result)


@api_view(['GET','POST'])
# @renderer_classes((XMLRenderer,))
def posttest(request):
    data = request.GET
    test = data.get('test')
    haha = data.get('haha')
    logger.debug(request.body)
    data123 = json.loads(json.dumps(xmltodict.parse(request.body)))
    logger.debug(data123)
    result = {'test': test, 'haha': haha}
    return Response(result)


@api_view(['POST'])
@renderer_classes((XMLRenderer,))
def open_interface(request):
    logger.debug('------------------------------------')
    data = request.GET
    para = {}
    para['method'] = data.get('method')
    para['format'] = data.get('formater', 'XML')
    para['app_key'] = data.get('app_key')
    para['v'] = data.get('v')
    para['sign'] = data.get('sign')
    para['sign_method'] = data.get('sign_method')
    para['customerId'] = data.get('customerId')

    body = request.body
    logger.debug('======receive wms message==============')
    logger.debug(para)
    # print('parameters : ' + para)
    # print('xml body or json : ' + body)

    if para['format'] == 'XML':
        data = json.loads(json.dumps(xmltodict.parse(body)))
    elif para['format'] == 'json':
        data = json.loads(body)
    logger.debug('json : ' + str(data))
    logger.debug('======receive wms message end==============')

    method = para['method'].replace('.', '_')
    wms_interface = WmsInterface(para, data['request'])
    return Response(getattr(wms_interface, method)())


def get_parameters(data):
    print('request.post : '+data)
    para = {}
    para['method'] = data.get('method')
    para['format'] = data.get('format', 'xml')
    para['app_key'] = data.get('app_key')
    para['v'] = data.get('v')
    para['sign'] = data.get('sign')
    para['sign_method'] = data.get('sign_method')
    para['customerid'] = data.get('customerid')
    return para

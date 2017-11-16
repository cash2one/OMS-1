# -*- coding:utf-8 -*-
import logging

logger = logging.getLogger('custom.request')


class RequestMiddleware:

    def process_request(self, request):
        message = str(request.method) + ' ' + str(request.get_full_path()) + "\n"
        if(request.method == "POST"):
            message += "Query params:" + str(request.POST) + "\n"
            message += "Body:" + request.body.decode("utf-8") + "\n"
        elif(request.method == "GET"):
            message += "Query params:" + str(request.GET)
        logger.debug(message)

    def process_response(self, request, response):
        message = str(request.method) + ' ' + str(request.get_full_path()) + "\n"
        message += "Response:" + response.content.decode("utf-8")
        try:
            status = response.data['success']
            if not status:
                logger.exception(message, exc_info=True)
                return response
        except Exception as e:
            pass
        logger.info(message)
        return response
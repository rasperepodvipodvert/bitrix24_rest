#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads
from logging import info
from time import sleep
from requests import adapters, post, exceptions
from multidimensional_urlencode import urlencode


class Bitrix24(object):
    domain = 'sysadmin.bitrix24.ru'
    webhook_key = '5hi9bb2vqmqql3sr'
    webhook_url = 'https://%s.bitrix24.ru/rest/%d/%s/%s'
    timeout = 60

    def __init__(self, domain, webhook_key='', webhook_user=1):
        self.domain = domain
        self.webhook_key = webhook_key
        self.webhook_user = webhook_user

    def get_url(self, method):
        if self.webhook_key:
            return self.webhook_url % (self.domain, self.webhook_user, self.webhook_key, method)
        else:
            return self.api_url % (self.domain, method)

    @staticmethod
    def prepare_batch(params):
        """
        Prepare methods for batch call
        :param params: dict
        :return: dict
        """
        if not isinstance(params, dict):
            raise Exception('Invalid \'cmd\' structure')

        batched_params = dict()

        for call_id in sorted(params.keys()):
            if not isinstance(params[call_id], list):
                raise Exception('Invalid \'cmd\' method description')
            method = params[call_id].pop(0)
            if method == 'batch':
                raise Exception('Batch call cannot contain batch methods')
            temp = ''
            for i in params[call_id]:
                temp += urlencode(i) + '&'
            batched_params[call_id] = method + '?' + temp

        return batched_params

    @staticmethod
    def encode_cmd(cmd):
        """Resort batch cmd by request keys and encode it
        :param cmd: dict List methods for batch request with request ids
        :return: str
        """
        cmd_encoded = ''

        for i in sorted(cmd.keys()):
            cmd_encoded += urlencode({'cmd': {i: cmd[i]}}) + '&'

        return cmd_encoded

    def call(self, method, params1=None, params2=None, params3=None, params4=None):
        """Call Bitrix24 API method
        :param method: Method name
        :param params1: Method parameters 1
        :param params2: Method parameters 2. Needed for methods with determinate consequence of parameters
        :param params3: Method parameters 3. Needed for methods with determinate consequence of parameters
        :param params4: Method parameters 4. Needed for methods with determinate consequence of parameters
        :return: Call result
        """
        if method == '' or not isinstance(method, str):
            raise Exception('Empty Method')

        if method == 'batch' and 'prepared' not in params1:
            params1['cmd'] = self.prepare_batch(params1['cmd'])
            params1['prepared'] = True

        encoded_parameters = ''

        # print params1
        for i in [params1, params2, params3, params4]:
            if i is not None:
                if 'cmd' in i:
                    i = dict(i)
                    encoded_parameters += self.encode_cmd(i['cmd']) + '&' + urlencode({'halt': i['halt']}) + '&'
                elif 'filter' in i:
                    # i = dict(i)
                    encoded_parameters += urlencode(i)
                else:
                    encoded_parameters += urlencode(i) + '&'

        r = {}
        try:
            # request url
            url = self.get_url(method)
            # Make API request
            r = post(url, data=encoded_parameters, timeout=self.timeout)
            # Decode response
            result = loads(r.text)
        except ValueError:
            result = dict(error='Error on decode api response [%s]' % r.text)
        except exceptions.ReadTimeout:
            result = dict(error='Timeout waiting expired [%s sec]' % str(self.timeout))
        except exceptions.ConnectionError:
            result = dict(error='Max retries exceeded [' + str(adapters.DEFAULT_RETRIES) + ']')
        if 'error' in result and result['error'] in ('NO_AUTH_FOUND', 'expired_token'):
            result = self.refresh_tokens()
            if result is not True:
                return result
            # Repeat API request after renew token
            result = self.call(method, params1, params2, params3, params4)
        elif 'error' in result and result['error'] in ('QUERY_LIMIT_EXCEEDED',):
            # Suspend call on two second, wait for expired limitation time by Bitrix24 API
            print('SLEEP =)')
            sleep(2)
            return self.call(method, params1, params2, params3, params4)
        return result

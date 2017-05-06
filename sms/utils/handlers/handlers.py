import collections, logging

from django.conf import settings
import requests

from .exceptions import SMSHandlerError


sms_logger = logging.getLogger('sms_logger')


# FieldsMap "class" for mapping params with fields name for specific handler
FieldsMap = collections.namedtuple('FieldsMap', ('user', 'password', 'phone', 'message', 'check_success'))


class BaseHandler:
    """Base handler for handlers implementation.
    Attributes:
        BaseHandler.config (dict): handler settings, stored in settings file: SMS_GATES[<GATE_NAME>].
        Example:
            'MY_GATE': {
                'HOST': 'http://mygate.com',
                'USER': 'guest',
                'PASSWORD': 'guest',
                'PARAMS': {'charset': 'utf-8'}
            }
        
        BaseHandler.fields_map (FieldsMap): mapping params with fields name for handler
    """
    config = None
    fields_map = None

    @classmethod
    def _make_request(cls, phone, message):
        """Makes request and return response
        Args:
            phone (str): Phone number
            message (str): Text message
        Returns:
            requests.Response: Gate response
        Raises:
            SMSHandlerError: for invalid configurations and request/response errors
        """
        if not cls.config:
            raise SMSHandlerError('Handler property: config is empty')
        elif any(param not in cls.config for param in ('HOST', 'USER', 'PASSWORD')):
            raise SMSHandlerError('Invalid handler property: config. HOST, USER or PASSWORD are not configured')
        if not isinstance(cls.fields_map, FieldsMap):
            raise SMSHandlerError('Invalid handler property: fields_map')
        if not phone or not message:
            raise SMSHandlerError('Phone number or message are not specified')

        params = {
            cls.fields_map.user: cls.config['USER'],
            cls.fields_map.password: cls.config['PASSWORD'],
            cls.fields_map.phone: phone,
            cls.fields_map.message: message,
        }
        params.update(cls.config.get('PARAMS', {}))
        response = requests.post(cls.config['HOST'], params=params)
        if response.status_code != 200:
            raise SMSHandlerError('Failed to send sms, request status code: %s' % response.status_code)
        return response

    @classmethod
    def _parse_response(cls, response):
        """Parse response and detect successful gate response by specific field (BaseHandler.fields_map.check_success)
        Args:
            response (requests.Response): Gate response
        Returns:
            dict: Gate response in json format
        Raises:
            SMSHandlerError: if can't parse response or BaseHandler.fields_map.check_success has invalid value
        """
        try:
            response = response.json()
        except ValueError:
            raise SMSHandlerError('Failed to parse response from gate')
        status = response.get(cls.fields_map.check_success['field'], None)
        if status != cls.fields_map.check_success['value']:
            raise SMSHandlerError('Failed to send sms, field "%(name)s" != "%(value)s"' % cls.fields_map.check_success)
        return response

    @classmethod
    def send(cls, phone, message):
        """Send SMS
        Args:
            phone (str): Phone number
            message (str): Text message
        Returns:
            dict: Result in dict format: {'success': True|False, 'payload': str}
        """
        result = {'success': False, 'payload': None}
        try:
            response = cls._make_request(phone, message)
            result.update(success=True, payload=cls._parse_response(response))
            sms_logger.info(
                'SMS was sent. Handler: %s' % cls.__name__,
                extra={'phone': phone, 'text': message, 'payload': result['payload']}
            )
        except Exception as error:
            result.update(success=False, payload=error)
            sms_logger.error(
                "SMS wasn't sent. Handler: %s" % cls.__name__,
                extra={'phone': phone, 'text': message, 'payload': error}
            )
        return result


class SMSCHandler(BaseHandler):
    """SMSC gate handler: https://smsc.ru/api/"""
    config = settings.SMS_GATES['SMSC']
    fields_map = FieldsMap(
        user='login',
        password='psw',
        phone='phones',
        message='mes',
        check_success={'field': 'cnt', 'value': 1}
    )


class SMSTraffic(BaseHandler):
    """SMSTraffic gate handler: https://www.smstraffic.ru/"""
    config = settings.SMS_GATES['SMSTraffic']
    fields_map = FieldsMap(
        user='username',
        password='passwd',
        phone='phone',
        message='message',
        check_success={'field': 'status', 'value': 'ok'}
    )

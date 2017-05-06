# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import TestCase

from sms.utils import get_handler
from sms.utils.handlers import SMSHandlerError


class TestGetHandler(TestCase):
    def test_available_handler(self):
        handler = get_handler('SMSC')
        self.assertEqual(handler.__name__, 'SMSCHandler')

    def test_unknown_handler(self):
        with self.assertRaises(SMSHandlerError):
            get_handler('ABC')


class TestSMSCHandler(TestCase):

    HANDLER_NAME = 'SMSC'
    PHONE, MESSAGE = '79101926229', 'Тестовое СМС'

    def setUp(self):
        config = settings.SMS_GATES['SMSC'].copy()
        self.handler = get_handler('SMSC')
        self.handler.config = config

    def test_success_send(self):
        handler = get_handler(self.HANDLER_NAME)
        result = handler.send(self.PHONE, self.MESSAGE)
        self.assertTrue(result['success'])

    def test_invalid_response(self):
        self.handler.config['HOST'] = 'http://yarysh.com'
        result = self.handler.send(self.PHONE, self.MESSAGE)
        self.assertFalse(result['success'])
        self.assertIsInstance(result['payload'], SMSHandlerError)
        self.assertEqual(str(result['payload']), 'Failed to parse response from gate')

    def test_invalid_host(self):
        self.handler.config['HOST'] = 'https://test'
        result = self.handler.send(self.PHONE, self.MESSAGE)
        self.assertFalse(result['success'])

    def test_empty_gate_host(self):
        self.handler.config = {}
        result = self.handler.send(self.PHONE, self.MESSAGE)
        self.assertFalse(result['success'])
        self.assertIsInstance(result['payload'], SMSHandlerError)
        self.assertEqual(str(result['payload']), 'Handler property: config is empty')

    def test_empty_host(self):
        del self.handler.config['HOST']
        result = self.handler.send(self.PHONE, self.MESSAGE)
        self.assertFalse(result['success'])
        self.assertIsInstance(result['payload'], SMSHandlerError)
        self.assertEqual(str(result['payload']), 'Invalid handler property: config. HOST, USER or PASSWORD are not configured')

    def test_empty_phone(self):
        result = self.handler.send('', self.MESSAGE)
        self.assertFalse(result['success'])
        self.assertIsInstance(result['payload'], SMSHandlerError)
        self.assertEqual(str(result['payload']), 'Phone number or message are not specified')

    def test_empty_message(self):
        result = self.handler.send(self.PHONE, '')
        self.assertFalse(result['success'])
        self.assertIsInstance(result['payload'], SMSHandlerError)
        self.assertEqual(str(result['payload']), 'Phone number or message are not specified')

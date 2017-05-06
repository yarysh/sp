from . import handlers
from .handlers import SMSTraffic, SMSCHandler
from .exceptions import SMSHandlerError


def get_handler(handler_name):
    """
    Return available handler by name: <handler_name>Handler
    :rtype: handlers.BaseHandler
    """
    try:
        return getattr(handlers, handler_name + 'Handler')
    except AttributeError:
        raise SMSHandlerError('Handler: %s not found' % handler_name)

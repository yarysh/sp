import logging


class DbLogHandler(logging.Handler):
    def emit(self, record):
        from .models import SMSLog
        try:
            SMSLog.objects.create(
                phone=getattr(record, 'phone', None),
                text=getattr(record, 'text'),
                payload=getattr(record, 'payload'),
                success=record.levelname != 'ERROR',
            )
        except Exception:
            pass

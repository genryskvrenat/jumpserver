from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task

from common.sdk.sms.exceptions import CodeError, CodeExpired, CodeSendTooFrequently
from common.sdk.sms.endpoint import SMS
from common.exceptions import JMSException
from common.utils.random import random_string
from common.utils import get_logger


logger = get_logger(__file__)


@shared_task
def send_async(sender):
    sender.gen_and_send()


class SendAndVerifyCodeUtil(object):
    KEY_TMPL = 'auth-verify-code-{}'

    def __init__(self, target, code=None, key=None, backend='email', timeout=None, **kwargs):
        self.code = code
        self.target = target
        self.backend = backend
        self.key = key or self.KEY_TMPL.format(target)
        self.timeout = settings.VERIFY_CODE_TTL if timeout is None else timeout
        self.other_args = kwargs

    def gen_and_send_async(self):
        return send_async.delay(self)

    def gen_and_send(self):
        ttl = self.__ttl()
        if ttl > 0:
            logger.error('Send sms too frequently, delay {}'.format(ttl))
            raise CodeSendTooFrequently(ttl)

        try:
            if not self.code:
                self.code = self.__generate()
            self.__send(self.code)
        except JMSException:
            self.__clear()
            raise

    def verify(self, code):
        right = cache.get(self.key)
        if not right:
            raise CodeExpired

        if right != code:
            raise CodeError

        self.__clear()
        return True

    def __clear(self):
        cache.delete(self.key)

    def __ttl(self):
        return cache.ttl(self.key)

    def __get_code(self):
        return cache.get(self.key)

    def __generate(self):
        code = random_string(4, lower=False, upper=False)
        self.code = code
        return code

    def __send_with_sms(self):
        sms = SMS()
        sms.send_verify_code(self.target, self.code)

    def __send_with_email(self):
        subject = self.other_args.get('subject')
        message = self.other_args.get('message')
        from_email = settings.EMAIL_FROM or settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [self.target], html_message=message)

    def __send(self, code):
        """
        发送信息的方法，如果有错误直接抛出 api 异常
        """
        if self.backend == 'sms':
            self.__send_with_sms()
        else:
            self.__send_with_email()

        cache.set(self.key, self.code, self.timeout)
        logger.info(f'Send verify code to {self.target}: {code}')

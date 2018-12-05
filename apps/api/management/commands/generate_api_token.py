import logging

from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token
from apps.user.models.user import User


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate token for user with telegram_chat_id. New user will be created if not existed.'

    def add_arguments(self, parser):
        parser.add_argument('telegram_chat_id', type=str)

    def handle(self, *args, **options):
        logger.info(f"Creating REST API token for user with telegram_chat_id: {options['telegram_chat_id']}")
        create_new_token_for_user_with(options['telegram_chat_id'])

def create_new_token_for_user_with(telegram_chat_id):
    user, created = User.objects.get_or_create(telegram_chat_id = telegram_chat_id)
    if created:
        token = Token.objects.create(user=user)
    else:
        token = Token.objects.get(user=user)

    logger.info(f"{'New' if created else 'Existing'} token for user with telegram is:{telegram_chat_id} is:\n{token.key}")
    logger.info(f"""
    For clients to authenticate, the token key should be included in the Authorization HTTP header.
    The key should be prefixed by the string literal "Token", with whitespace separating the two strings.
    For example:\n
    Authorization: Token {token.key}
    """)

    # user = User.objects.filter(username="test@test.com").first()
    # if user is not None:
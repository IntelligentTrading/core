import logging

from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token
from apps.user.models.user import User


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate token for user with telegram_chat_id. New user will be created if not existed.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('telegram_chat_id', type=str)

        parser.add_argument(
            '-r',
            '--reset',
            action='store_true',
            dest='reset_token',
            default=False,
            help='Reset existing User token and create a new one',
        )

    def handle(self, *args, **options):
        username = options['username']
        telegram_chat_id = options['telegram_chat_id']
        reset_token = options['reset_token']

        if reset_token:
            reset_token_for_user(username)

        create_token_for_user(username, telegram_chat_id)

#        logger.info(f"Creating REST API token for user with username: {username} and telegram_chat_id: {telegram_chat_id}")



def reset_token_for_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise CommandError(f'Cannot create the Token: user {username} does not exist')
    else:
        Token.objects.filter(user=user).delete()
        print(f'Deleted old token for user {username}')


def create_token_for_user(username, telegram_chat_id):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username, telegram_chat_id=telegram_chat_id)
        user.save()
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)

    print(f'Use token {token.key} for user {username}')
    print(f"""
For clients to authenticate, the token key should be included in the Authorization HTTP header.
The key should be prefixed by the string literal "Token", with whitespace separating the two strings.
For example:\n
Authorization: Token {token.key}""")
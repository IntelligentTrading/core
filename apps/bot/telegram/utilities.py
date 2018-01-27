
# decorator for telegram_bot commands, responses
def telegram_command(execution_handle, pass_args=False):
    def telegram_command_decorator(response_function):

        def command_wrapper(bot, update, args=""):

            # get chat id
            chat_id = update.message.chat_id

            # run commnad with (or without) args and get response
            if pass_args and not args:
                response_string = "/" + response_function.__name__ + " command requires at least one argument"
            else:
                response_string = response_function(args) if pass_args else response_function()
            # send response back to user
            bot.send_message(chat_id=chat_id, text=response_string)

            # todo: check chat_id is registered. if not, register user after reponse.

        command_wrapper.execution_handle = execution_handle
        command_wrapper.help_text = ""
        command_wrapper.pass_args = pass_args  # True or False

        return command_wrapper

    return telegram_command_decorator


# class TelegramCommand(object):
#     def __init__(self, execution_handle, requires_args=False):
#         self.execution_handle = execution_handle
#         self.requires_args = requires_args
#         self.help_text = ""
#
#     def __call__(self, *args, **kwargs):
#
#         if self.requires_args and len(args) == 0:
#             raise ChatBotException(
#                 user_message="",
#                 developer_message=""
#             )
#
#         else:
#             return self.call_function(args)
#
#     def call_function(self, args=[]):
#         pass


class ChatBotException(Exception):
    def __init__(self, user_message="", developer_message=""):
        self.user_message = user_message
        self.developer_message = developer_message

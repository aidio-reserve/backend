import json

user_settion = {}


def restore_message(message):
    user_settion["response"] = message


input_message = input("Please enter a message: ")
restore_message(input_message)
print(json.dumps(user_settion, indent=4))

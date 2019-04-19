import zulip


def relay_messages(mess):
    # Pass the path to your zuliprc file here.
    client = zulip.Client(config_file="zuliprc")
    # Send a stream message
    request = {
        "type": "stream",
        "to": "bots (deprecated)",
        "subject": "Castle",
        "content": mess,
    }
    result = client.send_message(request)
    print(result)

# relay_messages('abc')
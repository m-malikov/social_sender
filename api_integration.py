class SendError(ValueError):
    def __init__(self, target_code):
        ValueError.__init__(self, "Error sending post: {}".format(target_code))


def send(target, text, token):
    print("sent {} to {}".format(text, target))

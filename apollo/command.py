import datetime


class Command(object):
    def __init__(self, data):
        self.data = data
        self.created_at = datetime.datetime.utcnow()
        self.result = None

    def set_result(self):
        """
        1. Error
            - timed out
        2. Cancelled
        3. ...
        4. Successful

        :return:
        """
        pass
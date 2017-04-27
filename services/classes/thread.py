import threading
from django.core.management import call_command


class BackgroundProcess(threading.Thread):

    def __init__(self, **kwargs):
        print("BackgroundProcess initialized")
        threading.Thread.__init__(self)
        self.threadID = kwargs.get('thread_id')
        self.name = kwargs.get('name')
        self.process = kwargs.get('process')
        self.positional_params = kwargs.get('positional_params')
        self.others_params = kwargs.get('others_params')
        self.provider = kwargs.get('provider')

    def run(self):
        try:
            print("BackgroundProcess called")
            call_command(self.process)
        except Exception as error:
            print("Error: " + str(error))

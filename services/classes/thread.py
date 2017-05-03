import threading
from services.models import SCHEDULED_WORK_IMPORTATION_PROCESS, SCHEDULED_WORK_CORRESPONDENCE_PROCESS, \
    SCHEDULED_WORK_CORRESPONDENCE_TYPE, Parameters, SCHEDULED_WORK_LEARNING_ALGORITHM
from django.core.management import call_command


class BackgroundProcess(threading.Thread):

    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.threadID = kwargs.get('thread_id')
        self.name = kwargs.get('name')
        self.process = kwargs.get('process')
        self.positional_params = kwargs.get('positional_params')
        self.others_params = kwargs.get('others_params')
        self.provider = kwargs.get('provider')

    def run(self):
        try:
            if self.process in (SCHEDULED_WORK_CORRESPONDENCE_TYPE, SCHEDULED_WORK_CORRESPONDENCE_PROCESS,
                                SCHEDULED_WORK_LEARNING_ALGORITHM):
                call_command(self.process)
            elif self.process == SCHEDULED_WORK_IMPORTATION_PROCESS:
                path = Parameters.objects.only('value').get(name='directory_path_importation').value
                call_command(self.process, path + self.positional_params, skip_geonames=True)

        except Exception as error:
            print("Error: " + str(error))

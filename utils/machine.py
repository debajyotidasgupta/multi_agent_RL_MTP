import json


class Machine(object):
    def __init__(self, _name, _id, uuid):   # This is for initialization
        self.uuid = uuid
        self.name = _name
        self.id = _id
        self.jobs = list()

    def __str__(self):  # This is for printing
        return f'{self.name} [{self.uuid}]\n{json.dumps(self.jobs, indent=4)}'

    def __repr__(self):  # This is for printing
        return self.name

    def add_job(self, job, uuid):  # This is for adding a job to the machine
        for i, elem in enumerate(job):
            duration, power = elem
            self.jobs.append((duration, power, (uuid, i)))

    def get_jobs(self):  # This is for getting the jobs of the machine
        return self.jobs

    def push(self, job, uuid):    # This is for adding a job to the machine
        self.add_job(job, uuid)

    def pop(self):  # This is for getting the topmost job of the machine
        return self.jobs.pop(0)

import json


class Machine(object):
    def __init__(self, _name, _id, uuid):   # This is for initialization
        self.uuid = uuid
        self.name = _name
        self.id = _id
        self.jobs = list()
        self.busy = -1
        self.remaining_jobs = 0
        self.current_power = 0

    def __str__(self):  # This is for printing
        return f'{self.name} [{self.uuid}]\n{json.dumps(self.jobs, indent=4)}'

    def __repr__(self):  # This is for printing
        return self.name

    def add_job(self, job, deadline, uuid):  # This is for adding a job to the machine
        for i, elem in enumerate(job):
            duration, power = elem
            self.jobs.append((duration, power, deadline, (*uuid, i)))
            self.remaining_jobs += 1

    def get_jobs(self):  # This is for getting the jobs of the machine
        return self.jobs

    def push(self, job, uuid):    # This is for adding a job to the machine
        self.add_job(job, uuid)

    def pop(self):  # This is for getting the topmost job of the machine
        if self.remaining_jobs == 0:
            raise IndexError('No jobs left')
        self.remaining_jobs -= 1
        return self.jobs.pop(0)

    def set_busy(self, t):  # This is for setting the machine busy
        self.busy = t

    def peek(self):
        return self.jobs[0]

    def is_busy(self, t):
        return self.busy > t

    def set_power(self, power):
        self.current_power = power

    def get_power(self, t):
        if self.is_busy(t):
            return self.current_power
        return 0

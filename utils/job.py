import json


class Job:
    def __init__(self, job_list, step):
        self.job_list = dict()
        for job in job_list:
            name = job['id']
            self.job_list[name] = []
            for cycle in job['cycles']:
                duration = cycle['duration'] / step
                power = cycle['power']
                self.job_list[name].append((duration, power))

    def get_job(self, name):
        return self.job_list[name]

    def __delitem__(self, name):
        del self.job_list[name]

    def __getitem__(self, name):
        return self.job_list[name]

    def __setitem__(self, name, value):
        self.job_list[name] = value

    def __str__(self):
        return json.dumps(self.job_list, indent=4)

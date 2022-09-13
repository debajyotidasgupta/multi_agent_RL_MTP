class Schedule:
    def __init__(self, job_id, machine_id, start_time, end_time):
        self.job_id = job_id
        self.machine_id = machine_id
        self.start_time = start_time
        self.end_time = end_time


class Solver:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.schedule_list = []
        self.optimal_cost = 0

    def solve(self):
        raise NotImplementedError()

    def __str__(self):
        return self.name

class Schedule:
    def __init__(self, job_id, machine_id, start_time, end_time):
        self.job_id = job_id
        self.machine_id = machine_id
        self.start_time = start_time
        self.end_time = end_time


class Solver:
    def __init__(self, env, price, name):
        self.env = env
        self.price = price
        self.name = name
        self.schedule_list = []
        self.cost = 0

        self.total_jobs = 0
        for house in env.S:
            for machine_id in env.S[house]:
                for machine in env.S[house][machine_id]:
                    self.total_jobs += machine.remaining_jobs

    def solve(self):
        raise NotImplementedError()

    def __str__(self):
        # output = f'\n\
        #     SOLVER: {self.name}\n\
        #     COST: {self.cost}\n\
        #     JOBS SCHEDULED: {len(self.schedule_list)} / {self.total_jobs}\n\
        # '
        output = f'\n\
             ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐\n\
             │ SOLVER: {self.name: <92} │\n\
             ├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n\
             │ COST: {self.cost: <94} │\n\
             ├──────────────────────────────────────────────────────────────────────────────────────────────────────┤\n\
             │ JOBS SCHEDULED: {len(self.schedule_list)} / {self.total_jobs: <79} │\n\
             └──────────────────────────────────────────────────────────────────────────────────────────────────────┘\n\
        '
        return output

    def scehdule(self):
        output = f'\n\
            SCHEDULE:\n\
                ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐\n\
                │    JOB ID       │ MACHINE ID      │ START TIME      │ END TIME        │\n\
                ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤\
        '
        for schedule in self.schedule_list:
            output += f'\n\
                │ {str(schedule.job_id):>15} │ {schedule.machine_id:>15} │ {schedule.start_time:>15} │ {schedule.end_time:>15} │\
            '
        output += f'\n\
                └─────────────────┴─────────────────┴─────────────────┴─────────────────┘\n\
        '
        return output

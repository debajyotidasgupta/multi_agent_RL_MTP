import json
from .machine import Machine
from collections import defaultdict


class Env:
    def __init__(self, building, job_list, machines, day):
        self.day = day
        self.S = defaultdict(lambda: defaultdict(list))
        self.n_machines = defaultdict(lambda: defaultdict(int))
        self.n_jobs = defaultdict(lambda: defaultdict(int))
        self.m_alloc = defaultdict(lambda: defaultdict(int))

        # Initialize machines in each house with their jobs
        m_counter = 0
        for apt in building:
            house = apt['house']  # Get the house number
            tasks = apt['tasks']  # Get the tasks

            # Iterate over the tasks in the house
            for task in tasks:
                _id = task['id']
                n_m = task['machine']  # Get the number of machines
                n_j = task['job']  # Get the number of jobs

                # Find the name of the machine
                for machine in machines:
                    if machine['id'] == _id:
                        name = machine['name']
                        break

                # Add the machine to the house
                for i in range(n_m):
                    self.S[house][_id].append(Machine(name, _id, m_counter))
                    m_counter += 1

                alloc = 0
                # Uniformly allocate the jobs to the machines
                # [-] Single job cannot be allocated to multiple machines
                for i in range(n_j):
                    self.S[house][_id][alloc].add_job(
                        job_list[_id], (house, _id, i))
                    self.m_alloc[(house, i)] = self.S[house][_id][alloc].uuid
                    alloc = (alloc + 1) % n_m

                # Update the number of machines and jobs
                self.n_machines[house][_id] = n_m
                self.n_jobs[house][_id] = n_j

    def __str__(self):
        return json.dumps(self.S, indent=2, default=vars)

    def reset(self, building, job_list, machines, day):
        self.__init__(building, job_list, machines, day)

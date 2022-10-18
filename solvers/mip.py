from .base import Solver, Schedule
from ortools.linear_solver import pywraplp


class MIPSolver(Solver):
    def __init__(self, env, price):
        super().__init__(env, price, 'Mixed Integer Program')

        self.variables = {}
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise Exception('No solver available.')

    def add_variables(self, debug=False):
        T = self.env.day

        for house in self.env.S:
            for machine_id in self.env.S[house]:
                for machine in self.env.S[house][machine_id]:
                    for job in machine.jobs:
                        duration, _, job_id = job
                        _, _, n_job, n_op = job_id
                        start_time = f'S_{house}_{machine_id}_{n_job}_{n_op}'
                        self.variables[start_time] = self.solver.IntVar(
                            0, T-duration, start_time)

                        if debug:
                            print(f'0 <= {start_time} <= {T-duration}')

                        for i in range(len(self.price)):
                            time_decider = f'T_{house}_{machine_id}_{n_job}_{n_op}_{i}'
                            self.variables[time_decider] = self.solver.IntVar(
                                0, 1, time_decider)

                            if debug:
                                print(f'0 <= {time_decider} <= 1')

                        print()

    def add_constraints(self, debug=False):
        T = self.env.day
        M = 1000000

        job_costs = []
        debug_costs = []

        for house in self.env.S:
            for machine_id in self.env.S[house]:
                for machine in self.env.S[house][machine_id]:
                    for i in range(len(machine.jobs)):
                        for j in range(i+1, len(machine.jobs)):
                            job_i = machine.jobs[i]
                            job_j = machine.jobs[j]

                            duration_i, _, job_id_i = job_i
                            duration_j, _, job_id_j = job_j

                            _, _, n_job_i, n_op_i = job_id_i
                            _, _, n_job_j, n_op_j = job_id_j

                            start_time_i = f'S_{house}_{machine_id}_{n_job_i}_{n_op_i}'
                            start_time_j = f'S_{house}_{machine_id}_{n_job_j}_{n_op_j}'

                            self.solver.Add(
                                self.variables[start_time_i] + duration_i <= self.variables[start_time_j])

                            if debug:
                                print(
                                    f'{start_time_i} + {duration_i} <= {start_time_j}')

                            # self.solver.Add(self.variables[start_time_j] + duration_j <= self.variables[start_time_i] + M * (
                            #     1 - self.variables[end_time_j] + self.variables[start_time_i]))

                    for job in machine.jobs:
                        duration, _, job_id = job
                        _, _, n_job, n_op = job_id
                        start_time = f'S_{house}_{machine_id}_{n_job}_{n_op}'

                        time_delta = []
                        debug_delta = []

                        for i in range(len(self.price)):
                            [_from, _to, _price] = self.price[i]
                            time_decider = f'T_{house}_{machine_id}_{n_job}_{n_op}_{i}'
                            time_delta.append(
                                self.variables[time_decider] * _price)
                            debug_delta.append(
                                f'{time_decider} * {_price}')

                            self.solver.Add(- M * (
                                1 - self.variables[time_decider]) <= self.variables[start_time] - _from)
                            self.solver.Add(self.variables[start_time] - _to <= M * (
                                1 - self.variables[time_decider]))

                            if debug:
                                print(
                                    f'-M * (1 - {time_decider}) <= {start_time} - {_from}')
                                print(
                                    f'{start_time} - {_to} <= M * (1 - {time_decider})')

                        job_costs.append(
                            duration * self.solver.Sum(time_delta))
                        debug_costs.append(
                            f'{duration} * ({" + ".join(debug_delta)})')

        self.solver.Minimize(self.solver.Sum(job_costs))
        if debug:
            print(f'Minimize: {" + ".join(debug_costs)}')

    def solve(self):

        debug = True
        if debug:
            print('Constraints:')

        self.add_variables(debug)
        self.add_constraints(debug)

        status = self.solver.Solve()
        power_usage = [0 for _ in range(self.env.day)]

        if status == pywraplp.Solver.OPTIMAL:
            for house in self.env.S:
                for machine_id in self.env.S[house]:
                    for machine in self.env.S[house][machine_id]:
                        for job in machine.jobs:
                            duration, power, job_id = job
                            _, _, n_job, n_op = job_id

                            start_time_variable = f'S_{house}_{machine_id}_{n_job}_{n_op}'
                            start_time = int(
                                self.variables[start_time_variable].solution_value())

                            self.schedule_list.append(
                                Schedule(job_id, machine_id, start_time, start_time + duration))

                            for i in range(start_time, start_time + duration):
                                power_usage[i] += power

            self.cost = 0
            for t in range(len(power_usage)):
                self.cost += self.price(t) * power_usage[t]

        else:
            raise Exception('The problem does not have an optimal solution.')

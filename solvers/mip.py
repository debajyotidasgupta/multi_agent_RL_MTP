from .base import Solver, Schedule
from ortools.linear_solver import pywraplp


class MIPSolver(Solver):
    def __init__(self, env, price):
        super().__init__(env, price, 'Mixed Integer Program')

        self.variables = {}
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            raise Exception('No solver available.')

    def add_variables(self):
        T = self.env.day

        for house in self.env.S:
            for machine_id in self.env.S[house]:
                for machine in self.env.S[house][machine_id]:
                    for job in machine.jobs:
                        _, _, job_id = job
                        _, _, n_job, n_op = job_id
                        start_time = f'S_{house}_{machine_id}_{n_job}_{n_op}'
                        end_time = f'E_{house}_{machine_id}_{n_job}_{n_op}'
                        self.variables[start_time] = self.solver.IntVar(
                            0, T-1, start_time)
                        self.variables[end_time] = self.solver.IntVar(
                            0, T, end_time)

                        for i in range(len(self.price)):
                            time_decider = f'T_{house}_{machine_id}_{n_job}_{n_op}_{i}'
                            self.variables[time_decider] = self.solver.IntVar(
                                0, 1, time_decider)

    def add_constraints(self):
        T = self.env.day
        M = 1000000

        job_costs = []
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

                            end_time_i = f'E_{house}_{machine_id}_{n_job_i}_{n_op_i}'
                            end_time_j = f'E_{house}_{machine_id}_{n_job_j}_{n_op_j}'

                            self.solver.Add(self.variables[start_time_i] + duration_i <= self.variables[start_time_j] + M * (
                                1 - self.variables[end_time_i] + self.variables[start_time_j]))

                            self.solver.Add(self.variables[start_time_j] + duration_j <= self.variables[start_time_i] + M * (
                                1 - self.variables[end_time_j] + self.variables[start_time_i]))

                    for job in machine.jobs:
                        duration, _, job_id = job
                        _, _, n_job, n_op = job_id
                        start_time = f'S_{house}_{machine_id}_{n_job}_{n_op}'
                        end_time = f'E_{house}_{machine_id}_{n_job}_{n_op}'
                        self.solver.Add(
                            self.variables[start_time] + duration == self.variables[end_time])

                        time_delta = []

                        for i in range(len(self.price)):
                            time_decider = f'T_{house}_{machine_id}_{n_job}_{n_op}_{i}'
                            time_delta.append(
                                self.variables[time_decider] * self.price[i][2])

                            self.solver.Add(- M * (
                                1 - self.variables[time_decider]) <= self.variables[start_time] - self.price[i][0])
                            self.solver.Add(self.variables[start_time] - self.price[i][0] <= M * (
                                1 - self.variables[time_decider]))

                            self.solver.Add(- M * (
                                1 - self.variables[time_decider]) <= self.variables[end_time] - self.price[i][1])
                            self.solver.Add(self.variables[end_time] - self.price[i][1] <= M * (
                                1 - self.variables[time_decider]))

                        job_costs.append(
                            duration * self.solver.Sum(time_delta))

        self.solver.Minimize(self.solver.Sum(job_costs))

    def solve(self):
        self.add_variables()
        self.add_constraints()

        status = self.solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            for house in self.env.S:
                for machine_id in self.env.S[house]:
                    for machine in self.env.S[house][machine_id]:
                        for job in machine.jobs:
                            duration, _, job_id = job
                            _, _, n_job, n_op = job_id
                            start_time = f'S_{house}_{machine_id}_{n_job}_{n_op}'
                            end_time = f'E_{house}_{machine_id}_{n_job}_{n_op}'
                            self.schedule_list.append(
                                Schedule(job_id, machine_id, self.variables[start_time].solution_value(), self.variables[end_time].solution_value()))
        else:
            raise Exception('The problem does not have an optimal solution.')

from random import randint
from copy import deepcopy
from .base import Solver, Schedule
from ortools.algorithms import pywrapknapsack_solver


class BSKnapsackSolver(Solver):
    def __init__(self, env, price):
        super().__init__(env, price,  'Binary Search + Knapsack')

        # Create the solver.
        self.solver = pywrapknapsack_solver.KnapsackSolver(
            pywrapknapsack_solver.KnapsackSolver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'BSKnapsackSolver')

    def knapsack(self, S, T, cost_cap):
        # Create the solver environment
        def toInt(x):
            return int(x * 1000)

        power_cap = self.price.cost_to_power(T, cost_cap)

        values = []
        weights = [[]]
        job_id = [[]]
        LIM = 10**-9

        for house in S:
            for machine_id in S[house]:
                for i, machine in enumerate(S[house][machine_id]):
                    # If machine is busy, skip
                    if machine.is_busy(T):
                        power_cap -= machine.get_power(T)
                        continue

                    # If machine has no jobs, skip
                    if machine.remaining_jobs == 0:
                        continue

                    # Get the job
                    job = machine.peek()
                    duration, power, deadline, _ = job

                    if T + duration > deadline:  # self.env.day:
                        continue

                    values.append(
                        int(1 / max(LIM, (deadline - T) ** 4) * (10 ** 5)))
                    weights[0].append(toInt(power))
                    job_id[0].append((house, machine_id, i))

        if power_cap < 0:
            return []

        # if len(values) > 1:
        #     for i in range(200):
        #         x = randint(0, len(values)-2)
        #         y = randint(x+1, len(values)-1)

        #         values[x], values[y] = values[y], values[x]
        #         weights[0][x], weights[0][y] = weights[0][y], weights[0][x]
        #         job_id[0][x], job_id[0][y] = job_id[0][y], job_id[0][x]

        capacity = [toInt(power_cap)]
        packed_items = []
        self.solver.Init(values, weights, capacity)

        self.solver.Solve()
        for i in range(len(values)):
            if self.solver.BestSolutionContains(i):
                packed_items.append(job_id[0][i])

        return packed_items

    def check(self, cost_cap, debug=False):
        T = self.env.day
        S = deepcopy(self.env.S)
        self.schedule_list = []
        self.cost = 0

        if debug:
            print(self.price)

        for t in range(T):
            for house, machine_id, machine_n in self.knapsack(S, t, cost_cap):
                machine = S[house][machine_id][machine_n]

                job = machine.pop()
                duration, power, _, job_id = job

                # Schedule the job
                self.schedule_list.append(
                    Schedule(job_id, machine_id, t, t + duration))

                # Set the machine busy
                machine.set_busy(t + duration)

                # Set the machine power usage
                machine.set_power(power)

            power_usage = 0
            for house in S:
                for machine_id in S[house]:
                    for machine in S[house][machine_id]:
                        power_usage += machine.get_power(t)
            self.cost += self.price(t) * power_usage
            if debug:
                print(t, power_usage, self.price(t))

        return len(self.schedule_list) == self.total_jobs

    def solve(self):

        # binary search on per unit time cost
        low = 0
        high = 10**9

        while low < high:
            mid = (low + high) // 2
            if self.check(mid):
                high = mid
            else:
                low = mid + 1

        print('            OPTIMAL CPUT: ', low)
        _ = self.check(low, debug=False)

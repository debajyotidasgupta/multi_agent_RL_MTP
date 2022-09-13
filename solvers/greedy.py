from .base import Solver, Schedule


class GreedySolver(Solver):
    def __init__(self, env):
        super().__init__(env, 'Greedy (FCFS)')

    def solve(self):
        pass

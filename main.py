import yaml
from utils import *
from solvers import *
from pprint import pprint

if __name__ == '__main__':
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    step = config['step']
    building = config['building']
    machines = config['machines']
    price_list = config['price_list']
    job_list = config['job_list']
    day = config['day'] // step

    price = Price(price_list, step)
    job = Job(job_list, step)
    env = Env(building, job, machines, day)

    solvers = [
        BSKnapsackSolver,
        GreedySolver,
        MIPSolver,
    ]

    for solver in solvers:
        env.reset(building, job, machines, day)
        solver = solver(env, price)
        solver.solve()
        print(solver)
        # print(solver.scehdule())

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
    day = config['day'] / step

    price = Price(price_list, step)
    job = Job(job_list, step)
    env = Env(building, job, price, machines, day)

    solvers = [
        # BSKnapsackSolver,
        GreedySolver,
    ]

    for solver in solvers:
        env.reset(building, job, price, machines, day)
        solver = solver(env)
        solver.solve()
        print(solver)

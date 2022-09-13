from .base import Solver, Schedule


class GreedySolver(Solver):
    def __init__(self, env, price):
        super().__init__(env, price, 'Greedy (FCFS)')

    def solve(self):
        T = self.env.day

        S = self.env.S
        for t in range(T):
            power_usage = 0

            for house in S:
                for machine_id in S[house]:
                    for machine in S[house][machine_id]:

                        # If machine is not busy at the moment
                        if not machine.is_busy(t):

                            # If there are jobs left
                            if machine.remaining_jobs > 0:

                                # Get the job
                                job = machine.pop()
                                duration, power, job_id = job

                                # Schedule the job
                                self.schedule_list.append(
                                    Schedule(job_id, machine_id, t, t + duration))

                                # Set the machine busy
                                machine.set_busy(t + duration)

                                # Set the machine power usage
                                machine.set_power(power)

                        # Add the power usage at the current time
                        power_usage += machine.get_power(t)

            self.cost += self.price(t) * power_usage

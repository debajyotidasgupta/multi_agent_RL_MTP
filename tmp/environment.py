import gym
import numpy as np
from gym import spaces
from copy import deepcopy
from random import randint
from matplotlib import pyplot as plt
import streamlit as st


class Job:
    def __init__(self, power, time, type_mc, name):
        '''
        Parameters
        ----------
        power: unit of power the process will consume,per unit time
        time : duration of the process (in minutes)
        '''
        self.id = randint(1, 10**5)
        self.name = name
        self.power = power
        self.type_mc = type_mc
        self.time = time

    def allocate(self, time, machine):
        '''
        Parameters
        ----------
        time: time to be allocated to the job
        machine: machine to be allocated to the job
        '''
        self.time = time
        self.machine = machine


class SmartApplEnv(gym.Env):
    def __init__(self,
                 number_of_machines,  # list of length same as number of different types of devices
                 number_of_jobs,     # list of length same as number of different types of devices
                 distinct_machines,
                 power_rate_chart,
                 full_day,
                 time_per_unit,
                 cycle_stat=None):

        self._state = np.zeros((max(number_of_jobs), max(
            number_of_machines), distinct_machines))
        self.action_space = spaces.Discrete(
            1+int(pow(2, max(number_of_machines))*pow(2, distinct_machines)))
        self.observation_space = spaces.Box(
            low=-1e20, high=1e20, shape=self._state.shape)

        self._episode_ended = False

        # Parameters related to different data statistics
        self.all_list = [[] for _ in range(distinct_machines)]
        self.job_list = [[] for _ in range(distinct_machines)]
        self.full_day = full_day
        self.time_per_unit = time_per_unit
        self.power_rate_chart = power_rate_chart

        self.max_jobs = number_of_jobs
        self.max_machines = number_of_machines
        self.distinct_machines = distinct_machines
        self.number_of_jobs = np.array(number_of_jobs).astype(np.int32)
        self.number_of_machines = np.array(number_of_machines).astype(np.int32)

        self.schedule_list = []
        self.power_usage = []
        self.cost_chart = []

        if cycle_stat != None:
            for m in range(distinct_machines):
                self.add_job(number_of_jobs[m], cycle_stat[m], m)
        _ = self.reset()

    def add_machine(self, machine):
        # correct this later
        machine_id = self.distinct_machines
        self.distinct_machines += 1
        return machine_id

    def add_job(self, num_jobs, cycle_stat, machine, set_val=False):
        # maxhine = 0 / 1 / 2

        for _ in range(num_jobs):
            self.all_list[machine].append([])
            self.job_list[machine].append([])
            if set_val:
                self.number_of_jobs[machine] += 1

            for cycle in cycle_stat:
                self.all_list[machine][-1].append(
                    Job(cycle['power'],
                        (cycle['time'] + self.time_per_unit -
                         1) // self.time_per_unit,
                        machine,
                        cycle['cycle']))

                self.job_list[machine][-1].append(
                    Job(cycle['power'],
                        (cycle['time'] + self.time_per_unit -
                         1) // self.time_per_unit,
                        machine,
                        cycle['cycle']))

    def amount_for_bill(self, power):
        amount = 0
        pos = -1
        # Get the time of the day when the scheduling is currently being done in the power stat chart
        for time_limit in sorted(self.power_rate_chart, reverse=True):
            if time_limit < self.time:
                break
            pos = time_limit

        # Get the power rate for the current time
        amount = self.power_rate_chart[pos]['cost'] * \
            power * self.time_per_unit

        # If the power consumption crosses the threshold, then the penalization is applied
        if power > self.power_rate_chart[pos]['limit']:
            amount += (power - self.power_rate_chart[pos]['limit']) * \
                self.power_rate_chart[pos]['penalty'] * self.time_per_unit
        return amount

    def generate_state_encoding(self):
        MN, MX = -300, 0
        image = np.zeros(self._state.shape, dtype=np.float32)

        pos = -1
        # Get the time of the day when the scheduling is currently being done in the power stat chart
        for time_limit in sorted(self.power_rate_chart, reverse=True):
            if time_limit < self.time:
                break
            pos = time_limit

        for m in range(self.distinct_machines):
            for i in range(self.number_of_jobs[m]):
                for j in range(self.number_of_machines[m]):
                    if self.machine_free_time[m, j] <= self.time\
                            and self.job_free_time[m, i] <= self.time\
                            and (self.job_allocation_list[m, i] == -1 or
                                 self.job_allocation_list[m, i] == j)\
                            and (self.machine_allocation_list[m, j] == -1 or
                                 self.machine_allocation_list[m, j] == i)\
                            and len(self.job_list[m][i]) > 0:

                        image[i, j, m] = self.job_list[m][i][0].power -\
                            self.power_rate_chart[pos]['limit']
                        # another idea can be to use the get_cost  method

                        MX = max(MX, image[i, j, m])
                    else:
                        image[i, j, m] = MN
        # plt.imshow(image, cmap="hot")
        return image / max(1, MX)  # changed this line

    def reset(self):
        # Make the job list from the data of the cycles on machines
        self.job_list = deepcopy(self.all_list)

        # parameters describing the state of the environment
        self.time = 0
        self.schedule_list = []
        self.cost_chart = []
        self.power_usage = []

        self.machine_free_time = np.zeros(
            (self.distinct_machines, np.max(self.number_of_machines)), dtype=np.int32)
        self.job_free_time = np.zeros(
            (self.distinct_machines, np.max(self.number_of_jobs)),     dtype=np.int32)
        self.machine_allocation_list = np.zeros(
            (self.distinct_machines, np.max(self.number_of_machines)), dtype=np.int32) - 1
        self.job_allocation_list = np.zeros(
            (self.distinct_machines, np.max(self.number_of_jobs)),     dtype=np.int32) - 1

        self.bill = 0
        self._state = self.generate_state_encoding()
        self._episode_ended = False
        # print(self._state.shape)
        return self._state

    def schedule(self, machine, action):
        power, reward = 0, 0

        for m in range(self.distinct_machines):
            for i in range(self.number_of_machines[m]):
                if action & (1 << i):
                    if self.machine_free_time[m, i] <= self.time:
                        if self.machine_allocation_list[m, i] == -1:
                            for j in range(self.number_of_jobs[m]):
                                if self.job_free_time[m, j] == 0:
                                    self.machine_allocation_list[m, i] = j
                                    self.job_allocation_list[m, j] = i

                                    reward += 20000.
                                    break

                        job = self.machine_allocation_list[m, i]
                        if job == -1:
                            continue

                        self.schedule_list.append({
                            'time': self.time,
                            'type': m,
                            'mc_id': i,
                            'job_id': job,
                        })
                        self.job_free_time[m][job] += self.job_list[m][job][0].time
                        self.machine_free_time[m][i] += self.job_list[m][job][0].time
                        power += self.job_list[m][job][0].power

                        # reward += 10. * self.job_list[m][job][0].time
                        self.job_list[m][job].pop(0)

                        if len(self.job_list[m][job]) == 0:
                            reward += 100000.
                            self.machine_allocation_list[m, i] = -1
                            self.job_allocation_list[m, job] = -1
                    else:
                        reward -= 15000.
        return power, reward

    def step(self, action):
        if self._episode_ended:
            return self.reset()

        # actions += 1
        reward, done, info = -100., False, {}  # make 10. -> 100.
        power = 0

        for machine in range(self.distinct_machines):
            if action < self.action_space.n - 1:
                mask = action % int(pow(2, self.number_of_machines[machine]))
                action = action // int(pow(2,
                                       self.number_of_machines[machine]))
                cur_pow, cur_rew = self.schedule(machine, mask)
                power += cur_pow
                reward += cur_rew

            for i in self.job_list[machine]:
                reward -= len(i) * 1000.  # make this 1000.

        reward -= self.amount_for_bill(power) * 10000.
        self.bill += self.amount_for_bill(power)

        self.power_usage.append(power)
        self.cost_chart.append(self.bill)

        self.time += 1
        if self.time == self.full_day:
            done = True

        self._state = self.generate_state_encoding()
        self._episode_ended = done
        info = {}

        return self._state, reward, self._episode_ended, info

    def render(self, args):
        fig, ax = plt.subplots(1, 3, figsize=(5, 5))
        for i in range(self._state.shape[2]):
            ax[i].imshow(self._state[:, :, i])
            ax[i].grid(False)
        st.pyplot(fig)

class SmartHouse(gym.Env):
    def __init__(self, args, data):
        self.args = args
        self.data = data
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=0, high=1, shape=(1, 1, 1))
        self.reset()

    def reset(self):
        self._state = np.zeros((1, 1, 1))
        self._episode_ended = False
        return self._state

    def step(self, action):
        if self._episode_ended:
            return self.reset()

        reward, done, info = 0, False, {}
        self._state = np.zeros((1, 1, 1))
        self._episode_ended = done
        info = {}

        return self._state, reward, self._episode_ended, info

    def render(self, args):
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))
        ax.imshow(self._state[:, :, 0])
        ax.grid(False)
        st.pyplot(fig)
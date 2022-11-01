import functools
from gym.spaces import Discrete, Box, MultiBinary
from pettingzoo import ParallelEnv
from pettingzoo.test import api_test
from pettingzoo.utils import wrappers
from pettingzoo.utils import parallel_to_aec, aec_to_parallel
from ..env import Env

MOVES = []
NUM_ITERS = 100
REWARD_MAP = {}


class parallel_env(ParallelEnv):
    metadata = {'render_modes': ['human'], "name": "Smart Grid V1"}

    def __init__(self, base_env: Env):
        '''
        The init method takes in environment arguments and should define the following attributes:
        - possible_agents
        - action_spaces
        - observation_spaces

        These attributes should not be changed after initialization.
        '''
        self.possible_agents = [f"house_{r}" for r in range(base_env.n_houses)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents)))))

        for h_num in range(base_env.n_houses):
            MOVES.append(base_env.houses[h_num].move)
            REWARD_MAP[(h_num, h_num)] = (
                base_env.houses[h_num].reward, base_env.houses[h_num].reward)

    # this cache ensures that same space object is returned for the same agent
    # allows action space seeding to work as expected
    @ functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces
        return Discrete(4)

    @ functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(3)

    def render(self, mode="human"):
        '''
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        '''
        if len(self.agents) == 2:
            string = ("Current state: Agent1: {} , Agent2: {}".format(
                MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]))
        else:
            string = "Game over"
        print(string)

    def close(self):
        '''
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        '''
        pass

    def reset(self):
        '''
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.

        Here it initializes the `num_moves` variable which counts the number of
        hands that are played.

        Returns the observations for each agent
        '''
        self.agents = self.possible_agents[:]
        self.num_moves = 0
        observations = {agent: NONE for agent in self.agents}
        return observations

    def step(self, actions):
        '''
        step(action) takes in an action for each agent and should return the
        - observations
        - rewards
        - dones
        - infos
        dicts where each dict looks like {agent_1: item_1, agent_2: item_2}
        '''
        # If a user passes in actions with no agents, then just return empty observations, etc.
        if not actions:
            self.agents = []
            return {}, {}, {}, {}

        # rewards for all agents are placed in the rewards dictionary to be returned
        rewards = {}
        rewards[self.agents[0]], rewards[self.agents[1]] = REWARD_MAP[(
            actions[self.agents[0]], actions[self.agents[1]])]

        self.num_moves += 1
        env_done = self.num_moves >= NUM_ITERS
        dones = {agent: env_done for agent in self.agents}

        # current observation is just the other player's most recent action
        observations = {self.agents[i]: int(
            actions[self.agents[1 - i]]) for i in range(len(self.agents))}

        # typically there won't be any information in the infos, but there must
        # still be an entry for each agent
        infos = {agent: {} for agent in self.agents}

        if env_done:
            self.agents = []

        return observations, rewards, dones, infos


env = env()
api_test(env, num_cycles=1000, verbose_progress=False)

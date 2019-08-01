"""
Wrapper around a gym env that provides convenience functions
"""

import gym
import numpy as np


class EnvSpec(object):
    def __init__(self, obs_dim, act_dim, horizon):
        self.observation_dim = obs_dim
        self.action_dim = act_dim
        self.horizon = horizon


class GymEnv(object):
    def __init__(self, env_name):
        env = gym.make(env_name)
        self.env = env
        self.env_id = env.spec.id

        try:
            self._horizon = env.spec.max_episode_steps
        except AttributeError:
            self._horizon = env.spec._horizon

        try:
            self._action_dim = self.env.env.action_dim
        except AttributeError:
            self._action_dim = self.env.action_space.shape[0]

        try:
            self._observation_dim = self.env.env.obs_dim
        except AttributeError:
            self._observation_dim = self.env.observation_space.shape[0]

        # Specs
        self.spec = EnvSpec(self._observation_dim, self._action_dim, self._horizon)

    @property
    def action_dim(self):
        return self._action_dim

    @property
    def observation_dim(self):
        return self._observation_dim

    @property
    def observation_space(self):
        return self.env.observation_space

    @property
    def action_space(self):
        return self.env.action_space

    @property
    def horizon(self):
        return self._horizon

    def reset(self, seed=None):
        try:
            self.env._elapsed_steps = 0
            return self.env.env.reset_model(seed=seed)
        except:
            return self.env.reset()

    def reset_model(self, seed=None):
        # overloading for legacy code
        return self.reset(seed)

    def step(self, action):
        return self.env.step(action)

    def render(self):
        try:
            self.env.env.mujoco_render_frames = True
            self.env.env.mj_render()
        except:
            self.env.render()

    def set_seed(self, seed=123):
        try:
            self.env.seed(seed)
        except AttributeError:
            self.env._seed(seed)

    def get_obs(self):
        try:
            return self.env.env._get_obs()
        except:
            return self.env.env.get_obs()

    def get_env_infos(self):
        try:
            return self.env.env.get_env_infos()
        except:
            return {}

    # ===========================================
    # Trajectory optimization related
    # Envs should support these functions in case of trajopt

    def get_env_state(self):
        try:
            return self.env.env.get_env_state()
        except:
            raise NotImplementedError

    def set_env_state(self, state_dict):
        try:
            self.env.env.set_env_state(state_dict)
        except:
            raise NotImplementedError

    def real_env_step(self, bool_val):
        try:
            self.env.env.real_step = bool_val
        except:
            raise NotImplementedError

    # ===========================================

    def visualize_policy(self, policy, horizon=1000, num_episodes=1, mode='exploration'):
        try:
            self.env.env.visualize_policy(policy, horizon, num_episodes, mode)
        except:
            for ep in range(num_episodes):
                o = self.reset()
                d = False
                t = 0
                while t < horizon and d is False:
                    a = policy.get_action(o)[0] if mode == 'exploration' else policy.get_action(o)[1]['evaluation']
                    o, r, d, _ = self.step(a)
                    self.render()
                    t = t+1

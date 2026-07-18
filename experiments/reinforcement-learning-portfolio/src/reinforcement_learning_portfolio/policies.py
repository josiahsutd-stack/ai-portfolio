from __future__ import annotations

import random
from collections.abc import Callable


def random_policy(state: dict[str, float]) -> int:
    return random.choice([0, 5, 10, 15, 20])


def heuristic_inventory_policy(state: dict[str, float]) -> int:
    return 25 if float(state.get("inventory", 0)) < 20 else 5


def evaluate_policy(
    env, policy: Callable[[dict[str, float]], int], episodes: int = 5
) -> dict[str, float]:
    rewards = []
    stockouts = 0
    for _episode in range(episodes):
        state = env.reset()
        total = 0.0
        done = False
        while not done:
            state, reward, done, info = env.step(policy(state))
            total += reward
            stockouts += int(info.get("stockout", 0) > 0)
        rewards.append(total)
    return {
        "average_reward": round(sum(rewards) / len(rewards), 3),
        "episode_success_rate": round(sum(1 for reward in rewards if reward > 0) / len(rewards), 3),
        "stockout_events": stockouts,
    }

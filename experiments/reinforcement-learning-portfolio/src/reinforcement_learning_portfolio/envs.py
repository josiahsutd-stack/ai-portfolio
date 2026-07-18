from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class WarehouseInventoryEnv:
    seed: int = 7
    max_inventory: int = 80
    target_inventory: int = 35

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.day = 0
        self.inventory = self.target_inventory

    def reset(self) -> dict[str, int]:
        self.day = 0
        self.inventory = self.target_inventory
        return {"day": self.day, "inventory": self.inventory}

    def step(self, action: int) -> tuple[dict[str, int], float, bool, dict[str, float]]:
        reorder = max(0, min(30, int(action)))
        demand = self.rng.randint(12, 32)
        self.inventory = min(self.max_inventory, self.inventory + reorder)
        sold = min(self.inventory, demand)
        stockout = max(0, demand - self.inventory)
        self.inventory -= sold
        holding_cost = self.inventory * 0.08
        order_cost = reorder * 0.2
        stockout_cost = stockout * 2.5
        reward = sold * 1.5 - holding_cost - order_cost - stockout_cost
        self.day += 1
        done = self.day >= 30
        return (
            {"day": self.day, "inventory": self.inventory},
            round(reward, 3),
            done,
            {"demand": demand, "stockout": stockout, "holding_cost": holding_cost},
        )


@dataclass
class DynamicPricingEnv:
    seed: int = 11
    inventory: int = 120
    competitor_price: float = 10.0

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.day = 0
        self.price = 10.0

    def reset(self) -> dict[str, float]:
        self.day = 0
        self.inventory = 120
        self.price = 10.0
        return {"day": self.day, "inventory": self.inventory, "price": self.price}

    def step(self, action: int) -> tuple[dict[str, float], float, bool, dict[str, float]]:
        self.price = max(5.0, min(18.0, self.price + float(action)))
        demand = max(0, int(38 - 2.1 * self.price + self.rng.gauss(0, 3)))
        sold = min(self.inventory, demand)
        self.inventory -= sold
        margin = self.price - 4.0
        instability_penalty = abs(float(action)) * 1.2
        reward = sold * margin - instability_penalty
        self.day += 1
        done = self.day >= 30 or self.inventory <= 0
        return (
            {"day": self.day, "inventory": self.inventory, "price": self.price},
            round(reward, 3),
            done,
            {"demand": demand, "sold": sold, "profit": sold * margin},
        )

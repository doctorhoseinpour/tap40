from __future__ import annotations
from typing import List, Set, Callable
from datetime import datetime, timedelta
from functools import reduce
import logging


class Action:
    def __init__(self, description: str, created_at: datetime, price: float):
        self.name = description
        self.created_at = created_at
        self.price = price
        self.finished_at = None

    def finish(self, finished_at: datetime = datetime.now()):
        self.finished_at = finished_at


class DrivingAction(Action):
    def __init__(self, description: str, created_at: datetime, customer_name: str, price: float):
        """
        for this limited model we define actions in a way that Drivers own these actions, but in a real life model
        the implementation will differ in a way that these actions will refer to drivers and customers
        """
        super().__init__(description, created_at, price)
        self.customer_name = customer_name

    def finish(self, finished_at: datetime = datetime.now()):
        super(DrivingAction, self).finish(finished_at)
        return self.price


class DeliveryAction(Action):
    # other type of actions can be implemented...
    pass


class Award:
    def __init__(self, name: str, created_at: datetime):
        self.name = name
        self.created_at = created_at
        self.awarded_at = None

    def award_to_driver(self, driver: Driver, awarded_at: datetime):
        self.awarded_at = awarded_at
        raise NotImplementedError


class CashAward(Award):
    def __init__(self, name: str, created_at: datetime, value: float):
        super().__init__(name, created_at)
        self.value = value

    def award_to_driver(self, driver: Driver, awarded_at: datetime):
        super().award_to_driver(driver, awarded_at)
        driver.change_balance(self.value)


class VoucherAward(Award):
    def __init__(self, name: str, created_at: datetime, value: float):
        super().__init__(name, created_at)
        self.value = value

    def award_to_driver(self, driver: Driver, awarded_at: datetime):
        super().award_to_driver(driver, awarded_at)
        driver.add_voucher(self)


class Driver:
    _drivers: Set[Driver] = set()

    @classmethod
    def get_all_drivers(cls) -> Set[Driver]:
        return cls._drivers

    def __init__(self, driver_id: str, name: str, phone_number: str, active_missions: Set[Mission],
                 action_history: List[Action], account_balance: float):
        self.driver_id = driver_id
        self.name = name
        self.phone_number = phone_number
        self.active_missions = active_missions
        self.completed_missions = set()
        self.action_history = action_history
        self.account_balance = account_balance
        self.vouchers: List[VoucherAward] = []

        Driver._drivers.add(self)

    def __del__(self):
        Driver._drivers.remove(self)

    def add_voucher(self, voucher: VoucherAward):
        self.vouchers.append(voucher)

    def change_balance(self, amount: float):
        self.account_balance += amount

    def accept_mission(self, mission: Mission):
        if datetime.now() > mission.deadline:
            raise Exception('too late!')
        self.active_missions.add(mission)

    def delete_mission(self, mission: Mission):
        self.active_missions.remove(mission)
        self.completed_missions.add(mission)

    def action_done(self, action: Action, time: datetime = datetime.now()):
        pay = action.finish(time)
        # assuming pay is only cash (so float)
        self.account_balance += pay
        self.action_history.append(action)

        self.check_for_completed_mission()

    def check_for_completed_mission(self):
        for mis in self.active_missions:
            if mis.has_met_expectations(
                    list(filter(lambda x: x.created_at >= mis.from_time and x.finished_at <= mis.deadline,
                                self.action_history))):
                mis.mission_completed(self)
                logging.info(f'missions {mis.mission_id} has been completed by driver: {self.name}')


class Mission:
    _missions: Set[Mission] = set()

    @classmethod
    def get_all_missions(cls):
        return cls._missions

    def __init__(self, mission_id: str, title: str, description: str, awards: List[Award], from_time: datetime,
                 deadline: datetime, expectations: Callable[[List[Action]], bool]):
        self.mission_id = mission_id,
        self.title = title
        self.description = description
        self.awards = awards
        self.from_time = from_time
        self.deadline = deadline
        self.expectations = expectations

        Mission._missions.add(self)

    def __del__(self):
        Mission._missions.remove(self)

    def mission_completed(self, driver: Driver, completed_at: datetime = datetime.now()):
        if completed_at > self.deadline:
            raise Exception('too late!')

        for award in self.awards:
            award.award_to_driver(driver, completed_at)
        driver.delete_mission(self)

    def has_met_expectations(self, actions: List[Action]) -> bool:
        return self.expectations(actions)


the_awards = [CashAward('award_name_woe', datetime.now(), 10000.0)]


def mission_expectation(actions: List[Action]) -> bool:
    # checks if income from the actions is greater than 100000.0 T
    return reduce(lambda x, a: a + x.price, map(lambda x: x.price, actions)) >= 100000.0


def counting_expectation(actions: List[Action]) -> bool:
    # checks if has done 10 or more Driving actions
    return len([i for i in actions if isinstance(i, DrivingAction)]) >= 10


the_mission = Mission(
    '1234', 'asghar', 'asghar kachale why why', the_awards, from_time=datetime.now(),
    deadline=datetime.now() + timedelta(days=1),
    expectations=mission_expectation
)

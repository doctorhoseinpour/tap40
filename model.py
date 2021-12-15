from __future__ import annotations
from typing import List, Set
from datetime import date, datetime


class Action:
    def __init__(self, name: str, created_at: datetime):
        self.name = name
        self.created_at = created_at
        self.finished_at = None

    def finish(self, finished_at: datetime = datetime.now()):
        self.finished_at = finished_at


class DrivingAction(Action):
    def __init__(self, name: str, created_at: datetime, customer_name: str, price: float):
        """
        for this limited model we define actions in a way that Drivers own these actions, but in a real life model
        the implementation will differ in a way that these actions will refer to drivers and customers
        """
        super().__init__(name, created_at)
        self.customer_name = customer_name
        self.price = price

    def finish(self, finished_at: datetime = datetime.now()):
        super(DrivingAction, self).finish(finished_at)
        return self.price


class Award:

    def __init__(self, name: str, created_at: date, awarded_at: date):
        self.name = name
        self.created_at = created_at
        self.awarded_at = awarded_at

    def award_to_driver(self, driver: Driver):
        raise NotImplementedError


class CashAward(Award):
    def __init__(self, name: str, created_at: date, awarded_at: date, value: float):
        super().__init__(name, created_at, awarded_at)
        self.value = value

    def award_to_driver(self, driver: Driver):
        driver.account_balance += self.value


class VoucherAward(Award):
    def __init__(self, name: str, created_at: date, awarded_at: date, value: float):
        super().__init__(name, created_at, awarded_at)
        self.value = value

    def award_to_driver(self, driver: Driver):
        driver.vouchers.append(self)


class Driver:
    _drivers: Set[Driver] = set()

    def __init__(self, driver_id: str, name: str, phone_number: str, active_missions: List[str],
                 action_history: List[Action], account_balance: float):
        self.driver_id = driver_id
        self.name = name
        self.phone_number = phone_number
        self.active_missions = active_missions
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


class Mission:
    def __init__(self, mission_id: str, title: str, description: str, awards: List[Award]):
        self.mission_id = mission_id,
        self.title = title
        self.description = description
        self.awards = awards

    def mission_completed(self, driver: Driver):
        for award in self.awards:
            award.award_to_driver(driver)

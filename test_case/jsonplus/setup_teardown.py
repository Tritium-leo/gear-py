import unittest

import datetime
from typing import *

pres_datatime = datetime.datetime.fromtimestamp(1656651105.609446)
pres_data = datetime.date.fromtimestamp(1656604800.0)


class SetupTeardown(unittest.TestCase):
    data: Dict[str, Any] = {
        "a": 123,
        "b": "bc",
        "c": pres_datatime,
        "d": pres_data,
        "e": {"g": "ge"},
        "f": ["123", "456"],
        "g": True
    }

    data_str = '{"a": 123, "b": "bc", "c": {"__class__": "datetime", "timestamp": "1656651105.609446"}, "d": {"__class__": "date", "timestamp": "1656604800.0"}, "e": {"g": "ge"}, "f": ["123", "456"], "g": true}'

    def setUp(self) -> None:
        print("setup")
        pass

    def tearDown(self) -> None:
        print("tearDown")
        pass

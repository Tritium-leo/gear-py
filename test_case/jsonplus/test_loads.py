from pkg import jsonplus

from test_case.jsonplus.setup_teardown import SetupTeardown


class TestLoads(SetupTeardown):

    def test_loads(self):
        self.assertEqual(self.data, jsonplus.loads(self.data_str))

from pkg import jsonplus

from test_case.jsonplus.setup_teardown import SetupTeardown


class TestDumps(SetupTeardown):

    def test_dumps(self):
        self.assertEqual(self.data_str, jsonplus.dumps(self.data))

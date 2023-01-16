from pkg.fake_operator.src.main import FileFaker, DirFaker
from root import PROJECT_ROOT
from .setup_teardown import SetupTeardown


class TestFileFaker(SetupTeardown):

    def test_fake(self):
        FileFaker.fake()
        ...


class TestDirFaker(SetupTeardown):

    def test_fake(self):
        root = PROJECT_ROOT.joinpath()
        DirFaker.fake(root, )

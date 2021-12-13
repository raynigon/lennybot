

class IAction:

    @property
    def application(self) -> str:
        pass

    @property
    def target_version(self) -> str:
        pass

    def run(self):
        pass
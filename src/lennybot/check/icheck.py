class ICheck:

    @property
    def application(self) -> str:
        pass

    @property
    def source_version(self) -> str:
        pass

    @property
    def target_version(self) -> str:
        pass

    def check(self) -> bool:
        pass

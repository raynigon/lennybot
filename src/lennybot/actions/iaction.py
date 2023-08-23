class IAction:
    @property
    def application(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    @property
    def source_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    @property
    def target_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    def run(self):
        pass

class IAction:
    @property
    def application(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    @property
    def source_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    @property
    def target_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    def run(self):
        pass

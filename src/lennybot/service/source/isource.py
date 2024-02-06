class ISource:
    @property
    def application(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    def latest_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

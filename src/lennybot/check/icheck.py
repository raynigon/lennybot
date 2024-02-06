class ICheck:
    @property
    def application(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    @property
    def source_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    @property
    def target_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

    def check(self) -> bool:  # pyright: ignore [reportGeneralTypeIssues, reportReturnType]
        pass

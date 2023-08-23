class ICheck:
    @property
    def application(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    @property
    def source_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    @property
    def target_version(self) -> str:  # pyright: ignore [reportGeneralTypeIssues]
        pass

    def check(self) -> bool:  # pyright: ignore [reportGeneralTypeIssues]
        pass

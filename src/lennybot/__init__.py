from .lennybot import LennyBot
import sys

def main() -> int:
    app = LennyBot("test/config.yaml")
    plan = app.plan()
    #result = app.apply(plan)

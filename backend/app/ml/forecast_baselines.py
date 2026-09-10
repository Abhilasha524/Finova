"""
Naive forecasting baselines - deliberately simple, used as an honesty check
against Holt-Winters. If a sophisticated model can't beat these, that's a
real finding worth reporting, not something to hide.

Both classes expose .forecast(periods) so predict.py can call whichever
winning model was saved without needing to know or care which type it is.
"""
import pandas as pd


class NaiveLastValueForecaster:
    """Predicts every future month as equal to the most recent known month."""

    def __init__(self, last_value: float):
        self.last_value = last_value

    def forecast(self, periods: int) -> pd.Series:
        return pd.Series([self.last_value] * periods)


class NaiveMovingAverageForecaster:
    """Predicts every future month as the average of the last N known months."""

    def __init__(self, average_value: float, window: int):
        self.average_value = average_value
        self.window = window

    def forecast(self, periods: int) -> pd.Series:
        return pd.Series([self.average_value] * periods)
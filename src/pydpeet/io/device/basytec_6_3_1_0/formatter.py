import pandas as pd

from pydpeet.io.utils.formatter_utils import _round_testtime, _testtime_hours_to_seconds_direct


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a pandas DataFrame and applies two functions to it:

    1. `testtime_hours_to_seconds_direct`: converts the "Test_Time[s]" column from hours to seconds with string interpretation.
    2. `round_testtime`: rounds the "Test_Time[s]" column down to the nearest second.

    Returns the modified DataFrame.
    """
    df = _testtime_hours_to_seconds_direct(df)
    df = _round_testtime(df)

    return df

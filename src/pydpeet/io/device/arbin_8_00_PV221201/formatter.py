import pandas as pd

from pydpeet.io.utils.formatter_utils import (
    _absolute_time_timedate_typecast,
    _testtime_hours_to_seconds_with_string_interpretation,
)


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the given DataFrame into a standard format.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        The formatted DataFrame
    """
    df = _testtime_hours_to_seconds_with_string_interpretation(df, True)
    df = _absolute_time_timedate_typecast(df)

    return df

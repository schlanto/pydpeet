import pandas as pd

from pydpeet.io.utils.formatter_utils import (
    _absolute_time_timedate_typecast,
    _testtime_hours_to_seconds_with_string_interpretation,
    _typecast,
)


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame from a Neware cycler into a standard format.

    The DataFrame is modified in-place.

    Parameters
    ----------
    data_frame : pd.DataFrame
        DataFrame to be formatted

    Returns
    -------
    pd.DataFrame
        Formatted DataFrame
    """
    _testtime_hours_to_seconds_with_string_interpretation(df, True)
    df = _absolute_time_timedate_typecast(df)
    _typecast(df, "Step_Count", int)
    _typecast(df, "Temperature[°C]", float)

    return df

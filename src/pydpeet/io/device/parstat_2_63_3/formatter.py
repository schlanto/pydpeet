import pandas as pd

from pydpeet.io.utils.formatter_utils import _round_testtime, _typecast


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the given DataFrame into a standard format.

    This function takes a DataFrame and applies some formatting to it. It rounds the
    "Test_Time[s]" column to 5 decimal places, and typecasts the "Step_Count", "Voltage[V]",
    "Current[A]", "Test_Time[s]", "EIS_f[Hz]", "EIS_Z_Real[Ohm]" and "EIS_Z_Imag[Ohm]" columns to
    int, float, float, float, float, float and float respectively.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame
    """
    df = _round_testtime(df)
    _typecast(df, "Step_Count", int)
    _typecast(df, "Voltage[V]", float)
    _typecast(df, "Current[A]", float)
    _typecast(df, "Test_Time[s]", float)
    _typecast(df, "EIS_f[Hz]", float)
    _typecast(df, "EIS_Z_Real[Ohm]", float)
    _typecast(df, "EIS_Z_Imag[Ohm]", float)

    return df

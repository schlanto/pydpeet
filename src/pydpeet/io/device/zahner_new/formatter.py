import pandas as pd

from pydpeet.io.utils.formatter_utils import _nan_to_none_in_column, _round_testtime, _typecast


def _get_data_into_format_zahner_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Test_Time[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "Step_Count" and "EIS_f[Hz]" columns to int and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    _round_testtime(df)
    _nan_to_none_in_column(df, "Test_Time[s]")
    _typecast(df, "Step_Count", int)
    _typecast(df, "EIS_f[Hz]", float)

    return df


def _get_data_into_format_zahner_2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Test_Time[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "Step_Count", "Voltage[V]", and "Current[A]" columns to int, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    df = _round_testtime(df)
    df = _nan_to_none_in_column(df, "Test_Time[s]")
    _typecast(df, "Step_Count", int)
    _typecast(df, "Voltage[V]", float)
    _typecast(df, "Current[A]", float)

    return df


def _get_data_into_format_zahner_3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Test_Time[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "Step_Count", "Voltage[V]", "Current[A]", and "EIS_f[Hz]" columns to int, float, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    df = _round_testtime(df)
    df = _nan_to_none_in_column(df, "Test_Time[s]")
    _typecast(df, "Step_Count", int)
    _typecast(df, "Voltage[V]", float)
    _typecast(df, "Current[A]", float)
    _typecast(df, "EIS_f[Hz]", float)

    return df

import pandas as pd

from pydpeet.io.utils.formatter_utils import _nan_to_none_in_column, _round_testtime, _typecast


def _get_data_into_format_zahner_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 1.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Test_Time[s]" column is rounded to 5 decimal places.
    - NaN values in the "Test_Time[s]" column are replaced with None.
    - The "Step_Count" column is typecast to int.
    - The "EIS_f[Hz]" column is typecast to float.
    - The "EIS_Z_Real[Ohm]" column is typecast to float.
    - The "EIS_Z_Imag[Ohm]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    df = _round_testtime(df)
    df = _nan_to_none_in_column(df, "Test_Time[s]")
    _typecast(df, "Step_Count", int)
    _typecast(df, "EIS_f[Hz]", float)
    _typecast(df, "EIS_Z_Real[Ohm]", float)
    _typecast(df, "EIS_Z_Imag[Ohm]", float)

    return df


def _get_data_into_format_zahner_2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 2.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Test_Time[s]" column is rounded to 5 decimal places.
    - NaN values in the "Test_Time[s]" column are replaced with None.
    - The "Step_Count" column is typecast to int.
    - The "Voltage[V]" column is typecast to float.
    - The "Current[A]" column is typecast to float.
    - The "Test_Time[s]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    df = _round_testtime(df)
    df = _nan_to_none_in_column(df, "Test_Time[s]")
    _typecast(df, "Step_Count", int)
    _typecast(df, "Voltage[V]", float)
    _typecast(df, "Current[A]", float)
    _typecast(df, "Test_Time[s]", float)

    return df

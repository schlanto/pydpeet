import pandas as pd

from pydpeet.io.utils.formatter_utils import (
    _absolute_time_timedate_typecast,
    _apply_convert_to_float_if_possible,
    _move_strings_from_column_to_metadata,
    _nan_to_none_in_column,
    _replace_empty_with_none_in_standard_columns,
    _round_testtime,
    _typecast,
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
    df = _replace_empty_with_none_in_standard_columns(df)
    _typecast(df, "Step_Count", int)
    df = _apply_convert_to_float_if_possible(df, "Voltage[V]")
    df = _apply_convert_to_float_if_possible(df, "Current[A]")
    df = _round_testtime(df)
    df = _absolute_time_timedate_typecast(df)
    _typecast(df, "EIS_Z_Real[Ohm]", float)
    _typecast(df, "EIS_Z_Imag[Ohm]", float)
    df = _nan_to_none_in_column(df, "Current[A]")
    df = _move_strings_from_column_to_metadata(df, "Voltage[V]")

    return df

import pandas as pd

from pydpeet.io.utils.formatter_utils import _typecast


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame into standard format required by the database.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be formatted.

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame.
    """
    _typecast(df, "Step_Count", int)
    _typecast(df, "EIS_f[Hz]", float)
    _typecast(df, "EIS_Z_Real[Ohm]", float)
    _typecast(df, "EIS_Z_Imag[Ohm]", float)

    return df

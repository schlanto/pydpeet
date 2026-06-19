import inspect
import logging

import numpy as np
import pandas as pd
from scipy import integrate

from pydpeet.process.analyze.configs.battery_config import _BatteryConfigClass
from pydpeet.process.analyze.power import add_power
from pydpeet.process.analyze.utils import (
    _check_columns,
    _StepTimer,
)


def add_cumulative_energy(
    df: pd.DataFrame,
    config: _BatteryConfigClass = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Calculates cumulative energy [Wh] and absolute cumulative energy [Wh] from 'Test_Time[s]' and 'Power[W]' columns.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'Test_Time[s]' and 'Power[W]' columns
    - cumu_energy_method (CumulativeEnergyMethod): Method to use for cumulative energy calculation
    - config (BatteryConfig): Config object containing max and min voltage values

    Returns:
    - pandas.DataFrame: DataFrame with added 'CumulativeEnergy[Wh]' and 'AbsoluteCumulativeEnergy[Wh]' columns

    Notes:
    The 'CumulativeEnergy[Wh]' column represents the cumulative energy (in Wh) with sign (i.e., charge + / discharge -)
    The 'AbsoluteCumulativeEnergy[Wh]' column represents the cumulative absolute energy (in Wh)
    """
    logging.info("Calculating CumulativeEnergy[Wh]...")

    if config is None:
        frame = inspect.currentframe()
        assert frame is not None
        func_name = frame.f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    df_mod = df.copy()
    if "Power[W]" not in df_mod.columns:
        logging.info("Power[W] column missing → adding via add_power.")
        with _StepTimer(verbose) as st:
            df_mod = add_power(df_mod)
            st._log("added Power[W] column")

    with _StepTimer(verbose) as st:
        _check_columns(df_mod, ["Test_Time[s]", "Power[W]"])
        power_values = df_mod["Power[W]"].to_numpy(dtype=float)
        time_values = df_mod["Test_Time[s]"].to_numpy(dtype=float)

        energy = integrate.cumulative_trapezoid(power_values, x=time_values, initial=0) / 3600
        abs_energy = integrate.cumulative_trapezoid(np.abs(power_values), x=time_values, initial=0) / 3600

        df_mod["CumulativeEnergy[Wh]"] = energy
        df_mod["AbsoluteCumulativeEnergy[Wh]"] = abs_energy
        st._log("calculated CumulativeEnergy[Wh] and AbsoluteCumulativeEnergy[Wh]")

    return df_mod

from dataclasses import dataclass
from typing import Optional


@dataclass
class _BatteryConfigClass:
    """Internal battery configuration dataclass.

    Attributes:
        cell_name: Name identifier for the cell type.
        c_ref: Reference capacity in Ah (optional).
        soc_start: Starting state of charge (0-1).
        max_voltage: Maximum cell voltage in V.
        min_voltage: Minimum cell voltage in V.
        threshold_current: Current threshold for analysis.
        voltage_intervall: Voltage interval step size.
        minimal_current_for_capacity: Minimum current threshold for capacity calc.
        maximal_current_for_capacity: Maximum current threshold for capacity calc.
        min_current_diff: Minimum current difference for resistance calculation.
        max_time_diff: Maximum time difference for resistance calculation.
        min_voltage_diff: Minimum voltage difference for resistance calculation.
        ignore_negative_resistance_values: Whether to ignore negative R values.
    """

    cell_name: str
    c_ref: Optional[float]
    soc_start: float
    max_voltage: float
    min_voltage: float
    threshold_current: float
    voltage_intervall: float
    # ----- values for capacity calculation -----
    minimal_current_for_capacity: float
    maximal_current_for_capacity: float
    # ----- values for internal resistance calculation -----
    min_current_diff: float
    max_time_diff: float
    min_voltage_diff: float
    # ignores negative values in internal resistance calculation,
    # should only appear in Neware Cells because of a bug
    ignore_negative_resistance_values: bool


def battery_config_wrapper(
    cell_name: str = "Default",
    c_ref: Optional[float] = 4.8,
    soc_start: float = 0,
    max_voltage: float = 4.2,
    min_voltage: float = 2.5,
    threshold_current: float = 0.075,
    voltage_intervall: float = 0.01,
    minimal_current_for_capacity: float = -1.2,
    maximal_current_for_capacity: float = -0.8,
    min_current_diff: float = 0.5,
    max_time_diff: float = 0.5,
    min_voltage_diff: float = 0,
    ignore_negative_resistance_values: bool = False,
) -> _BatteryConfigClass:
    """Factory function to create a BatteryConfig instance with non-standard parameters.

    All parameters have defaults matching the standard configuration.
    Use this instead of direct _BatteryConfigClass instantiation to ensure
    safe creation of independent config instances.

    Args:
        cell_name: Name identifier for the cell type.
        c_ref: Reference capacity in Ah.
        soc_start: Starting state of charge.
        max_voltage: Maximum cell voltage in V.
        min_voltage: Minimum cell voltage in V.
        threshold_current: Current threshold for analysis.
        voltage_intervall: Voltage interval step size.
        minimal_current_for_capacity: Min current threshold for capacity calc.
        maximal_current_for_capacity: Max current threshold for capacity calc.
        min_current_diff: Min current difference for resistance calc.
        max_time_diff: Max time difference for resistance calc.
        min_voltage_diff: Min voltage difference for resistance calc.
        ignore_negative_resistance_values: Ignore negative resistance values.

    Returns:
        A new _BatteryConfigClass instance with the specified parameters.
    """
    return _BatteryConfigClass(
        cell_name=cell_name,
        c_ref=c_ref,
        soc_start=soc_start,
        max_voltage=max_voltage,
        min_voltage=min_voltage,
        threshold_current=threshold_current,
        voltage_intervall=voltage_intervall,
        minimal_current_for_capacity=minimal_current_for_capacity,
        maximal_current_for_capacity=maximal_current_for_capacity,
        min_current_diff=min_current_diff,
        max_time_diff=max_time_diff,
        min_voltage_diff=min_voltage_diff,
        ignore_negative_resistance_values=ignore_negative_resistance_values,
    )


class BatteryConfig:
    """Container class providing predefined battery configurations.

    This class holds static factory calls for common battery cell types.
    Access predefined configs via class attributes, or create custom configs
    using the battery_config_wrapper function.

    Attributes:
        DEFAULT
        LGM50LT_NMC_4800
        HAKADI_NMC_1500
    """

    DEFAULT = battery_config_wrapper()

    # Configs for different Cells
    LGM50LT_NMC_4800 = battery_config_wrapper(
        c_ref=4.8,
        max_voltage=4.2,
        min_voltage=2.5,
        min_current_diff=1,
        max_time_diff=0.5,
        min_voltage_diff=0,
        ignore_negative_resistance_values=True,
    )

    HAKADI_NMC_1500 = battery_config_wrapper(c_ref=1.5, max_voltage=3.6, min_voltage=2.0)

from dataclasses import dataclass
from typing import Any, Optional

from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences


class DeviceConfig:
    """
    Device configurations used for segment detection and primitive annotation.

    Attributes:
        BASYTEC_CTS (list[float])
            0.002,  # ACCURACY_VOLTAGE_SIGNAL
            0.003,  # ACCURACY_CURRENT_SIGNAL
            0.002,  # ACCURACY_VOLTAGE_MEASUREMENT
            0.003,  # ACCURACY_CURRENT_MEASUREMENT
            6,  # FS_VOLTAGE
            5,  # FS_CURRENT

        NEWARE_CT_4008Q_5V12A_S1 (list[float])
            0.0005,  # ACCURACY_VOLTAGE_SIGNAL
            0.0005,  # ACCURACY_CURRENT_SIGNAL
            0.0005,  # ACCURACY_VOLTAGE_MEASUREMENT
            0.0005,  # ACCURACY_CURRENT_MEASUREMENT
            5,  # FS_VOLTAGE
            3,  # FS_CURRENT
    """

    BASYTEC_CTS = [  # BaSyTec
        0.002,  # ACCURACY_VOLTAGE_SIGNAL
        0.003,  # ACCURACY_CURRENT_SIGNAL
        0.002,  # ACCURACY_VOLTAGE_MEASUREMENT
        0.003,  # ACCURACY_CURRENT_MEASUREMENT
        6,  # FS_VOLTAGE
        5,  # FS_CURRENT
    ]

    NEWARE_CT_4008Q_5V12A_S1 = [
        0.0005,  # ACCURACY_VOLTAGE_SIGNAL
        0.0005,  # ACCURACY_CURRENT_SIGNAL
        0.0005,  # ACCURACY_VOLTAGE_MEASUREMENT
        0.0005,  # ACCURACY_CURRENT_MEASUREMENT
        5,  # FS_VOLTAGE
        3,  # FS_CURRENT
    ]


@dataclass
class _PrimitiveConfigClass:
    """Internal primitive analysis configuration dataclass.

    This configuration is used by add_primitive_segments() for segment detection
    and primitive annotation.

    Attributes:
        threshold_dict: Device threshold configuration list [voltage_acc, current_acc,
            voltage_meas_acc, current_meas_acc, voltage_fs, current_fs].
        segments_to_detect_config: List of (column, threshold) tuples for segment detection.
            Threshold should be half the definitive difference for detection above/below.
        adjust_segments_config: List of (column, threshold) tuples for segment adjustment.
            ORDER IS IMPORTANT - determines adjustment priority.
        thresholds_primitive_annotation: Dict mapping primitive keys (V, I, P) to threshold values.
            MUST USE SAME KEY AS DATA_COLUMNS.
        threshold_cv_segments_0a_end: Threshold for detecting CV segments ending at 0A.

        show_runtime: Whether to show runtime information.
        show_runtime_annotation: Whether to show annotation runtime.
        show_runtime_analyze: Whether to show analysis runtime.
        show_runtime_visualization: Whether to show visualization runtime.
        threshold_console_prints_zero_length_check: Console print threshold for zero length check.
        threshold_console_prints_cv_check: Console print threshold for CV check.
        threshold_console_prints_finetuning_width: Console print threshold for finetuning width.
        threshold_console_prints_power_zero_watt_check: Console print threshold for power zero watt check.

        data_columns: Dict mapping short keys to full column names {"V": "Voltage[V]", ...}.
            These shouldn't be changed when using ppb Dataframes.

        check_cv_0aend_segments_bool: Whether to check CV segments ending at 0A.
        check_zero_length_segments_bool: Whether to check for zero-length segments.
        check_power_zero_w_segments_bool: Whether to check for power zero watt segments.
        supress_io_warnings: Whether to suppress IO warnings during processing.
        precompile: Whether to precompile configuration for performance.
        force_precompilation: Whether to force precompilation even if not needed.
    """

    # Threshold and segment configuration
    threshold_dict: list[float]
    segments_to_detect_config: list[tuple[str, float]]
    adjust_segments_config: list[tuple[str, float]]
    thresholds_primitive_annotation: dict[str, float]
    threshold_cv_segments_0a_end: float

    # Runtime configuration
    show_runtime: bool
    show_runtime_annotation: bool
    show_runtime_analyze: bool
    show_runtime_visualization: bool
    threshold_console_prints_zero_length_check: int
    threshold_console_prints_cv_check: int
    threshold_console_prints_finetuning_width: int
    threshold_console_prints_power_zero_watt_check: int

    # Data configuration
    data_columns: dict[str, str]

    # Additional configuration flags
    check_cv_0aend_segments_bool: bool
    check_zero_length_segments_bool: bool
    check_power_zero_w_segments_bool: bool
    supress_io_warnings: bool
    precompile: bool
    force_precompilation: bool


@dataclass
class _SequenceOverviewConfigClass:
    """Internal sequence overview configuration dataclass.

    This configuration is used by extract_sequence_overview() for sequence detection
    and analysis.

    Attributes:
        segment_sequence_config: Unified configuration for all segments and sequences.
            Ordered as: sequences -> standard segments -> primitive segments.
            Each entry contains "rules" dict with possible keys:
            - variable: "I", "V", or "P" (for primitive segments)
            - type: "Constant", "Ramp", or "Rest" (for standard segments)
            - direction: "Charge", "Discharge", "Up", or "Down" (for standard segments)
            For sequences: {"loop": bool, "min_loops": int, "sequence": [segment_names]}

        show_runtime: Whether to show runtime information.

        data_columns: Dict mapping short keys to full column names {"V": "Voltage[V]", ...}.
            These shouldn't be changed when using ppb Dataframes.
    """

    segment_sequence_config: dict[str, dict[str, Any]]
    show_runtime: bool
    data_columns: dict[str, str]


@dataclass
class _VisualizationConfigClass:
    """Internal visualization configuration dataclass.

    This configuration is used for visualization and plotting functions.

    Attributes:
        visualize_phases_config: List of (phase_key, color) tuples for phase visualization.
        line_visualization_config: List of (column, color, (min, max)) tuples for line plots.
        start: Start time/value for analysis window.
        end: End time/value for analysis window.
        use_lines_for_segments: Whether to use lines for segment visualization.
        show_column_names: Whether to show column names in plots.
        show_time: Whether to show time axis in plots.
        show_id: Whether to show segment IDs in plots.
        segment_alpha: Alpha transparency value for segment visualization (0.0-1.0).
        width_height_ratio: [width, height] ratio for plot sizing.
        end_condition_map_generate_instructions: Dict mapping segment types to end conditions.
            Keys: "CC", "CV", "CP", "Pause". Values: "voltage", "current", "time".
        standard_columns: List of standard column names for data processing.
    """

    visualize_phases_config: list[tuple[str, str]]
    line_visualization_config: list[tuple[str, str, tuple[float, float]]]
    start: float
    end: float
    use_lines_for_segments: bool
    show_column_names: bool
    show_time: bool
    show_id: bool
    show_runtime: bool
    segment_alpha: float
    width_height_ratio: list[float]
    end_condition_map_generate_instructions: dict[str, str]
    standard_columns: list[str]


def primitive_config_wrapper(
    threshold_dict: Optional[list[float]] = None,
    segments_to_detect_config: Optional[list[tuple[str, float]]] = None,
    adjust_segments_config: Optional[list[tuple[str, float]]] = None,
    thresholds_primitive_annotation: Optional[dict[str, float]] = None,
    show_runtime: bool = True,
    show_runtime_annotation: bool = True,
    show_runtime_analyze: bool = True,
    show_runtime_visualization: bool = True,
    threshold_console_prints_zero_length_check: int = 2,
    threshold_console_prints_cv_check: int = 2,
    threshold_console_prints_finetuning_width: int = 2,
    threshold_console_prints_power_zero_watt_check: int = 10,
    data_columns: Optional[dict[str, str]] = None,
    check_cv_0aend_segments_bool: bool = False,
    check_zero_length_segments_bool: bool = False,
    check_power_zero_w_segments_bool: bool = False,
    supress_io_warnings: bool = False,
    precompile: bool = False,
    force_precompilation: bool = False,
) -> _PrimitiveConfigClass:
    """Factory function to create a PrimitiveConfig instance with non-standard parameters.

    All parameters have defaults matching the standard configuration.
    Use this instead of direct _PrimitiveConfigClass instantiation to ensure
    safe creation of independent config instances.

    Args:
        threshold_dict: Device threshold configuration list [voltage_acc, current_acc,
            voltage_meas_acc, current_meas_acc, voltage_fs, current_fs].
            Defaults to DeviceConfig.NEWARE_CT_4008Q_5V12A_S1.
        segments_to_detect_config: List of (column, threshold) tuples for segment detection.
            Threshold should be half the definitive difference for detection above/below.
            ORDER IS IMPORTANT for detection priority.
        adjust_segments_config: List of (column, threshold) tuples for segment adjustment.
            ORDER IS IMPORTANT - determines adjustment priority.
        thresholds_primitive_annotation: Dict mapping primitive keys (V, I, P) to threshold values.
            MUST USE SAME KEY AS DATA_COLUMNS.
        show_runtime: Whether to show runtime information during processing.
        show_runtime_annotation: Whether to show annotation runtime information.
        show_runtime_analyze: Whether to show analysis runtime information.
        show_runtime_visualization: Whether to show visualization runtime information.
        threshold_console_prints_zero_length_check: Console print threshold for zero length check.
        threshold_console_prints_cv_check: Console print threshold for CV segment check.
        threshold_console_prints_finetuning_width: Console print threshold for width finetuning.
        threshold_console_prints_power_zero_watt_check: Console print threshold for power zero watt check.
        data_columns: Dict mapping short keys to full column names.
            Example: {"V": "Voltage[V]", "I": "Current[A]"}.
            Should not be changed when using ppb Dataframes.
        check_cv_0aend_segments_bool: Whether to check CV segments ending at 0A. Default: False.
        check_zero_length_segments_bool: Whether to check for zero-length segments. Default: False.
        check_power_zero_w_segments_bool: Whether to check for power zero watt segments. Default: False.
        supress_io_warnings: Whether to suppress IO warnings during processing. Default: False.
        precompile: Whether to precompile configuration for performance. Default: False.
        force_precompilation: Whether to force precompilation even if not needed. Default: False.

    Returns:
        A new _PrimitiveConfigClass instance with the specified parameters.
    """
    # Set default threshold_dict if not provided
    if threshold_dict is None:
        threshold_dict = DeviceConfig.NEWARE_CT_4008Q_5V12A_S1

    # Calculate derived values
    min_definitive_voltage_difference, min_definitive_current_difference = calculate_minimum_definitive_differences(
        *threshold_dict
    )

    # Set default configurations if not provided
    if segments_to_detect_config is None:
        segments_to_detect_config = [
            # divide threshold by 2 because it's looking above and below the target line
            ("Voltage[V]", min_definitive_voltage_difference / 2),
            ("Current[A]", min_definitive_current_difference / 2),
            ("Power[W]", (min_definitive_voltage_difference + min_definitive_current_difference) / 2),
        ]

    if adjust_segments_config is None:
        # ORDER IS IMPORTANT!
        adjust_segments_config = [
            ("Voltage[V]", min_definitive_voltage_difference),
            ("Current[A]", min_definitive_current_difference),
            ("Power[W]", (min_definitive_voltage_difference + min_definitive_current_difference)),
        ]

    if thresholds_primitive_annotation is None:
        # HAS TO USE SAME KEY AS DATA_COLUMNS! only change the values of thresholds!
        thresholds_primitive_annotation = {
            "V": min_definitive_voltage_difference,
            "I": min_definitive_current_difference,
            "P": min_definitive_voltage_difference + min_definitive_current_difference,
        }

    threshold_cv_segments_0a_end = min_definitive_current_difference

    if data_columns is None:
        # These shouldn't be changed when using ppb Dataframes
        data_columns = {
            "V": "Voltage[V]",
            "I": "Current[A]",
            "P": "Power[W]",
        }

    return _PrimitiveConfigClass(
        threshold_dict=threshold_dict,
        segments_to_detect_config=segments_to_detect_config,
        adjust_segments_config=adjust_segments_config,
        thresholds_primitive_annotation=thresholds_primitive_annotation,
        threshold_cv_segments_0a_end=threshold_cv_segments_0a_end,
        show_runtime=show_runtime,
        show_runtime_annotation=show_runtime_annotation,
        show_runtime_analyze=show_runtime_analyze,
        show_runtime_visualization=show_runtime_visualization,
        threshold_console_prints_zero_length_check=threshold_console_prints_zero_length_check,
        threshold_console_prints_cv_check=threshold_console_prints_cv_check,
        threshold_console_prints_finetuning_width=threshold_console_prints_finetuning_width,
        threshold_console_prints_power_zero_watt_check=threshold_console_prints_power_zero_watt_check,
        data_columns=data_columns,
        check_cv_0aend_segments_bool=check_cv_0aend_segments_bool,
        check_zero_length_segments_bool=check_zero_length_segments_bool,
        check_power_zero_w_segments_bool=check_power_zero_w_segments_bool,
        supress_io_warnings=supress_io_warnings,
        precompile=precompile,
        force_precompilation=force_precompilation,
    )


def sequence_overview_config_wrapper(
    segment_sequence_config: Optional[dict[str, dict[str, Any]]] = None,
    show_runtime: bool = True,
    data_columns: Optional[dict[str, str]] = None,
) -> _SequenceOverviewConfigClass:
    """Factory function to create a SequenceOverviewConfig instance with non-standard parameters.

    All parameters have defaults matching the standard configuration.
    Use this instead of direct _SequenceOverviewConfigClass instantiation to ensure
    safe creation of independent config instances.

    Args:
        segment_sequence_config: Unified configuration for all segments and sequences.
            Ordered as: sequences -> standard segments -> primitive segments.
            Each entry contains "rules" dict. For segments:
            - variable: "I", "V", or "P" (primitive segments only)
            - type: "Constant", "Ramp", or "Rest" (standard segments)
            - direction: "Charge", "Discharge", "Up", or "Down" (standard segments)
            For sequences: {"loop": bool, "min_loops": int, "sequence": [segment_names]}
        show_runtime: Whether to show runtime information during processing.
        data_columns: Dict mapping short keys to full column names.
            Example: {"V": "Voltage[V]", "I": "Current[A]"}.
            Should not be changed when using ppb Dataframes.

    Returns:
        A new _SequenceOverviewConfigClass instance with the specified parameters.
    """
    if segment_sequence_config is None:
        # Unified segment and sequence configuration - maintaining original order:
        # 1. Complex Sequences (sequences_config)
        # 2. Standard segments (segments_config_standard)
        # 3. Primitive segments (segments_config_simple)
        segment_sequence_config = {
            # Complex Sequences
            # Loop rules: "loop": True, "exact_loops": 2, "min_loops": 2, "max_loops": 2, "minimum_IDs": 6
            "Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge", "Pause"]},
            "Charge_iOCV": {"loop": True, "min_loops": 2, "sequence": ["Pause", "CC_Charge"]},
            "CCCV_Charge": {"loop": False, "sequence": ["CC_Charge", "CV_Charge"]},
            # Standard segments - Pause, CC/CV/CP Charge/Discharge, Ramp segments
            "Pause": {"rules": {"type": "Rest"}},
            "CC_Charge": {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
            "CV_Charge": {"rules": {"variable": "V", "type": "Constant", "direction": "Charge"}},
            "CP_Charge": {"rules": {"variable": "P", "type": "Constant", "direction": "Charge"}},
            "CC_Discharge": {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
            "CV_Discharge": {"rules": {"variable": "V", "type": "Constant", "direction": "Discharge"}},
            "CP_Discharge": {"rules": {"variable": "P", "type": "Constant", "direction": "Discharge"}},
            "CRamp_Charge": {"rules": {"variable": "I", "type": "Ramp", "direction": "Up"}},
            "VRamp_Charge": {"rules": {"variable": "V", "type": "Ramp", "direction": "Up"}},
            "PRamp_Charge": {"rules": {"variable": "P", "type": "Ramp", "direction": "Up"}},
            "CRamp_Discharge": {"rules": {"variable": "I", "type": "Ramp", "direction": "Down"}},
            "VRamp_Discharge": {"rules": {"variable": "V", "type": "Ramp", "direction": "Down"}},
            "PRamp_Discharge": {"rules": {"variable": "P", "type": "Ramp", "direction": "Down"}},
            # Primitive segments - I, V, P, Charging, Discharging
            "I": {"rules": {"variable": "I"}},
            "V": {"rules": {"variable": "V"}},
            "P": {"rules": {"variable": "P"}},
            "Charging": {"rules": {"direction": "Charge"}},
            "Discharging": {"rules": {"direction": "Discharge"}},
        }

    if data_columns is None:
        # These shouldn't be changed when using ppb Dataframes
        data_columns = {
            "V": "Voltage[V]",
            "I": "Current[A]",
            "P": "Power[W]",
        }

    return _SequenceOverviewConfigClass(
        segment_sequence_config=segment_sequence_config,
        show_runtime=show_runtime,
        data_columns=data_columns,
    )


def visualization_config_wrapper(
    visualize_phases_config: Optional[list[tuple[str, str]]] = None,
    line_visualization_config: Optional[list[tuple[str, str, tuple[float, float]]]] = None,
    start: float = 0,
    end: float = 1e100,
    use_lines_for_segments: bool = True,
    show_column_names: bool = True,
    show_time: bool = True,
    show_id: bool = True,
    show_runtime: bool = True,
    segment_alpha: float = 0.3,
    width_height_ratio: Optional[list[float]] = None,
    end_condition_map_generate_instructions: Optional[dict[str, str]] = None,
    standard_columns: Optional[list[str]] = None,
) -> _VisualizationConfigClass:
    """Factory function to create a VisualizationConfig instance with non-standard parameters.

    All parameters have defaults matching the standard configuration.
    Use this instead of direct _VisualizationConfigClass instantiation to ensure
    safe creation of independent config instances.

    Args:
        visualize_phases_config: List of (phase_key, color) tuples for phase visualization.
            Example: [("V", "blue"), ("I", "red")].
        line_visualization_config: List of (column, color, (min, max)) tuples for line plots.
            Example: [("Voltage[V]", "blue", (2.4, 4.3))].
        start: Start time/value for analysis window. Default: 0.
        end: End time/value for analysis window. Default: 1e100.
        use_lines_for_segments: Whether to use lines for segment visualization. Default: True.
        show_column_names: Whether to show column names in plots. Default: True.
        show_time: Whether to show time axis in plots. Default: True.
        show_id: Whether to show segment IDs in plots. Default: True.
        segment_alpha: Alpha transparency value for segment visualization (0.0-1.0). Default: 0.3.
        width_height_ratio: [width, height] ratio for plot sizing. Default: [1, 0.3].
        end_condition_map_generate_instructions: Dict mapping segment types to end conditions.
            Keys: "CC", "CV", "CP", "Pause". Values: "voltage", "current", "time".
        standard_columns: List of standard column names for data processing.
            Example: ["Test_Time[s]", "Voltage[V]", "Current[A]"].

    Returns:
        A new _VisualizationConfigClass instance with the specified parameters.
    """
    if visualize_phases_config is None:
        visualize_phases_config = [
            ("V", "blue"),
            ("I", "red"),
            ("P", "green"),
        ]

    if line_visualization_config is None:
        line_visualization_config = [
            ("Voltage[V]", "blue", (2.4, 4.3)),
            ("Current[A]", "red", (-10, 10)),
            ("Power[W]", "green", (-40, 20)),
        ]

    if width_height_ratio is None:
        width_height_ratio = [1, 0.3]

    if end_condition_map_generate_instructions is None:
        end_condition_map_generate_instructions = {
            "CC": "voltage",
            "CV": "current",
            "CP": "voltage",
            "Pause": "time",
        }

    if standard_columns is None:
        standard_columns = ["Test_Time[s]", "Voltage[V]", "Current[A]"]

    return _VisualizationConfigClass(
        visualize_phases_config=visualize_phases_config,
        line_visualization_config=line_visualization_config,
        start=start,
        end=end,
        use_lines_for_segments=use_lines_for_segments,
        show_column_names=show_column_names,
        show_time=show_time,
        show_id=show_id,
        show_runtime=show_runtime,
        segment_alpha=segment_alpha,
        width_height_ratio=width_height_ratio,
        end_condition_map_generate_instructions=end_condition_map_generate_instructions,
        standard_columns=standard_columns,
    )


class PrimitiveConfig:
    """Container class providing predefined primitive analysis configurations.

    This class holds static factory calls for common primitive analysis configuration types.
    Access predefined configs via class attributes, or create custom configs
    using the primitive_config_wrapper function.

    Attributes:
        DEFAULT
        FALLBACK
        _PREPROCESSING
        _PRECOMPILE (internal use)
    """

    DEFAULT = primitive_config_wrapper()

    # Fallback configuration with specific non-standard parameters
    FALLBACK = primitive_config_wrapper(
        show_runtime_annotation=False,
        show_runtime_analyze=False,
        show_runtime_visualization=False,
        check_cv_0aend_segments_bool=True,
        check_zero_length_segments_bool=True,
        check_power_zero_w_segments_bool=True,
        supress_io_warnings=False,
        precompile=True,
        force_precompilation=False,
    )

    # Preprocessing configuration with enhanced runtime settings
    _PREPROCESSING = primitive_config_wrapper(
        show_runtime=True,
        show_runtime_annotation=True,
        show_runtime_analyze=True,
        show_runtime_visualization=True,
    )

    # Precompilation configuration for internal use
    _PRECOMPILE = primitive_config_wrapper(
        show_runtime=False,
        show_runtime_annotation=False,
        show_runtime_analyze=False,
        show_runtime_visualization=False,
        check_cv_0aend_segments_bool=True,
        check_zero_length_segments_bool=True,
        check_power_zero_w_segments_bool=False,
        supress_io_warnings=True,
        precompile=False,
        force_precompilation=False,
    )

    # OCV analysis configuration
    OCV_ANALYSIS_DEFAULT = primitive_config_wrapper(
        threshold_dict=DeviceConfig.NEWARE_CT_4008Q_5V12A_S1,
        show_runtime=True,
        show_runtime_annotation=True,
        show_runtime_analyze=True,
        show_runtime_visualization=True,
        threshold_console_prints_zero_length_check=2,
        threshold_console_prints_cv_check=2,
        check_cv_0aend_segments_bool=True,
        check_zero_length_segments_bool=True,
        check_power_zero_w_segments_bool=True,
        supress_io_warnings=False,
        precompile=False,
        force_precompilation=False,
    )


class SequenceOverviewConfig:
    """Container class providing predefined sequence overview configurations.

    This class holds static factory calls for common sequence overview configuration types.
    Access predefined configs via class attributes, or create custom configs
    using the sequence_overview_config_wrapper function.

    Attributes:
        DEFAULT
        OCV
        STEP_ANALYZER
    """

    DEFAULT = sequence_overview_config_wrapper()

    # OCV configuration with simplified sequences
    OCV = sequence_overview_config_wrapper(
        segment_sequence_config={
            # Sequences for OCV
            "Discharge_iOCV": {"loop": True, "sequence": ["Pause", "CC_Discharge"]},
            "Charge_iOCV": {"loop": True, "sequence": ["Pause", "CC_Charge"]},
            # Standard segments for OCV
            "Pause": {"rules": {"type": "Rest"}},
            "CC_Charge": {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
            "CV_Charge": {"rules": {"variable": "V", "type": "Constant", "direction": "Charge"}},
            "CC_Discharge": {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
            "CV_Discharge": {"rules": {"variable": "V", "type": "Constant", "direction": "Discharge"}},
            "Ramp": {"rules": {"type": "Ramp"}},
            "C_Charge": {"rules": {"variable": "I", "direction": "Charge"}},
            "C_Discharge": {"rules": {"variable": "I", "direction": "Discharge"}},
            "Discharge": {"rules": {"direction": "Charge"}},  # Note: This might be a typo in original
        },
    )

    # Step analyzer configuration with custom sequences
    STEP_ANALYZER = sequence_overview_config_wrapper(
        segment_sequence_config={
            # Sequences for step analyzer
            "CCCV_Charge": {"loop": False, "sequence": ["CC_Charge", "CV_Charge"]},
            "CCCV_Discharge": {"loop": False, "sequence": ["CC_Discharge", "CV_Discharge"]},
            "CC_Discharge_after_CC_Charge": {"loop": False, "sequence": ["CC_Charge", "CC_Discharge"]},
            "CC_Discharge_after_CCCV_Charge": {"loop": False, "sequence": ["CCCV_Charge", "CC_Discharge"]},
            "CC_Discharge_after_CV_Charge": {"loop": False, "sequence": ["CV_Charge", "CC_Discharge"]},
            "CC_Discharge_after_CCCV_Charge_with_Pause": {
                "loop": False,
                "sequence": ["CCCV_Charge", "Pause", "CV_Discharge"],
            },
            "CC_Discharge_after_CC_Charge_with_Pause": {
                "loop": False,
                "sequence": ["CC_Charge", "Pause", "CC_Discharge"],
            },
            "CC_Discharge_after_CV_Charge_with_Pause": {
                "loop": False,
                "sequence": ["CV_Charge", "Pause", "CC_Discharge"],
            },
            # Standard segments for step analyzer
            "Pause": {"rules": {"type": "Rest"}},
            "CC_Charge": {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
            "CV_Charge": {"rules": {"variable": "V", "type": "Constant", "direction": "Charge"}},
            "CP_Charge": {"rules": {"variable": "P", "type": "Constant", "direction": "Charge"}},
            "CC_Discharge": {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
            "CV_Discharge": {"rules": {"variable": "V", "type": "Constant", "direction": "Discharge"}},
            "CP_Discharge": {"rules": {"variable": "P", "type": "Constant", "direction": "Discharge"}},
        },
    )

    # Generate instructions configuration - matches original SEGMENTS_CONFIG_STANDARD from generate_instructions.py
    GENERATE_INSTRUCTIONS = sequence_overview_config_wrapper(
        segment_sequence_config={
            "Pause": {"rules": {"type": "Rest"}},
            "CC_Charge": {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
            "CV_Charge": {"rules": {"variable": "V", "type": "Constant", "direction": "Charge"}},
            "CP_Charge": {"rules": {"variable": "P", "type": "Constant", "direction": "Charge"}},
            "CC_Discharge": {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
            "CV_Discharge": {"rules": {"variable": "V", "type": "Constant", "direction": "Discharge"}},
            "CP_Discharge": {"rules": {"variable": "P", "type": "Constant", "direction": "Discharge"}},
            "CRamp_Charge": {"rules": {"variable": "I", "type": "Ramp", "direction": "Up"}},
            "VRamp_Charge": {"rules": {"variable": "V", "type": "Ramp", "direction": "Up"}},
            "PRamp_Charge": {"rules": {"variable": "P", "type": "Ramp", "direction": "Up"}},
            "CRamp_Discharge": {"rules": {"variable": "I", "type": "Ramp", "direction": "Down"}},
            "VRamp_Discharge": {"rules": {"variable": "V", "type": "Ramp", "direction": "Down"}},
            "PRamp_Discharge": {"rules": {"variable": "P", "type": "Ramp", "direction": "Down"}},
        },
    )


class VisualizationConfig:
    """Container class providing predefined visualization configurations.

    This class holds static factory calls for common visualization configuration types.
    Access predefined configs via class attributes, or create custom configs
    using the visualization_config_wrapper function.

    Attributes:
        DEFAULT
    """

    DEFAULT = visualization_config_wrapper()

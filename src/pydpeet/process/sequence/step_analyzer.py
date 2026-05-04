import logging
import os

import pandas as pd

from pydpeet.process.sequence.configs.config import (
    PrimitiveConfig,
    SequenceOverviewConfig,
    _PrimitiveConfigClass,
    _SequenceOverviewConfigClass,
)
from pydpeet.process.sequence.utils.annotate.annotate_primitives import (
    _annotate_primitives,
    _merged_annotations,
)
from pydpeet.process.sequence.utils.console_prints.log_time import _log_time
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
from pydpeet.process.sequence.utils.processing.analyze_segments import _analyze_segments
from pydpeet.process.sequence.utils.processing.attempt_to_merge_neighboring_segments import (
    _attempt_to_merge_neighboring_segments,
)
from pydpeet.process.sequence.utils.processing.check_CV_results import _check_CV_0Aend_segments
from pydpeet.process.sequence.utils.processing.check_power_zero_watt_segments import _check_power_zero_watt_segments
from pydpeet.process.sequence.utils.processing.check_zero_length import _check_zero_length_segments
from pydpeet.process.sequence.utils.processing.split_in_segments import _split_in_segments_using_incremental_linear_fit
from pydpeet.process.sequence.utils.processing.supress_smaller_segments import (
    _add_segment_lengths,
    _keep_max_segment_id,
)
from pydpeet.process.sequence.utils.processing.widen_constant_segments import _widen_constant_segments
from pydpeet.utils.guardrails import _guardrail_boolean, _guardrail_dataframe

logger = logging.getLogger(__name__)


def add_primitive_segments(
    df: pd.DataFrame,
    config: _PrimitiveConfigClass,
) -> pd.DataFrame:
    """
    Function to perform step analysis to create a segmentation of a dataframe into primitive Segments.

    Parameters:
    df (pd.DataFrame): Input dataframe to perform primitive step analysis on.
    config (_PrimitiveConfigClass): Configuration object containing all parameters for step analysis.
        Use PrimitiveConfig.DEFAULT, PrimitiveConfig.FALLBACK, or create custom config via primitive_config_wrapper().

    Returns:
    df_primitives (pd.DataFrame): The final annotated dataframe
    """
    # --- Extract configuration from config object ---
    SEGMENTS_TO_DETECT_CONFIG = config.segments_to_detect_config
    ADJUST_SEGMENTS_CONFIG = config.adjust_segments_config
    THRESHOLDS_PRIMITIVE_ANNOTATION = config.thresholds_primitive_annotation
    THRESHOLD_CV_SEGMENTS_0A_END = config.threshold_cv_segments_0a_end
    SHOW_RUNTIME = config.show_runtime
    THRESHOLD_CONSOLE_PRINTS_CV_CHECK = config.threshold_console_prints_cv_check
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = config.threshold_console_prints_zero_length_check
    THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = config.threshold_console_prints_finetuning_width
    THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = config.threshold_console_prints_power_zero_watt_check
    check_CV_0Aend_segments_bool = config.check_cv_0aend_segments_bool
    check_zero_length_segments_bool = config.check_zero_length_segments_bool
    check_Power_zero_W_segments_bool = config.check_power_zero_w_segments_bool
    supress_IO_warnings = config.supress_io_warnings
    PRECOMPILE = config.precompile
    FORCE_PRECOMPILATION = config.force_precompilation

    DATA_COLUMNS = config.data_columns

    # # TODO variable to choose if copy should be used?
    # --- Handle None boolean values by converting to True defaults ---
    SHOW_RUNTIME = True if SHOW_RUNTIME is None else SHOW_RUNTIME
    check_CV_0Aend_segments_bool = True if check_CV_0Aend_segments_bool is None else check_CV_0Aend_segments_bool
    check_zero_length_segments_bool = (
        True if check_zero_length_segments_bool is None else check_zero_length_segments_bool
    )
    check_Power_zero_W_segments_bool = (
        True if check_Power_zero_W_segments_bool is None else check_Power_zero_W_segments_bool
    )
    supress_IO_warnings = True if supress_IO_warnings is None else supress_IO_warnings
    PRECOMPILE = True if PRECOMPILE is None else PRECOMPILE
    FORCE_PRECOMPILATION = True if FORCE_PRECOMPILATION is None else FORCE_PRECOMPILATION

    # --- Guardrails ---
    required_column_dtypes = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
    required_columns = [col for col, _ in required_column_dtypes]
    _guardrail_dataframe(
        df,
        hard_fail_missing_required_columns=(True, required_columns),
        hard_fail_wrong_column_dtypes=(True, required_column_dtypes),
        hard_fail_inf_values=(False, required_columns),
        hard_fail_nan_values=(False, required_columns),
        hard_fail_none_values=(False, required_columns),
    )
    for boolean_param in [
        SHOW_RUNTIME,
        check_CV_0Aend_segments_bool,
        check_zero_length_segments_bool,
        check_Power_zero_W_segments_bool,
        supress_IO_warnings,
        PRECOMPILE,
        FORCE_PRECOMPILATION,
    ]:
        _guardrail_boolean(boolean_param, hard_fail_none=False, hard_fail_wrong_type=True)

    df_step = df.copy()
    logger.warning("Dropping NaN values in 'Test_Time[s]', dropping duplicates and sorting 'Test_Time[s]' column.")
    df_step.dropna(subset=["Test_Time[s]"], inplace=True)
    df_step.drop_duplicates(subset=["Test_Time[s]"], inplace=True)
    df_step.sort_values(by=["Test_Time[s]"], inplace=True)

    # --- Guardrails & IO Warnings ---

    assert SEGMENTS_TO_DETECT_CONFIG is not None
    assert ADJUST_SEGMENTS_CONFIG is not None
    assert THRESHOLDS_PRIMITIVE_ANNOTATION is not None
    assert THRESHOLD_CV_SEGMENTS_0A_END is not None
    assert THRESHOLD_CONSOLE_PRINTS_CV_CHECK is not None
    assert THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK is not None
    assert THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH is not None
    assert THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK is not None

    if not supress_IO_warnings:
        for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG:
            if threshold < 0:
                logger.warning(f"Threshold for {column_name} is negative, using abs({threshold}) instead.")
                SEGMENTS_TO_DETECT_CONFIG = [
                    (column_name, abs(threshold)) for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG
                ]
        if THRESHOLD_CV_SEGMENTS_0A_END < 0.0:
            logger.warning(
                f"THRESHOLD_CV_SEGMENTS_0A_END is negative, using abs({THRESHOLD_CV_SEGMENTS_0A_END}) instead."
            )
            THRESHOLD_CV_SEGMENTS_0A_END = abs(THRESHOLD_CV_SEGMENTS_0A_END)
        if THRESHOLD_CONSOLE_PRINTS_CV_CHECK < 0:
            logger.warning(
                f"THRESHOLD_CONSOLE_PRINTS_CV_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_CV_CHECK}) instead."
            )
            THRESHOLD_CONSOLE_PRINTS_CV_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_CV_CHECK)
        if THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK < 0:
            logger.warning(
                f"THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK}) instead."
            )
            THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK)
        if THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH < 0:
            logger.warning(
                f"THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH is negative, using abs({THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH}) instead."
            )
            THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = abs(THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH)
        if THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK < 0:
            logger.warning(
                f"THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK}) instead."
            )
            THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK)

    if PRECOMPILE:
        if len(df_step) > 100_000 or FORCE_PRECOMPILATION:
            with _log_time(
                "precompiling step_analyzer_primitives and df_primitives_correction", SHOW_RUNTIME=SHOW_RUNTIME
            ):
                _precompile_step_analyzer()

        else:
            logger.warning(
                f"Input dataframe is small ({len(df_step)} < 100_000 rows. Skipping precompilation unless you set FORCE_PRECOMPILATION = True."
            )

    if SHOW_RUNTIME:
        logger.info(f"detecting segments in dataframe of size {len(df_step)}...")

    with _log_time("calculating Power[W]", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step["Power[W]"] = df_step["Voltage[V]"] * df_step["Current[A]"]

    for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG:
        with _log_time(
            f"separating {column_name} into segments using incremental linear fit", SHOW_RUNTIME=SHOW_RUNTIME
        ):
            df_step = _split_in_segments_using_incremental_linear_fit(
                df=df_step, column_name=column_name, threshold=threshold
            )

    keep_max_segment_id_config = []
    for _, col_name in DATA_COLUMNS.items():
        segment_col = f"Segment_{col_name}"
        with _log_time(f"adding Length_{segment_col} to calculate the dominating segments", SHOW_RUNTIME=SHOW_RUNTIME):
            df_step = _add_segment_lengths(df=df_step, column_name=col_name)
        keep_max_segment_id_config.append((f"Length_{segment_col}", segment_col))

    with _log_time("suppressing smaller segments", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _keep_max_segment_id(df=df_step, keep_max_segment_id_config=keep_max_segment_id_config)

    with _log_time("attempting to merge neighboring segments", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _attempt_to_merge_neighboring_segments(df=df_step, adjust_segments_config=ADJUST_SEGMENTS_CONFIG)

    with _log_time("fine tuning width of constant segments to better fit the data", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _widen_constant_segments(
            df=df_step,
            adjust_segments_config=ADJUST_SEGMENTS_CONFIG,
            Threshold_segments_to_print=THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH,
            supress_IO_warnings=supress_IO_warnings,
        )

    if SHOW_RUNTIME:
        logger.info("starting annotation...")

    df_primitives = _annotate_primitives(
        df_step, data_columns=DATA_COLUMNS, thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION, show_runtime=SHOW_RUNTIME
    )

    with _log_time("dropping temporary length and segment columns", SHOW_RUNTIME=SHOW_RUNTIME):
        columns_to_drop = [f"Length_Segment_{v}" for v in DATA_COLUMNS.values()] + [
            f"Segment_{v}" for v in DATA_COLUMNS.values()
        ]
        df_primitives = df_primitives.drop(columns=columns_to_drop)

    # Can be removed if we choose to always apply these additional corrections
    if check_CV_0Aend_segments_bool or check_Power_zero_W_segments_bool or check_zero_length_segments_bool:
        if SHOW_RUNTIME:
            logger.info("starting additional data checks and corrections...")
    else:
        if not supress_IO_warnings:
            logger.warning("Skipping additional data checks and corrections...")

    if check_CV_0Aend_segments_bool:
        df_primitives = _check_CV_0Aend_segments(
            df_primitives=df_primitives,
            tolerance=THRESHOLD_CV_SEGMENTS_0A_END,
            SHOW_RUNTIME=SHOW_RUNTIME,
            DATA_COLUMNS=DATA_COLUMNS,
            THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
            supress_IO_warnings=supress_IO_warnings,
            THRESHOLD_CONSOLE_PRINTS_CV_CHECK=THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
            THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK=THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
        )

    if check_zero_length_segments_bool:
        df_primitives = _check_zero_length_segments(
            df_primitives,
            SHOW_RUNTIME=SHOW_RUNTIME,
            DATA_COLUMNS=DATA_COLUMNS,
            THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
            supress_IO_warnings=supress_IO_warnings,
            THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK=THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
        )

    if check_Power_zero_W_segments_bool:
        df_primitives = _check_power_zero_watt_segments(
            df_primitives=df_primitives,
            SHOW_RUNTIME=SHOW_RUNTIME,
            THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
            supress_IO_warnings=supress_IO_warnings,
            THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK=THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK,
            DATA_COLUMNS=DATA_COLUMNS,
        )

    if check_CV_0Aend_segments_bool or check_zero_length_segments_bool or check_Power_zero_W_segments_bool:
        with _log_time("updating annotations", SHOW_RUNTIME=SHOW_RUNTIME):
            df_primitives = _merged_annotations(
                df=df_primitives, data_columns=DATA_COLUMNS, thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION
            )

    return df_primitives


def extract_sequence_overview(
    df_primitives: pd.DataFrame,
    config: _SequenceOverviewConfigClass,
) -> pd.DataFrame:
    """
    Create a DataFrame of segments and sequences from a DataFrame of primitives. (ID, longest sequence, segments/sequence)
    Each Segment/Sequence is listed per ID with an incrementally increasing value per match.

    The rules dictionary can contain the following keys:
        - "min_length_sec": minimum length of the segment in seconds
        - "min_avg_abs": minimum average absolute value of the segment
        - "max_slope": maximum slope of the segment
        - "min_abs_slope": minimum absolute slope of the segment
        - "direction": direction of the segment
        - "variable": variable name of the segment
        - "type": type of the segment

    "loop": True can be used to support looping sequences
    "merge": True can be used to support merging multiple subsequences and segments

    Parameters:
        df_primitives (pd.DataFrame): A DataFrame of primitives created using add_primitive_segments(). With the following columns:
            standard_columns = ['Test_Time[s]', 'Voltage[V]', 'Current[A]', 'Power[W]', "ID", "Variable", "Duration", "Length", "Min", "Max", "Avg", "Type", "Direction", "Slope"]
        config (_SequenceOverviewConfigClass): Configuration object containing segment_sequence_config and show_runtime.
            Use SequenceOverviewConfig.DEFAULT, SequenceOverviewConfig.OCV, or create custom config via sequence_overview_config_wrapper().

    Returns:
        df_segments_and_sequences (pd.DataFrame): A DataFrame containing the columns 'ID', 'Sequence', and all columns
                                                  specified in config.segment_sequence_config.

    """
    # --- Extract configuration from config object ---
    SEGMENT_SEQUENCE_CONFIG = config.segment_sequence_config
    SHOW_RUNTIME = config.show_runtime

    if SEGMENT_SEQUENCE_CONFIG is None or not isinstance(SEGMENT_SEQUENCE_CONFIG, dict):
        raise ValueError("segment_sequence_config is None or not a dict")

    # --- Guardrails ---
    # Check boolean first (fast) before expensive dataframe checks (slow O(N))
    _guardrail_boolean(SHOW_RUNTIME, hard_fail_none=True, hard_fail_wrong_type=True)

    required_column_dtypes = [
        ("Test_Time[s]", float),
        ("Voltage[V]", float),
        ("Current[A]", float),
        ("Power[W]", float),
        ("ID", int),
        ("Variable", str),
        ("Duration", float),
        ("Length", float),
        ("Min", float),
        ("Max", float),
        ("Avg", float),
        ("Type", str),
        ("Direction", str),
        ("Slope", float),
    ]
    required_columns = [col for col, _ in required_column_dtypes]
    _guardrail_dataframe(
        df_primitives,
        hard_fail_empty=True,
        hard_fail_missing_required_columns=(True, required_columns),
        hard_fail_wrong_column_dtypes=(True, required_column_dtypes),
        hard_fail_inf_values=(False, required_columns),
        hard_fail_nan_values=(False, required_columns),
        hard_fail_none_values=(False, required_columns),
    )

    if SHOW_RUNTIME:
        logger.info("analyzing segments...")
    with _log_time("filtering by ID", SHOW_RUNTIME=SHOW_RUNTIME):
        df_ID_filtered = df_primitives.loc[df_primitives.groupby("ID")["ID"].idxmin()]

    # Not with log_time() since it's handled internally
    df_segments_and_sequences = _analyze_segments(
        df=df_ID_filtered, SHOW_RUNTIME=SHOW_RUNTIME, SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG
    )

    return df_segments_and_sequences


def _precompile_step_analyzer() -> None:
    """
    Precompilation of the step analyzer function using dummy data.

    This function precompiles the numba.njit subfunctions of the step analyzer using dummy data.
    This is useful for having *consistent* runtimes when these subfunctions are called to run multiple times.

    Parameters:
        None

    Returns:
        None
    """
    # Use PRECOMPILE config for precompilation (has all runtime flags disabled)
    primitive_config = PrimitiveConfig._PRECOMPILE
    sequence_config = SequenceOverviewConfig.DEFAULT

    # precompile using dummy data
    _project_dir = os.path.dirname(os.path.abspath(__file__))
    _res_dir = os.path.join(_project_dir, "../../res")
    _input_path = os.path.join(_res_dir, "precompile_dummy_data.parquet")
    _df_file = pd.read_parquet(_input_path)

    _df_primitives = add_primitive_segments(
        df=_df_file,
        config=primitive_config,
    )

    correction_config = {
        "replace_ID": {
            1: "V",
        }
    }
    _df_primitives = df_primitives_correction(
        df_primitives=_df_primitives,
        correction_config=correction_config,
        data_columns=primitive_config.data_columns,
        thresholds=primitive_config.thresholds_primitive_annotation,
    )

    _ = extract_sequence_overview(
        df_primitives=_df_primitives,
        config=sequence_config,
    )

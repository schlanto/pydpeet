from __future__ import annotations

import logging
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Optional, TypeAlias

import pandas as pd

from pydpeet.io.configs.config import ReadConfig, _EXTENSION_GROUPS
from pydpeet.io.convert import (
    _convert_file,
    _convert_files_in_directory,
)
from pydpeet.utils.guardrails import _guardrail_boolean

ConfigLike: TypeAlias = ReadConfig | str
PathLike: TypeAlias = str | Path


def read(
    config: Optional[ConfigLike] = None,
    input_path: object = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame | list[pd.DataFrame]:
    """
    Read and convert battery test data into the unified PyDPEET format.

    This is the main high-level import function of PyDPEET. The function
    automatically detects whether the provided input path points to a file,
    a directory, or a list of files/directories and converts the contained
    battery test data into the unified PyDPEET dataframe format.

    Depending on the provided input, the function either returns a single
    dataframe or a list of dataframes.

    The conversion itself is performed using the selected device configuration.

    Parameters
    ----------
    config : ConfigLike, optional
        Device configuration used for parsing and mapping the raw battery
        test data into the unified PyDPEET format.

        This can either be:

        - a predefined PyDPEET configuration
        - a custom configuration object
        - a configuration dictionary

        If ``None`` (default), the filetype is auto-detected from the file
        extension and each matching configuration is tried until one succeeds.
    input_path : str | list[str]
        Path to the input data.

        Supported inputs are:

        - path to a single raw data file
        - path to a directory containing raw data files
        - list of file and/or directory paths

    keep_all_additional_data : bool, default=False
        If ``True``, all additional columns that are not part of the unified
        PyDPEET format are preserved in the returned dataframe.

        If ``False``, only standardized PyDPEET columns are kept.

    custom_folder_path : str | None, default=None
        Optional custom folder path used by specific device configurations
        that require additional external metadata or lookup files.

    Returns
    -------
    pandas.DataFrame | list[pandas.DataFrame]
        Converted dataframe(s) in the unified PyDPEET format.

        - If a single file or directory is provided, a single dataframe is returned.
        - If a list of paths is provided, a list of dataframes is returned.

    Raises
    ------
    ValueError
        Raised if:

        - the provided input path does not exist
        - an input path has an invalid type
        - a list contains unsupported entries
        - no configuration could be auto-detected

    Notes
    -----
    The returned dataframe follows the standardized PyDPEET format
    contains following columns, when available in the raw data and depending on the selected device configuration:

    - ``Date_Time``
    - ``Test_Time[s]``
    - ``Voltage[V]``
    - ``Current[A]``
    - ``Step_Count``
    - ``Temperature[°C]``
    - ``EIS_f[Hz]``
    - ``EIS_Z_Real[Ohm]``
    - ``EIS_Z_Imag[Ohm]``

    depending on the available raw data and the selected device configuration.

    Examples
    --------
    More Usage Examples can be found in following tutorial notebooks:
        :doc:`Tutorial 01: Convert and Import <../../examples/notebooks/Tutorial_01_Convert_Import>`

    Read a single file with explicit configuration:

    >>> import pydpeet as eet
    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="measurement.csv",
    ... )

    Read a single file with auto-detection that tries all possible configs that match the filetype (.xlsx, .csv, ...):

    >>> import pydpeet as eet
    >>> df = eet.read(
    ...     input_path="measurement.csv",
    ... )


    Read all files in a directory:

    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="data/",
    ... )

    Read multiple files and directories:

    >>> dfs = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path=[
    ...         "measurement_01.csv",
    ...         "measurement_02.csv",
    ...         "folder_with_measurements/",
    ...     ],
    ... )

    Keep additional raw columns:

    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="measurement.csv",
    ...     keep_all_additional_data=True,
    ... )



    See Also
    --------
    convert : Lower-level conversion interface.
    write : Export unified PyDPEET dataframes.
    merge_into_series : Merge multiple datasets into a continuous series.
        # References
    # ----------
    # """

    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            return _convert_input(input_path, config, keep_all_additional_data, custom_folder_path)
        if os.path.isdir(input_path):
            return _convert_dir(input_path, config, keep_all_additional_data, custom_folder_path)
        raise ValueError("Input path is invalid!")
    if isinstance(input_path, list):
        results = []
        for item in input_path:
            if not isinstance(item, str):
                raise ValueError("Input path item is of invalid type!")
            if os.path.isfile(item):
                results.append(_convert_input(item, config, keep_all_additional_data, custom_folder_path))
            elif os.path.isdir(item):
                results.append(_convert_dir(item, config, keep_all_additional_data, custom_folder_path))
            else:
                raise ValueError("Input path item is invalid!")
        return results
    raise ValueError("Input path is of invalid type!")


def _try_read_configs(
    config_group: Iterable[ReadConfig],
    input_path: str,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame:
    errors: dict[ReadConfig, Exception] = {}
    for config in config_group:
        try:
            logging.warning("trying config %s for file %s", config, input_path)
            result = _convert_file(config, input_path, None, keep_all_additional_data, custom_folder_path)
            logging.warning("config %s succeeded for file %s", config, input_path)
            return result
        except Exception as e:
            logging.warning("config %s failed: %s", config, e)
            errors[config] = e
    names = ", ".join(str(e) for e in errors)
    raise ValueError(
        f"None of the {config_group.__name__} configs worked for '{input_path}'. Errors: {names}"
    )


def _convert_input(
    path: str,
    config: Optional[ConfigLike],
    keep_all_additional_data: bool,
    custom_folder_path: Optional[str],
) -> pd.DataFrame:
    if config is not None:
        return _convert_file(config, path, None, keep_all_additional_data, custom_folder_path)
    suffix = Path(path).suffix.lower()
    group = _EXTENSION_GROUPS.get(suffix)
    if group is None:
        raise ValueError(f"Could not detect filetype for '{path}'")
    return _try_read_configs(group, path, keep_all_additional_data, custom_folder_path)


def _convert_dir(
    path: str,
    config: Optional[ConfigLike],
    keep_all_additional_data: bool,
    custom_folder_path: Optional[str],
) -> list[pd.DataFrame] | None:
    if config is not None:
        return _convert_files_in_directory(config, path, None, keep_all_additional_data, custom_folder_path)
    raise ValueError(
        "Auto-detection is only supported for single files. "
        "Please specify a config explicitly when reading a directory."
    )

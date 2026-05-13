from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, TypeAlias  # Add this import

import pandas as pd

from pydpeet.io.configs.config import ReadConfig
from pydpeet.io.convert import (
    _convert_file,
    _convert_files_in_directory,
)
from pydpeet.utils.guardrails import _guardrail_boolean

ConfigLike: TypeAlias = ReadConfig | str
PathLike: TypeAlias = str | Path


def read(
    config: ConfigLike,
    input_path: object,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame | list[pd.DataFrame]:
    """
    Reads a measurement file or directory of files and returns the standardized DataFrame or list of DataFrames.
    The config determines the reader, formatter and mapper to use.

    Parameters
    ----------
    config : ReadConfig or str
        The configuration to use for standardizing the file or directory.
    input_path : object
        The path to the file or directory to standardize.
    keep_all_additional_data : bool, optional
        Whether to keep all additional data in the output DataFrame. If False, any
        columns not specified in the configuration will be dropped. Defaults to
        False.
    custom_folder_path : str, optional
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.

    Returns
    -------
    pd.DataFrame or list[pd.DataFrame]
        The standardized DataFrame or list of DataFrames.
    """
    # Validate boolean parameter using guardrail
    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    # TODO: Docstring
    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            return _convert_file(config, input_path, None, keep_all_additional_data, custom_folder_path)
        elif os.path.isdir(input_path):
            return _convert_files_in_directory(config, input_path, None, keep_all_additional_data, custom_folder_path)
        else:
            raise ValueError("Input path is invalid!")
    elif isinstance(input_path, list):
        dfs = []
        for input_item in input_path:
            if isinstance(input_item, str):
                if os.path.isfile(input_item):
                    dfs.append(_convert_file(config, input_item, None, keep_all_additional_data, custom_folder_path))
                elif os.path.isdir(input_item):
                    dfs.append(
                        _convert_files_in_directory(
                            config, input_item, None, keep_all_additional_data, custom_folder_path
                        )
                    )
                else:
                    raise ValueError("Input path item is invalid!")
            else:
                raise ValueError("Input path item is of invalid type!")
        return dfs
    else:
        raise ValueError("Input path is of invalid type!")

from __future__ import annotations

import gc
import os
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


def custom_read_csv(
    file_name: str,
    data_folder: str,
    reformat_cols: str = None,
    hide_print: bool = True,
    include_cols: list[str] = None,
    use_polars: bool = False,
    read_by_chunk: bool = False,
    force_str_format: bool = False,
) -> pd.DataFrame:
    """
    Read CSV file and return DataFrame

    Args:
        - file_name (str): File name
        - data_folder (str): Data folder path
        - reformat_cols (str): Column name formatting method ("upper", "lower", None)
        - hide_print (bool): Whether to hide print information
        - include_cols (list[str]): List of column names to read, if None then read all columns
        - use_polars (bool): Whether to use Polars library to read data
        - read_by_chunk (bool): Whether to read data by chunks
        - force_str_format (bool): Whether to force convert all columns to string format
    Returns:
        - pd.DataFrame: DataFrame containing the read CSV data
    """

    file_path = str(Path(data_folder).joinpath(file_name))
    if not os.path.exists(file_path) or not file_path.endswith(".csv"):
        raise ValueError(f"Invalid file path or file name: {file_path}. Please check the file name and path.")

    if not hide_print:
        print(f"\nReading {file_path}")

    try:
        if read_by_chunk:
            chunks = []

            for chunk in pd.read_csv(file_path, chunksize=100000, usecols=include_cols, dtype=str if force_str_format else None):
                chunks.append(chunk)
            df = pd.concat(chunks, ignore_index=True)
            del chunks
            gc.collect()
        else:
            if use_polars:
                try:
                    import polars as pl
                    import pyarrow

                    df = pl.read_csv(file_path, columns=include_cols, infer_schema=False if force_str_format else True).to_pandas()
                except ImportError:
                    df = pd.read_csv(
                        file_path,
                        usecols=include_cols,
                        dtype=str if force_str_format else None,
                        keep_default_na=False if force_str_format else True,
                    )
            else:
                df = pd.read_csv(
                    file_path,
                    usecols=include_cols,
                    dtype=str if force_str_format else None,
                    keep_default_na=False if force_str_format else True,
                )

    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found in {data_folder}. Please check the file name and path.")

    if reformat_cols == "upper":
        df.rename(columns=str.upper, inplace=True)
    elif reformat_cols == "lower":
        df.rename(columns=str.lower, inplace=True)
    else:
        pass

    if not hide_print:
        print(f"Read {df.shape[0]} rows and columns are: {df.columns.to_list()}\n")

    return df


def custom_save_csv(df: pd.DataFrame, data_folder: str, file_name: str, hide_print: bool = True, use_polars: bool = False) -> None:
    """
    Save DataFrame to CSV file

    Args:
        - df (pd.DataFrame): DataFrame to save
        - data_folder (str): Data folder path
        - file_name (str): File name, must end with .csv
        - hide_print (bool): Whether to hide print information
        - use_polars (bool): Whether to use Polars library to save data
    """

    os.makedirs(data_folder, exist_ok=True)
    file_path = str(Path(data_folder).joinpath(file_name))

    if not hide_print:
        print(f"\nSaving {file_path}")

    if not file_path.endswith(".csv"):
        raise ValueError(f"Invalid file name {file_name}. File name must end with .csv")

    if use_polars:
        try:
            import polars as pl
            import pyarrow

            pl_df = pl.from_pandas(df)
            pl_df.write_csv(file_path, separator=",", include_header=True, null_value="")
        except ImportError:
            df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)

    if not hide_print:
        print(f"Saved {df.shape[0]} rows and columns are: {df.columns.to_list()}")


def yaml_to_object(yaml_path: str, to_object: bool = True) -> dict | SimpleNamespace:
    """
    Read YAML configuration file and return as dictionary or SimpleNamespace object.

    Args:
        - yaml_file (str): YAML file path.
        - to_object (bool, optional): Whether to transform to Python SimpleNamespace object. Defaults to True.

    Returns:
        - dict | SimpleNamespace: Configuration data as dictionary or SimpleNamespace object
    """

    with open(yaml_path, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if to_object:
        data = SimpleNamespace(**data)

    return data
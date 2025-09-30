from __future__ import annotations

import gc
import os
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import yaml


def custom_read_csv(
    file_name: str = None,
    data_folder: str = None,
    file_path: str = None,
    columns: list[str] = None,
    column_case: str = None,
    column_case_sensitive: bool = True,
    use_polars: bool = False,
    chunked: bool = False,
    force_str_format: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Custom function to read a CSV file with various options.

    Args:
        - file_name (str, optional): Name of the CSV file to read. Required if file_path is not provided.
        - data_folder (str, optional): Folder path where the CSV file is located. Required if file_path is not provided.
        - file_path (str, optional): Full path to the CSV file. If provided, file_name and data_folder are ignored.
        - columns (list of str, optional): List of columns to read from the CSV. If None, all columns are read.
        - column_case (str, optional): If 'upper', convert column names to uppercase; if 'lower', convert to lowercase; if None, keep original case.
        - column_case_sensitive (bool, optional): If False, perform case-insensitive column matching. Default is True.
        - use_polars (bool, optional): If True, use Polars library for reading CSV. Default is False (uses pandas).
        - chunked (bool, optional): If True, read the CSV in chunks to save memory. Default is False.
        - force_str_format (bool, optional): If True, read all data as strings. Default is False.
        - verbose (bool, optional): If True, print progress messages. Default is True.

    Returns:
        - pd.DataFrame: DataFrame containing the requested data.
    """

    # Validate input parameters
    if column_case not in (None, "upper", "lower"):
        raise ValueError("Invalid column_case value. Choose from None, 'upper', 'lower'.")

    if (file_name is not None or data_folder is not None) and file_path is not None:
        raise ValueError("Provide either file_path or both file_name and data_folder, not both.")

    if not column_case_sensitive and columns is not None:
        # check if all columns are lowercase
        for col in columns:
            if not col.islower():
                raise ValueError("When column_case_sensitive is False, all columns in 'columns' must be lowercase.")

    # Construct file path if not provided
    if file_path is None:
        file_path = str(Path(data_folder).joinpath(file_name))

    # Check if file exists and is a CSV
    if not os.path.exists(file_path) or not file_path.endswith(".csv"):
        raise ValueError(f"Invalid file path or file name: {file_path}. Please check the file name and path.")

    # Read CSV file
    if verbose:
        print(f"\nReading {file_path} ...")

    # Case-sensitive column handling
    if not column_case_sensitive and columns is not None:
        print("Note: column_case_sensitive is False, performing case-insensitive column matching and output columns will be lowercase.")

        header_df = pd.read_csv(file_path, nrows=0)  # Read only the header to get actual column names
        lower_to_original = {col.lower(): col for col in header_df.columns}  # Map lowercase to original column names
        read_columns = []

        # For all requested columns, get the actual column names
        for col in columns:
            lower_col = col.lower()
            if lower_col in lower_to_original:
                read_columns.append(lower_to_original[lower_col])
            else:
                raise ValueError(f"Column '{col}' not found in file '{file_path}'")

        column_case = "lower"  # Ensure columns are converted to lowercase after reading

    elif not column_case_sensitive and columns is None:
        print("Warning: column_case_sensitive is False but no columns specified. Reading all columns as-is.")
        read_columns = columns

    else:
        print("Note: column_case_sensitive is True, performing case-sensitive column matching.")
        read_columns = columns

    # Read the CSV file with specified options
    if chunked:
        chunks = []

        for chunk in pd.read_csv(file_path, chunksize=100000, usecols=read_columns, dtype=str if force_str_format else None):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        del chunks
        gc.collect()

    else:
        if use_polars:
            try:
                import polars as pl
                import pyarrow

                df = pl.read_csv(file_path, columns=read_columns, infer_schema=False if force_str_format else True).to_pandas()
            except ImportError:
                df = pd.read_csv(
                    file_path,
                    usecols=read_columns,
                    dtype=str if force_str_format else None,
                    keep_default_na=False if force_str_format else True,
                )
        else:
            df = pd.read_csv(
                file_path,
                usecols=read_columns,
                dtype=str if force_str_format else None,
                keep_default_na=False if force_str_format else True,
            )

    # Reformat column names if needed
    if column_case == "upper":
        df.rename(columns=str.upper, inplace=True)
    elif column_case == "lower":
        df.rename(columns=str.lower, inplace=True)
    else:
        pass

    # Print summary
    if verbose:
        print(f"Read {df.shape[0]} rows and columns are: {df.columns.to_list()}\n")

    return df


def custom_save_csv(
    df: pd.DataFrame,
    file_name: str = None,
    data_folder: str = None,
    file_path: str = None,
    use_polars: bool = False,
    verbose: bool = True,
) -> None:
    """
    Custom function to save a DataFrame to a CSV file with various options.

    Args:
        - df (pd.DataFrame): DataFrame to save.
        - file_name (str, optional): Name of the CSV file to save. Required if file_path is not provided.
        - data_folder (str, optional): Folder path where the CSV file will be saved. Required if file_path is not provided.
        - file_path (str, optional): Full path to the CSV file. If provided, file_name and data_folder are ignored.
        - use_polars (bool, optional): If True, use Polars library for saving CSV. Default is False (uses pandas).
        - verbose (bool, optional): If True, print progress messages. Default is True.

    Returns:
        - None
    """

    # Validate input parameters
    if (file_name is not None or data_folder is not None) and file_path is not None:
        raise ValueError("Provide either file_path or both file_name and data_folder, not both.")

    # Construct file path if not provided
    if file_path is None:
        file_path = str(Path(data_folder).joinpath(file_name))

    # Check if file name ends with .csv
    if not file_path.endswith(".csv"):
        raise ValueError(f"Invalid file name {file_name}. File name must end with .csv")

    # Ensure the directory exists
    parent_dir = Path(file_path).parent
    os.makedirs(parent_dir, exist_ok=True)

    # Print progress message
    if verbose:
        print(f"\nSaving {file_path}")

    # Save DataFrame to CSV
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

    # Print summary
    if verbose:
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

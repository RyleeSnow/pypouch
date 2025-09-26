from __future__ import annotations

import inspect

import pandas as pd


def col_to_int(df: pd.DataFrame, cols_list: list[str], inplace: bool = True) -> pd.DataFrame | None:
    """
    Convert specified columns in a DataFrame from float or object type to int64 type.

    Args:
        df (pd.DataFrame): The DataFrame containing columns to be converted.
        cols_list (list[str]): List of column names to convert to int64 type.
        inplace (bool, optional): Whether to modify the original DataFrame in place. Defaults to True.
            - If True, modifies the original DataFrame directly.
            - If False, returns a new DataFrame with conversions applied.

    Returns:
        pd.DataFrame | None: Returns the converted DataFrame if inplace=False,
                             otherwise returns None and modifies the original DataFrame.

    Raises:
        ValueError: Raised when conversion fails for any specified column.
                    Error message includes the column name, DataFrame variable name
                    (if determinable), and the underlying exception details.
    """

    target_df = df if inplace else df.copy()

    for col in cols_list:

        if pd.api.types.is_integer_dtype(target_df[col]):  # already int type
            continue

        try:
            if pd.api.types.is_object_dtype(target_df[col]):  # object type
                try:
                    # convert to int
                    target_df[col] = target_df[col].astype("int64")
                except:
                    # convert via float if direct conversion fails
                    target_df[col] = target_df[col].astype(float).astype("int64")

            else:
                target_df[col] = target_df[col].astype("int64")

        except Exception as e:
            frame = inspect.currentframe().f_back
            df_name = [name for name, val in frame.f_locals.items() if val is df]
            df_name = df_name[0] if df_name else "Unknown DataFrame"
            raise ValueError(f"Warning: Failed to convert column {col} to int64 in {df_name}: {e}")

    if not inplace:
        return target_df


def col_to_float(df: pd.DataFrame, cols_list: list[str], inplace: bool = True) -> pd.DataFrame | None:
    """
    Convert specified columns in a DataFrame from float or object type to float64 type.

    Args:
        df (pd.DataFrame): The DataFrame containing columns to be converted.
        cols_list (list[str]): List of column names to convert to float64 type.
        inplace (bool, optional): Whether to modify the original DataFrame in place. Defaults to True.
            - If True, modifies the original DataFrame directly.
            - If False, returns a new DataFrame with conversions applied.

    Returns:
        pd.DataFrame | None: Returns the converted DataFrame if inplace=False,
                            otherwise returns None and modifies the original DataFrame.

    Raises:
        ValueError: Raised when conversion fails for any specified column.
                    Error message includes the column name, DataFrame variable name
                    (if determinable), and the underlying exception details.
    """

    target_df = df if inplace else df.copy()

    for col in cols_list:
        try:
            if pd.api.types.is_float_dtype(target_df[col]):  # already float type
                continue

            # convert to float
            target_df[col] = target_df[col].astype("float64")

        except Exception as e:
            frame = inspect.currentframe().f_back
            df_name = [name for name, val in frame.f_locals.items() if val is df]
            df_name = df_name[0] if df_name else "Unknown DataFrame"
            raise ValueError(f"Warning: Failed to convert column {col} to float64 in {df_name}: {e}")

    if not inplace:
        return target_df


def col_to_str(df: pd.DataFrame, cols_list: list, inplace: bool = True) -> pd.DataFrame | None:
    """
    Convert specified columns in a DataFrame from float or object type to str type.

    Args:
        df (pd.DataFrame): The DataFrame containing columns to be converted.
        cols_list (list[str]): List of column names to convert to str type.
        inplace (bool, optional): Whether to modify the original DataFrame in place. Defaults to True.
            - If True, modifies the original DataFrame directly.
            - If False, returns a new DataFrame with conversions applied.

    Returns:
        pd.DataFrame | None: Returns the converted DataFrame if inplace=False,
                            otherwise returns None and modifies the original DataFrame.

    Raises:
        ValueError: Raised when conversion fails for any specified column.
                    Error message includes the column name, DataFrame variable name
                    (if determinable), and the underlying exception details.
    """

    target_df = df if inplace else df.copy()

    for col in cols_list:
        try:
            if pd.api.types.is_string_dtype(target_df[col]):  # already string type
                continue

            # convert to string
            target_df[col] = target_df[col].astype("string")

        except Exception as e:
            frame = inspect.currentframe().f_back
            df_name = [name for name, val in frame.f_locals.items() if val is df]
            df_name = df_name[0] if df_name else "Unknown DataFrame"
            raise ValueError(f"Warning: Failed to convert column {col} to str in {df_name}: {e}")

    if not inplace:
        return target_df

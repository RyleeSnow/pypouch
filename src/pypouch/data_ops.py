from __future__ import annotations

import pandas as pd


def custom_dfs_concat(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate multiple DataFrames by rows

    Args:
        - df_list (list[pd.DataFrame]): List of DataFrames to concatenate
    Returns:
        - pd.DataFrame: Concatenated DataFrame
    """

    df_list = [df for df in df_list if df is not None and len(df) > 0]  # Filter out empty DataFrames

    if len(df_list) == 0:
        return pd.DataFrame()

    elif len(df_list) == 1:
        return df_list[0].copy()

    else:
        assert all([df_list[0].columns.equals(df.columns) for df in df_list]), "All DataFrames in df_list must have identical columns"
        return pd.concat(df_list, axis=0, ignore_index=True)


def combine_with_dollar_sign(
    df_prds: pd.DataFrame,
    id_col: str,
    time_tag_col: str,
    input_col: str,
    save_col: str,
    prds_lst: list[int | str],
    df_mth: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Combine multiple columns of data into one column using $ symbol

    Args:
        - df_prds (pd.DataFrame): Period data
            - Data example (showing only necessary columns):
              | id | time_tag | input_col |
              |----|----------|-----------|
              | A  | 202401   | 100       |
              | B  | 202401   | 200       |
              | A  | 202402   | 150       |
              | B  | 202402   | 250       |

        - id_col (str): ID column name
        - time_tag_col (str): Time tag column name
        - input_col (str): Input column name to be combined
        - save_col (str): Output column name to save combined data
        - prds_lst (list[int | str]): List of periods to combine (e.g., [202401, 202402, 202403])
        - df_mth (pd.DataFrame | None): Monthly data (optional)
            - If provided, will be used as base data
            - Data example:
              | id | other_col |
              |----|-----------|
              | A  | info_A    |
              | B  | info_B    |

    Returns:
        - pd.DataFrame: DataFrame with combined data
            - Output example:
              | id | save_col      | other_col |
              |----|---------------|-----------|
              | A  | 100$150$None  | info_A    |
              | B  | 200$250$None  | info_B    |

    Note:
        - Data will be combined in the order of prds_lst
        - Missing data will be filled with "None"
        - Combined format: "value1$value2$value3"
    """

    # Get unique IDs
    unique_ids = df_prds[id_col].unique()

    result_data = []
    for uid in unique_ids:
        combined_values = []
        for prd in prds_lst:
            # Get data for current ID and period
            mask = (df_prds[id_col] == uid) & (df_prds[time_tag_col] == prd)
            prd_data = df_prds[mask]

            if len(prd_data) > 0:
                value = prd_data[input_col].iloc[0]
                combined_values.append(str(value) if pd.notna(value) else "None")
            else:
                combined_values.append("None")

        # Create combined string
        combined_str = "$".join(combined_values)
        result_data.append({id_col: uid, save_col: combined_str})

    # Create result DataFrame
    result_df = pd.DataFrame(result_data)

    # If monthly data provided, merge with it
    if df_mth is not None:
        result_df = df_mth.merge(result_df, on=id_col, how="left")

    return result_df


def fix_decimal_id(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """
    Fix IDs that are stored as decimal numbers by converting them to strings without decimal points

    Args:
        - df (pd.DataFrame): Input DataFrame
        - id_col (str): ID column name to clean
    Returns:
        - pd.DataFrame: DataFrame with cleaned IDs
    """

    def _fix_decimal_id(id_val):
        try:
            # If float, convert to int then string
            if isinstance(id_val, float):
                return str(int(id_val))
            # If string with decimal point, remove decimal part
            elif isinstance(id_val, str) and "." in id_val:
                return id_val.split(".")[0]
            # Otherwise convert directly to string
            else:
                return str(id_val)
        except Exception:
            return str(id_val)

    df[id_col] = df[id_col].apply(_fix_decimal_id)
    df[id_col] = df[id_col].astype("string")
    return df


def has_decimal_values(df: pd.DataFrame, col_name: str) -> float | None:
    """
    Check if the specified column contains real decimal values

    Args:
        - df (pd.DataFrame): Input DataFrame
        - col_name (str): Column name to check

    Returns:
        - float | None: If decimal values exist, return the first decimal value found; otherwise return None
    """

    series = df[col_name].dropna()

    for value in series:
        try:
            str_val = str(value)
            if "." in str_val:
                str_val = str_val.rstrip("0")
                if not str_val.endswith("."):
                    return value
        except (ValueError, TypeError):
            continue

    return None

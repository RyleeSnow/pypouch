from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import pandas as pd

try:
    # Try relative import first (when used as a package)
    from .datatype_utils import col_to_str
except ImportError:
    # Fallback to direct import (when run as script)
    from datatype_utils import col_to_str


def control_decimal_precision(df: pd.DataFrame, cols_list: list[str], n: int) -> pd.DataFrame:
    """
    Control decimal precision of specified columns in DataFrame

    Args:
        - df (pd.DataFrame): DataFrame to be processed
        - cols_list (list[str]): List of column names to process
        - n (int): Number of decimal places to keep when rounding

    Returns:
        - pd.DataFrame: Copy of processed DataFrame
    """

    if n < 0:
        raise ValueError("Parameter n must be a non-negative integer representing the number of decimal places to keep.")

    df_copy = df.copy()

    for column in cols_list:
        df_copy[column] = df_copy[column].apply(lambda x: _format_decimal(x, n))

    col_to_str(df_copy, cols_list)

    return df_copy


def _format_decimal(value: float | int | str | None, n: int) -> str:
    """
    Format a single numeric value: round to n decimal places, remove trailing zeros, and return as string

    Args:
        - value (float | int | str | None): Numeric value to process
        - n (int): Number of decimal places to keep

    Returns:
        - str: Formatted string (NA values return empty string)
    """

    try:
        # If value is null, return empty string
        if pd.isna(value):
            return ""

        # Check if value is positive or negative infinity
        if isinstance(value, (int, float)) and (value == float("inf") or value == float("-inf")):
            return ""

        # Convert to Decimal for precise calculation
        decimal_value = Decimal(str(value))

        # Round to n decimal places
        quantized = decimal_value.quantize(Decimal("0." + "0" * n), rounding=ROUND_HALF_UP)

        # Convert to string and intelligently remove trailing zeros
        result_str = str(quantized)

        # If there is a decimal point
        if "." in result_str:
            # Remove trailing zeros
            result_str = result_str.rstrip("0")
            # If all decimal digits are 0, keep one 0 (e.g., "2." becomes "2.0")
            if result_str.endswith("."):
                result_str += "0"

        # Return string directly
        return result_str

    except (ValueError, TypeError, InvalidOperation):
        # Handle exception scenarios: invalid strings (cannot convert to Decimal), type errors, numeric overflow, etc., return empty string for subsequent processing
        return ""

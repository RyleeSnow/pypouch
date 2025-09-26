"""
PyPouch - A collection of utility functions for Python data processing

This package provides various utility functions for:
- Time and date operations
- DataFrame manipulations  
- Data type conversions
- Precision control
- I/O operations
- Logging setup
- String formatting
- Function utilities
- Display utilities
- Notification services

Usage:
    from pypouch import *
    
    # Time operations
    cal = CalendarCal("202401")
    dates = cal.dates_lst
    
    # Time difference calculation
    start_time = time.time()
    # ... some processing ...
    time_diff = get_time_dif(start_time)
    
    # Data operations
    df_combined = custom_dfs_concat([df1, df2], ["id"])
    
    # Type conversions
    col_to_str(df, ["col1", "col2"])
    
    # Precision control  
    df_precise = control_decimal_precision(df, ["amount"], 2)
    
    # I/O operations
    df = custom_read_csv("data.csv", "./data")
    custom_save_csv(df, "./output", "result.csv")
    config = yaml_to_object("config.yaml")
"""

# Data operations (DataFrame manipulation and data cleaning)
from .data_ops import (
    combine_with_dollar_sign,
    custom_dfs_concat,
    fix_decimal_id,
    has_decimal_values,
)

# Data type operations (Type conversions)
from .datatype_utils import col_to_float, col_to_int, col_to_str

# Function utilities
from .func_utils import filter_kwargs

# I/O operations
from .io_ops import custom_read_csv, custom_save_csv, yaml_to_object

# Logger setup
from .logger_utils import setup_logger

# Notification utilities
from .notification_utils import email_notification, wechat_notification

# Precision control
from .precision_control import _format_decimal, control_decimal_precision

# Time operations
from .time_utils import CalendarCal, get_time_dif

# Display utilities (if exists)
# Note: display_utils.py not found, skipping import

__version__ = "0.1.0"
__author__ = "RyleeSnow"

# Main exports for `from pypouch import *`
__all__ = [
    # Time operations
    "CalendarCal",
    "get_time_dif",
    
    # Data operations
    "custom_dfs_concat",
    "combine_with_dollar_sign",
    "fix_decimal_id", 
    "has_decimal_values",
    
    # Type operations
    "col_to_int",
    "col_to_float",
    "col_to_str",
    
    # Precision control
    "control_decimal_precision",
    "_format_decimal",
    
    # I/O operations
    "custom_read_csv",
    "custom_save_csv",
    "yaml_to_object",
    
    # Formatting
    "fix_decimal_id",
    
    # Function utilities
    "filter_kwargs",
    
    # Logger
    "setup_logger",
    
    # Notifications
    "email_notification",
    "wechat_notification",
]

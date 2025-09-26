# PyPouch 🛍️

A lightweight Python toolkit for data processing and analysis workflows.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PyPouch provides a collection of utility functions designed to streamline common data processing tasks. It focuses on pandas DataFrame operations, precision control, time calculations, and I/O operations with a clean, intuitive API.

<br>

## Key Features

- **📅 Time Utilities**: Calendar calculations, date range generation, and period management
- **🔢 Precision Control**: Robust decimal precision handling with intelligent rounding
- **📊 Data Operations**: DataFrame concatenation, ID cleaning, and data combination tools  
- **🔄 Type Conversions**: Safe and reliable column type conversions
- **📁 I/O Operations**: Enhanced CSV reading/writing with optional Polars backend
- **📋 Logging**: Structured logging setup with customizable formatters
- **📢 Notifications**: Email and WeChat message notifications
- **📋 List Operations**: Set operations for lists (intersection, difference, union, symmetric difference)
- **📋 List Operations**: Set operations for lists (intersection, difference, union, symmetric difference)

<br>

## Quick Start

### Installation

```bash
pip install pypouch
```

### Basic Usage

```python
from pypouch import *
import pandas as pd

# Time operations - Generate date ranges and calculate time differences
cal = CalendarCal("202401")
weekly_dates = cal.dates_lst  # Get all dates in weekly format
sundays = cal.wks_lst        # Get all Sundays in the month

# Time difference calculation
start_time = time.time()
# ... your processing code here ...
time_elapsed = get_time_dif(start_time)  # Returns timedelta object

# Data operations - Clean and combine DataFrames  
df_clean = custom_dfs_concat([df1, df2, df3])
df_fixed = fix_decimal_id(df, "id_column")

# Advanced data processing with multiprocessing and groupby operations
df_processed = dataframe_mp(large_df, processing_func, mp_cpus=4)
df_aggregated = lambda_groupby(lambda x: x['sales'].sum(), df, ['region', 'month'], 'total_sales')

# Precision control - Handle floating point precision
df_precise = control_decimal_precision(df, ["price", "amount"], 2)

# Type conversions - Safe column type changes
col_to_str(df, ["id", "category"])
col_to_float(df, ["revenue", "cost"])

# Enhanced I/O - Read/write CSV with optimizations and YAML configs
df = custom_read_csv("data.csv", "./input", use_polars=True)
custom_save_csv(df, "./output", "results.csv")
config = yaml_to_object("config.yaml")  # Load YAML as SimpleNamespace object

# Notifications - Send messages via email or WeChat
email_notification("Job Complete", "Data processing finished", 
                  mail_host, mail_user, mail_pass, sender, receivers)
wechat_notification("Alert", "Process completed successfully", sendkey)

# List operations - Set operations for lists
list1 = [1, 2, 3, 4]
list2 = [3, 4, 5, 6]
common = list_inter(list1, list2)      # [3, 4]
unique_in_1 = list_diff(list1, list2)  # [1, 2]
all_items = list_union(list1, list2)   # [1, 2, 3, 4, 5, 6]
sym_diff = list_sym_diff(list1, list2) # [1, 2, 5, 6]
```

<br>

## Core Components

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `time_utils` | Date/time calculations | `CalendarCal` class for period management, `get_time_dif()` for timing |
| `precision_control` | Decimal precision | `control_decimal_precision()` for accurate rounding |
| `data_ops` | DataFrame operations | `custom_dfs_concat()`, `fix_decimal_id()`, `dataframe_mp()`, `lambda_groupby()` |
| `datatype_utils` | Type conversions | `col_to_str()`, `col_to_float()`, `col_to_int()` |
| `io_ops` | File I/O | `custom_read_csv()`, `custom_save_csv()`, `yaml_to_object()` |
| `logger_utils` | Logging setup | `setup_logger()` with colored output |
| `list_utils` | List operations | `list_inter()`, `list_diff()`, `list_union()`, `list_sym_diff()` |
| `notification_utils` | Message notifications | `email_notification()`, `wechat_notification()` |

<br>

## Requirements

- Python 3.9+
- pandas
- yaml
- Optional: polars (for enhanced I/O performance)

<br>

## Development

```bash
# Clone the repository
git clone https://github.com/RyleeSnow/pypouch.git
cd pypouch

# Install development dependencies
pip install -e .

# Run tests
pytest unit_test/
```

<br>

## License

MIT License - see [LICENSE](LICENSE) file for details.
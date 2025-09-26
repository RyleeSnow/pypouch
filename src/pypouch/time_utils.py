from __future__ import annotations

import pandas as pd


class CalendarCal:

    def __init__(self, yr_mth: str, dt_fmt: str = "%Y%m%d", time_dim: str = "weekly"):
        """
        Date calculation utility class

        Args:
            - yr_mth (str): Year-month string in "YYYYMM" format
            - dt_fmt (str): Date format, defaults to "YYYYMMDD"
            - time_dim (str): Time dimension, defaults to "weekly"
        """

        self.yr_mth = yr_mth
        assert len(yr_mth) == 6 and yr_mth.isdigit(), f"Invalid year-month format: {yr_mth}, should be YYYYMM with all digits"
        
        self.yr = int(yr_mth[:4])
        assert 2000 <= self.yr <= 2050, f"Year {self.yr} is not within supported range (2000-2050)"
        self.mth = int(yr_mth[4:6])
        assert 1 <= self.mth <= 12, f"Month {self.mth} is not within supported range (1-12)"

        self.days_in_month = pd.Period(f"{self.yr}-{self.mth:02d}").days_in_month  # Days in month

        self.dt_fmt = dt_fmt
        self.time_dim = time_dim

    @property
    def wks_lst(self) -> list:
        """Calculate all weeks in the current month"""

        weeks = pd.date_range(f"{self.yr}-{self.mth:02d}-01", f"{self.yr}-{self.mth:02d}-{self.days_in_month}", freq="W-SUN")
        wks_lst = weeks.strftime(self.dt_fmt).tolist()

        return wks_lst

    @property
    def dates_lst(self) -> list:
        """Calculate all dates corresponding to the current month"""

        if self.time_dim == "weekly":
            # If weekly dimension: Monday corresponding to first Sunday of the month >> last Sunday of the month
            first_monday = pd.to_datetime(self.wks_lst[0], format=self.dt_fmt) - pd.DateOffset(days=6)  # Monday of the first week
            first_monday_str = first_monday.strftime(self.dt_fmt)

            all_dates = pd.date_range(first_monday_str, self.wks_lst[-1], freq="D")
            dates_lst = all_dates.strftime(self.dt_fmt).tolist()

        elif self.time_dim in ["half_month", "monthly"]:
            # If half-month or monthly dimension: 1st of the month >> last day of the month
            all_dates = pd.date_range(f"{self.yr}-{self.mth:02d}-01", f"{self.yr}-{self.mth:02d}-{self.days_in_month}", freq="D")
            dates_lst = all_dates.strftime(self.dt_fmt).tolist()

        else:
            raise ValueError(f"Unsupported time_dim value: {self.time_dim}, must be `weekly`, `half_month` or `monthly`")

        return dates_lst

    @property
    def next_month_start_date(self) -> str:
        """Calculate the first day of next month"""
        return (pd.to_datetime(f"{self.yr}-{self.mth:02d}-01") + pd.DateOffset(months=1)).strftime(self.dt_fmt)

    @property
    def current_month_last_date(self) -> str:
        """Get the last day of current month"""
        return pd.to_datetime(f"{self.yr}-{self.mth:02d}-{self.days_in_month}").strftime(self.dt_fmt)

    @property
    def last_month(self) -> str:
        """Get the year-month string of last month (fixed format: YYYYMM)"""
        return (pd.Period(self.yr_mth, freq="M") - 1).strftime("%Y%m")

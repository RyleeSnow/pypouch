import calendar
from datetime import datetime

import pandas as pd
import pytest

from pypouch import CalendarCal


def count_sundays(year, month):
    """
    Calculate the number of Sundays in a specified year and month.

    Args:
      year: Year (int)
      month: Month (int)

    Returns:
      Number of Sundays (int)
    """

    sunday_count = 0
    month_calendar = calendar.monthcalendar(year, month)

    for week in month_calendar:
        # week[calendar.SUNDAY] represents the date of Sunday in that week
        # If it's not 0, it means this Sunday is in this month
        if week[calendar.SUNDAY] != 0:
            sunday_count += 1

    return sunday_count


class TestCalendarCal:
    """Test various functionalities of the CalendarCal class"""

    def test_init_valid_input(self):
        """Test normal initialization parameters"""
        cal = CalendarCal("202512")
        assert cal.yr_mth == "202512"
        assert cal.yr == 2025
        assert cal.mth == 12
        assert cal.dt_fmt == "%Y%m%d"
        assert cal.time_dim == "weekly"
        assert cal.days_in_month == 31

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters"""
        cal = CalendarCal("202506", dt_fmt="%Y-%m-%d", time_dim="monthly")
        assert cal.yr_mth == "202506"
        assert cal.yr == 2025
        assert cal.mth == 6
        assert cal.dt_fmt == "%Y-%m-%d"
        assert cal.time_dim == "monthly"
        assert cal.days_in_month == 30

    def test_init_invalid_format(self):
        """Test invalid year-month format"""
        with pytest.raises(AssertionError, match="Invalid year-month format"):
            CalendarCal("2025")

        with pytest.raises(AssertionError, match="Invalid year-month format"):
            CalendarCal("20231")

        with pytest.raises(AssertionError, match="Invalid year-month format"):
            CalendarCal("2023123")

    def test_different_month_days(self):
        """Test the number of days in different months"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]  # Include leap years and non-leap years
        for yr in test_year_lst:
            # Months with 31 days
            for month in ["01", "03", "05", "07", "08", "10", "12"]:
                cal = CalendarCal(f"{yr}{month}")
                assert cal.days_in_month == 31

            # Months with 30 days
            for month in ["04", "06", "09", "11"]:
                cal = CalendarCal(f"{yr}{month}")
                assert cal.days_in_month == 30

            # Number of days in February
            cal = CalendarCal(f"{yr}02")
            if (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0):
                assert cal.days_in_month == 29
            else:
                assert cal.days_in_month == 28

    def test_wks_lst_basic(self):
        """Test basic weekly list functionality"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}")
                weeks = cal.wks_lst

                # Verify it returns a list
                assert isinstance(weeks, list)

                # Verify date format
                for week in weeks:
                    assert len(week) == 8  # YYYYMMDD format
                    datetime.strptime(week, cal.dt_fmt)  # Verify it's a valid date

                # Verify dates all belong to this month
                for week in weeks:
                    week_date = datetime.strptime(week, cal.dt_fmt)
                    assert week_date.year == yr
                    assert week_date.month == int(month)

                # Verify they are Sunday dates
                for week in weeks:
                    date_obj = datetime.strptime(week, cal.dt_fmt)
                    assert date_obj.weekday() == 6  # Sunday is 6

                # Verify the number of Sundays is correct
                assert len(weeks) == count_sundays(yr, int(month))

    def test_wks_lst_different_months(self):
        """Test weekly lists for different months"""

        # Test February 2024 (leap year)
        cal = CalendarCal("202402")
        weeks = cal.wks_lst
        assert weeks == ["20240204", "20240211", "20240218", "20240225"]

        # Test February 2025 (non-leap year)
        cal = CalendarCal("202502")
        weeks = cal.wks_lst
        assert weeks == ["20250202", "20250209", "20250216", "20250223"]

        # Test March 2024
        cal = CalendarCal("202403")
        weeks = cal.wks_lst
        assert weeks == ["20240303", "20240310", "20240317", "20240324", "20240331"]

        # Test January 2025
        cal = CalendarCal("202501")
        weeks = cal.wks_lst
        assert weeks == ["20250105", "20250112", "20250119", "20250126"]

        # Test June 2025
        cal = CalendarCal("202506")
        weeks = cal.wks_lst
        assert weeks == ["20250601", "20250608", "20250615", "20250622", "20250629"]

        # Test August 2025
        cal = CalendarCal("202508")
        weeks = cal.wks_lst
        assert weeks == ["20250803", "20250810", "20250817", "20250824", "20250831"]

        # Test December 2025
        cal = CalendarCal("202512")
        weeks = cal.wks_lst
        assert weeks == ["20251207", "20251214", "20251221", "20251228"]

    def test_dates_lst_weekly_basic(self):
        """Test weekly dimension date list"""
        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}", time_dim="weekly", dt_fmt="%Y-%m-%d")
                dates = cal.dates_lst

                # Verify it returns a list
                assert isinstance(dates, list)

                # Verify all date formats
                for date in dates:
                    assert len(date) == 10  # YYYY-MM-DD format
                    datetime.strptime(date, cal.dt_fmt)

                # Number of dates should be a multiple of 7
                assert len(dates) % 7 == 0
                assert len(dates) == 7 * count_sundays(yr, int(month))

                # Verify date continuity
                for i in range(1, len(dates)):
                    prev_date = datetime.strptime(dates[i - 1], cal.dt_fmt)
                    curr_date = datetime.strptime(dates[i], cal.dt_fmt)
                    assert (curr_date - prev_date).days == 1

                # Verify consistency with wks_lst
                assert dates[6] == cal.wks_lst[0]  # First week
                assert dates[-1] == cal.wks_lst[-1]  # Last week

    def test_dates_lst_weekly_different_months(self):
        """Test weekly dimension date lists for different months"""

        # February 2024 (leap year)
        cal = CalendarCal("202402", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20240129"
        assert dates[-1] == "20240225"

        # March 2024
        cal = CalendarCal("202403", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20240226"
        assert dates[-1] == "20240331"

        # January 2025
        cal = CalendarCal("202501", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20241230"
        assert dates[-1] == "20250126"

        # February 2025 (non-leap year)
        cal = CalendarCal("202502", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20250127"
        assert dates[-1] == "20250223"

        # June 2025
        cal = CalendarCal("202506", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20250526"
        assert dates[-1] == "20250629"

        # August 2025
        cal = CalendarCal("202508", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20250728"
        assert dates[-1] == "20250831"

        # December 2025
        cal = CalendarCal("202512", time_dim="weekly")
        dates = cal.dates_lst
        assert dates[0] == "20251201"
        assert dates[-1] == "20251228"

    def test_dates_lst_monthly_basic(self):
        """Test monthly dimension date list"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}", time_dim="monthly")
                dates = cal.dates_lst

                # Verify it returns a list
                assert isinstance(dates, list)

                # Verify all date formats
                for date in dates:
                    assert len(date) == 8  # YYYYMMDD format
                    datetime.strptime(date, cal.dt_fmt)

                # Verify dates all belong to this month
                for date in dates:
                    date_obj = datetime.strptime(date, cal.dt_fmt)
                    assert date_obj.year == yr
                    assert date_obj.month == int(month)

                # Verify the number of dates equals the number of days in the month
                assert len(dates) in [28, 29, 30, 31]
                assert len(dates) == calendar.monthrange(yr, int(month))[1]

                # Verify date continuity
                for i in range(1, len(dates)):
                    prev_date = datetime.strptime(dates[i - 1], cal.dt_fmt)
                    curr_date = datetime.strptime(dates[i], cal.dt_fmt)
                    assert (curr_date - prev_date).days == 1

                # Verify first and last day
                assert dates[0] == f"{yr}{month}01"
                assert dates[-1] == f"{yr}{month}{str(len(dates)).zfill(2)}"

    def test_dates_lst_monthly_different_months(self):
        """Test monthly dimension date lists for different months"""

        # December 2023
        cal = CalendarCal("202312", time_dim="monthly")
        dates = cal.dates_lst

        # Verify the number of dates equals the number of days in the month
        assert len(dates) == 31

        # Verify first and last day
        assert dates[0] == "20231201"
        assert dates[-1] == "20231231"

        # February 2024 (leap year)
        cal = CalendarCal("202402", time_dim="monthly")
        dates = cal.dates_lst

        # Verify leap year February has 29 days
        assert len(dates) == 29

        # Verify first and last day
        assert dates[0] == "20240201"
        assert dates[-1] == "20240229"

    def test_dates_lst_half_month(self):
        """Test half-month dimension date list"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}", time_dim="half_month")
                dates = cal.dates_lst

                cal_m = CalendarCal(f"{yr}{month}", time_dim="monthly")
                dates_m = cal_m.dates_lst

                # Half-month dimension and monthly dimension date lists should be the same
                assert dates == dates_m

    def test_dates_lst_invalid_time_dim(self):
        """Test invalid time dimension"""

        cal = CalendarCal("202312", time_dim="invalid")
        with pytest.raises(ValueError, match="Unsupported time_dim value"):
            _ = cal.dates_lst

    def test_next_month_start_date(self):
        """Test calculation of the first day of next month"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}")
                nmsd = cal.next_month_start_date

                # Verify date format
                assert len(nmsd) == 8  # YYYYMMDD format
                datetime.strptime(nmsd, cal.dt_fmt)

                # Verify it's always the 1st day
                assert nmsd.endswith("01")

                # Verify year transition and non-year transition
                if month != "12":  # If not crossing year, same year with month plus 1
                    expected_month = str(int(month) + 1).zfill(2)
                    assert nmsd.startswith(f"{yr}{expected_month}")
                else:
                    # Cross year, year plus 1, month is 01
                    assert nmsd.startswith(f"{yr + 1}01")

    def test_current_month_last_date(self):
        """Test calculation of the last day of current month"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}", dt_fmt="%Y-%m-%d")
                cmld = cal.current_month_last_date

                # Verify date format
                assert len(cmld) == 10  # YYYY-MM-DD format
                datetime.strptime(cmld, cal.dt_fmt)

                # Verify last day
                last_day = calendar.monthrange(yr, int(month))[1]
                assert cmld == f"{yr}-{month}-{last_day}"

    def test_last_month(self):
        """Test calculation of last month"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                cal = CalendarCal(f"{yr}{month}")
                lm = cal.last_month

                # Verify date format
                assert len(lm) == 6  # YYYYMM format
                datetime.strptime(lm, "%Y%m")

                # Verify year transition and non-year transition
                if month != "01":  # If not crossing year, same year with month minus 1
                    expected_month = str(int(month) - 1).zfill(2)
                    assert lm.startswith(f"{yr}{expected_month}")
                else:
                    # Cross year, year minus 1, month is 12
                    assert lm.startswith(f"{yr - 1}12")

    def test_property_consistency(self):
        """Test consistency between properties"""

        test_year_lst = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
        test_month_lst = [str(m).zfill(2) for m in range(1, 13)]

        for yr in test_year_lst:
            for month in test_month_lst:
                for td in ["weekly", "half_month", "monthly"]:
                    cal = CalendarCal(f"{yr}{month}", time_dim=td)
                    wks_lst = cal.wks_lst
                    dates_lst = cal.dates_lst
                    last_month = cal.last_month
                    next_month_start_date = cal.next_month_start_date
                    current_month_last_date = cal.current_month_last_date

                    # current_month_last_date and next_month_start_date should differ by 1 day
                    current_month_last_date_obj = datetime.strptime(current_month_last_date, cal.dt_fmt)
                    next_month_start_date_obj = datetime.strptime(next_month_start_date, cal.dt_fmt)
                    assert (next_month_start_date_obj - current_month_last_date_obj).days == 1

                    # last_month and next_month_start_date should differ by exactly 2 months, current_month_last_date should differ by 1 month from both
                    last_month_period = pd.Period(last_month, freq="M")
                    current_month_period = pd.Period(current_month_last_date, freq="M")
                    next_month_period = pd.Period(next_month_start_date, freq="M")
                    assert (next_month_period - last_month_period).n == 2
                    assert (current_month_period - last_month_period).n == 1
                    assert (next_month_period - current_month_period).n == 1

                    if td == "weekly":
                        # The first day of dates_lst and first day of wks_lst should differ by 6 days
                        first_date_obj = datetime.strptime(dates_lst[0], cal.dt_fmt)
                        first_week_obj = datetime.strptime(wks_lst[0], cal.dt_fmt)
                        assert (first_week_obj - first_date_obj).days == 6

                        # The last day of dates_lst and last day of wks_lst should be equal
                        assert dates_lst[-1] == wks_lst[-1]

                        # The last day of dates_lst and next_month_start_date should differ by no more than 7 days, and should differ by no more than 6 days from current_month_last_date
                        last_date_obj = datetime.strptime(dates_lst[-1], cal.dt_fmt)
                        assert 0 <= (next_month_start_date_obj - last_date_obj).days <= 7
                        assert 0 <= (current_month_last_date_obj - last_date_obj).days <= 6

                    else:
                        # The first day of dates_lst should be earlier than or equal to the first day of wks_lst but not more than 6 days
                        first_date_obj = datetime.strptime(dates_lst[0], cal.dt_fmt)
                        first_week_obj = datetime.strptime(wks_lst[0], cal.dt_fmt)
                        assert 0 <= (first_week_obj - first_date_obj).days <= 6

                        # The last day of dates_lst should be later than or equal to the last day of wks_lst but not more than 6 days
                        last_date_obj = datetime.strptime(dates_lst[-1], cal.dt_fmt)
                        last_week_obj = datetime.strptime(wks_lst[-1], cal.dt_fmt)
                        assert 0 <= (last_date_obj - last_week_obj).days <= 6

                        # The last day of dates_lst and next_month_start_date should differ by 1 day, and should be equal to current_month_last_date
                        assert (next_month_start_date_obj - last_date_obj).days == 1
                        assert (current_month_last_date_obj - last_date_obj).days == 0

    def test_performance_properties(self):
        """Test property performance and repeated calls"""
        cal = CalendarCal("202312")

        # Multiple calls to the same property should return the same result
        weeks1 = cal.wks_lst
        weeks2 = cal.wks_lst
        assert weeks1 == weeks2

        dates1 = cal.dates_lst
        dates2 = cal.dates_lst
        assert dates1 == dates2

        last_month1 = cal.last_month
        last_month2 = cal.last_month
        assert last_month1 == last_month2

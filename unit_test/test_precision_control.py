from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from pypouch import _format_decimal, control_decimal_precision


class TestFormatDecimal:
    """Test various input scenarios for the _format_decimal private function"""
    
    def test_normal_float_values(self):
        """Test normal floating-point values"""

        # Test basic rounding
        assert _format_decimal(12.345, 2) == "12.35"
        assert _format_decimal(12.344, 2) == "12.34"
        assert _format_decimal(12.346, 2) == "12.35"
        
        # Test different precisions
        assert _format_decimal(12.3456789, 0) == "12"
        assert _format_decimal(12.3456789, 1) == "12.3"
        assert _format_decimal(12.3456789, 3) == "12.346"
        assert _format_decimal(12.3456789, 5) == "12.34568"
    
    def test_trailing_zeros_removal(self):
        """Test removal of trailing zeros"""
        # Test intelligent removal of trailing zeros
        assert _format_decimal(12.100, 3) == "12.1"
        assert _format_decimal(12.000, 3) == "12.0"
        assert _format_decimal(12.300, 3) == "12.3"
        assert _format_decimal(12.560, 3) == "12.56"

        assert _format_decimal(12.100, 6) == "12.1"
        assert _format_decimal(12.000, 6) == "12.0"
        assert _format_decimal(12.300, 6) == "12.3"
        assert _format_decimal(12.560, 6) == "12.56"
        
        # Test integer cases
        assert _format_decimal(12.0, 2) == "12.0"
        assert _format_decimal(12, 2) == "12.0"
    
    def test_integer_values(self):
        """Test integer inputs"""
        assert _format_decimal(12, 0) == "12"
        assert _format_decimal(12, 1) == "12.0"
        assert _format_decimal(12, 2) == "12.0"
        assert _format_decimal(0, 5) == "0.0"
        assert _format_decimal(-5, 2) == "-5.0"
    
    def test_string_numeric_values(self):
        """Test string-form numeric values"""
        assert _format_decimal("12.345", 2) == "12.35"
        assert _format_decimal("12", 2) == "12.0"
        assert _format_decimal("0.999", 2) == "1.0"
        assert _format_decimal("-12.345", 2) == "-12.35"
    
    def test_negative_values(self):
        """Test negative values"""
        assert _format_decimal(-12.345, 2) == "-12.35"
        assert _format_decimal(-12.344, 2) == "-12.34"
        assert _format_decimal(-0.1, 1) == "-0.1"
        assert _format_decimal(-0.999, 2) == "-1.0"
        assert _format_decimal(-0.999, 3) == "-0.999"
        assert _format_decimal(-0.999, 5) == "-0.999"
    
    def test_very_small_values(self):
        """Test very small values"""
        assert _format_decimal(0.001, 2) == "0.0"
        assert _format_decimal(0.001, 3) == "0.001"
        assert _format_decimal(0.001, 4) == "0.001"
        assert _format_decimal(0.0001, 3) == "0.0"
        assert _format_decimal(0.0005, 3) == "0.001"
        assert _format_decimal(0.0005, 4) == "0.0005"
    
    def test_very_large_values(self):
        """Test very large values"""
        assert _format_decimal(999999.999, 2) == "1000000.0"
        assert _format_decimal(123456789.123456, 2) == "123456789.12"
        assert _format_decimal(1e10, 2) == "10000000000.0"

    def test_float_precision_issues_without_format(self):
        """Test floating-point precision issues without using _format_decimal"""
                
        assert str(0.1 + 0.2) != "0.3"
        assert _format_decimal(0.1 + 0.2, 2) == "0.3"
        assert str(0.1 * 3) != "0.3"
        assert _format_decimal(0.1 * 3, 1) == "0.3"
        
        # Test precision accumulation issues from continuous operations
        accumulated_error = 0.0
        for _ in range(10):
            accumulated_error += 0.1
        assert str(accumulated_error) != "1.0"
        assert _format_decimal(accumulated_error, 1) == "1.0"
                
        # Test precision issues from scientific notation conversion
        scientific_value = 1e-1 + 2e-1
        assert str(scientific_value) != "0.3"
        assert _format_decimal(scientific_value, 3) == "0.3"

    def test_edge_cases_float_precision(self):
        """Test edge cases of floating-point precision"""
        # Test floating-point numbers very close to integers
        almost_integers = [
            0.9999999999999999,  # Very close to 1
            1.9999999999999998,  # Very close to 2
            2.9999999999999996,  # Very close to 3
        ]
        
        for value in almost_integers:
            # Should correctly round to the nearest integer
            result = _format_decimal(value, 0)
            expected_int = round(value)
            assert result == str(expected_int)
        
        # Test very small floating-point numbers
        tiny_values = [
            1e-15,  # Very small positive number
            1e-16,  # Even smaller number
        ]
        
        for value in tiny_values:
            # Should all be 0 at 2 decimal places
            assert _format_decimal(value, 2) == "0.0"
            # May show actual value at higher precision
            result_high_precision = _format_decimal(value, 16)
            # Verify result is reasonable
            if result_high_precision != "0.0":
                float(result_high_precision)  # Should be convertible back to float

    def test_financial_precision_scenarios(self):
        """Test precision issues in financial scenarios"""
        # Simulate common precision issues in price calculations
        base_price = 99.99
        discount_rate = 0.15
        
        # Calculate discount price
        discount_amount = base_price * discount_rate  # May have precision issues
        final_price = base_price - discount_amount
        
        # Process using _format_decimal
        formatted_discount = _format_decimal(discount_amount, 2)
        formatted_final = _format_decimal(final_price, 2)
        
        assert formatted_discount == "15.0"  # 99.99 * 0.15 = 14.9985
        assert formatted_final == "84.99"    # 99.99 - 14.9985 = 84.9915
        
        # Test tax calculation
        tax_rate = 0.08875  # 8.875% tax rate
        tax_amount = final_price * tax_rate
        total_with_tax = final_price + tax_amount
        
        formatted_tax = _format_decimal(tax_amount, 2)
        formatted_total = _format_decimal(total_with_tax, 2)
        
        # Verify results are reasonable monetary amounts
        assert '.' in formatted_tax
        assert '.' in formatted_total
        assert len(formatted_tax.split('.')[1]) <= 2 or formatted_tax.endswith('.0')
        assert len(formatted_total.split('.')[1]) <= 2 or formatted_total.endswith('.0')

    def test_percentage_precision_issues(self):
        """Test precision issues in percentage calculations"""
        # Common percentage calculation precision issues
        percentage_cases = [
            (1/3, 3, "0.333"),      # 33.33%
            (2/3, 3, "0.667"),      # 66.67%
            (1/7, 4, "0.1429"),     # 14.29%
            (22/7, 4, "3.1429"),    # Approximation of π
        ]
        
        for value, precision, expected in percentage_cases:
            result = _format_decimal(value, precision)
            assert result == expected
        
        # Test percentage conversion
        ratio = 0.12345
        percentage = ratio * 100
        formatted_percentage = _format_decimal(percentage, 2)
        assert formatted_percentage == "12.35"  # 12.35%
        
    def test_na_and_null_values(self):
        """Test various null and NA values"""
        # pandas NA值
        assert _format_decimal(pd.NA, 2) == ""
        assert _format_decimal(None, 2) == ""
        assert _format_decimal(np.nan, 2) == ""
        assert _format_decimal(float('nan'), 2) == ""
    
    def test_infinite_values(self):
        """Test infinite values"""
        assert _format_decimal(float('inf'), 2) == ""
        assert _format_decimal(float('-inf'), 2) == ""
        assert _format_decimal(np.inf, 2) == ""
        assert _format_decimal(-np.inf, 2) == ""
    
    def test_invalid_string_values(self):
        """Test invalid string inputs"""
        assert _format_decimal("abc", 2) == ""
        assert _format_decimal("12.34.56", 2) == ""
        assert _format_decimal("", 2) == ""
        assert _format_decimal("not_a_number", 2) == ""
    
    def test_edge_cases_precision(self):
        """Test edge cases of precision"""
        # Zero precision
        assert _format_decimal(12.9, 0) == "13"
        assert _format_decimal(12.1, 0) == "12"
        
        # High precision
        value = Decimal('12.123456789012345')
        assert _format_decimal(str(value), 10) == "12.123456789"
    
    def test_rounding_behavior(self):
        """Test rounding behavior"""
        # Test various rounding cases
        assert _format_decimal(2.5, 0) == "3"  # Round up
        assert _format_decimal(1.5, 0) == "2"  # Round up
        assert _format_decimal(2.25, 1) == "2.3"  # Round up
        assert _format_decimal(2.15, 1) == "2.2"  # Round up
        assert _format_decimal(2.125, 2) == "2.13"  # Round up


class TestControlDecimalPrecision:
    """Test DataFrame processing functionality of control_decimal_precision function"""
    
    def setup_method(self):
        """Setup before each test method execution"""
        # Create test DataFrame containing various data types
        self.test_df = pd.DataFrame({
            'price': [12.3456, 45.6700, 78.90002, 100.000090, np.nan, None, pd.NA],
            'discount': [0.1200, 0.2500, 0.3000, 0.0000, None, np.nan, float('inf')],
            'quantity': [1, 2, 3, 4, 5, 6, 7],  # Integer column, no processing needed
            'name': ['产品A', '产品B', '产品C', '产品D', '产品E', '产品F', '产品G']  # String column
        })
    
    def test_single_column_processing(self):
        """Test single column processing"""
        result = control_decimal_precision(self.test_df, ['price'], 2)
        
        # Verify processed values
        expected_prices = ["12.35", "45.67", "78.9", "100.0", "", "", ""]
        assert result['price'].tolist() == expected_prices
        
        # Verify column type is string
        assert pd.api.types.is_string_dtype(result['price'])
        
        # Verify other columns are not modified
        pd.testing.assert_series_equal(result['quantity'], self.test_df['quantity'])
        pd.testing.assert_series_equal(result['name'], self.test_df['name'])
    
    def test_multiple_columns_processing(self):
        """Test multiple column processing"""
        result = control_decimal_precision(self.test_df, ['price', 'discount'], 2)
        
        # Verify price column
        expected_prices = ["12.35", "45.67", "78.9", "100.0", "", "", ""]
        assert result['price'].tolist() == expected_prices
        
        # Verify discount column
        expected_discounts = ["0.12", "0.25", "0.3", "0.0", "", "", ""]
        assert result['discount'].tolist() == expected_discounts
        
        # Verify both columns are converted to string type
        assert pd.api.types.is_string_dtype(result['price'])
        assert pd.api.types.is_string_dtype(result['discount'])
    
    def test_different_precisions(self):
        """Test different precision settings"""
        # Test 0 decimal places
        result_0 = control_decimal_precision(self.test_df, ['price'], 0)
        expected_0 = ["12", "46", "79", "100", "", "", ""]
        assert result_0['price'].tolist() == expected_0
        
        # Test 1 decimal place
        result_1 = control_decimal_precision(self.test_df, ['price'], 1)
        expected_1 = ["12.3", "45.7", "78.9", "100.0", "", "", ""]
        assert result_1['price'].tolist() == expected_1
        
        # Test 3 decimal places
        result_3 = control_decimal_precision(self.test_df, ['price'], 3)
        expected_3 = ["12.346", "45.67", "78.9", "100.0", "", "", ""]
        assert result_3['price'].tolist() == expected_3
    
    def test_original_dataframe_unchanged(self):
        """Test that the original DataFrame is not modified"""
        original_df_copy = self.test_df.copy()
        
        # Execute processing
        result = control_decimal_precision(self.test_df, ['price'], 2)
        
        # Verify original DataFrame is not modified
        pd.testing.assert_frame_equal(self.test_df, original_df_copy)
        
        # Verify a new DataFrame is returned
        assert result is not self.test_df
    
    def test_empty_column_list(self):
        """Test empty column name list"""
        result = control_decimal_precision(self.test_df, [], 2)
        
        # Should return a copy of the original DataFrame, but no columns processed
        pd.testing.assert_frame_equal(result, self.test_df)
        assert result is not self.test_df  # Ensure it's a copy
    
    def test_nonexistent_column(self):
        """Test processing non-existent column names"""
        with pytest.raises(KeyError):
            control_decimal_precision(self.test_df, ['nonexistent_column'], 2)
    
    def test_mixed_data_types_in_column(self):
        """Test columns containing mixed data types"""
        mixed_df = pd.DataFrame({
            'mixed_col': [12.34, '56.78', None, np.nan, 'abc', 90, float('inf')]
        })
        
        result = control_decimal_precision(mixed_df, ['mixed_col'], 2)
        expected = ["12.34", "56.78", "", "", "", "90.0", ""]
        assert result['mixed_col'].tolist() == expected
    
    def test_all_na_column(self):
        """Test columns with all NA values"""
        na_df = pd.DataFrame({
            'na_col': [np.nan, None, pd.NA, float('nan')]
        })
        
        result = control_decimal_precision(na_df, ['na_col'], 2)
        expected = ["", "", "", ""]
        assert result['na_col'].tolist() == expected
    
    
    def test_very_large_precision(self):
        """Test very large precision values"""
        simple_df = pd.DataFrame({'value': [12.3456789]})
        result = control_decimal_precision(simple_df, ['value'], 10)
        expected = ["12.3456789"]
        assert result['value'].tolist() == expected
    
    def test_special_float_values(self):
        """Test special floating-point values"""
        special_df = pd.DataFrame({
            'special': [0.0, -0.0, 1e-10, 1e10, 2.2250738585072014e-308]  # Including very small values
        })
        
        result = control_decimal_precision(special_df, ['special'], 2)
        expected = ["0.0", "-0.0", "0.0", "10000000000.0", "0.0"]
        assert result['special'].tolist() == expected


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_real_world_price_data(self):
        """Test real-world price data scenarios"""
        price_df = pd.DataFrame({
            'product_id': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'original_price': [99.999, 149.50, 299.001, 0.01, 1999.999],
            'discount_rate': [0.1, 0.15, 0.2, 0.05, 0.0],
            'final_price': [89.999, 127.075, 239.2008, 0.0095, 1999.999]
        })
        
        # Process price-related columns, keeping 2 decimal places
        result = control_decimal_precision(
            price_df, 
            ['original_price', 'discount_rate', 'final_price'], 
            2
        )
        
        # Verify results
        assert result['original_price'].tolist() == ["100.0", "149.5", "299.0", "0.01", "2000.0"]
        assert result['discount_rate'].tolist() == ["0.1", "0.15", "0.2", "0.05", "0.0"]
        assert result['final_price'].tolist() == ["90.0", "127.08", "239.2", "0.01", "2000.0"]
        
        # Verify product_id column is not modified
        assert result['product_id'].tolist() == price_df['product_id'].tolist()
    
    def test_financial_calculation_scenario(self):
        """Test financial calculation scenarios"""
        financial_df = pd.DataFrame({
            'revenue': [1234567.8901, 987654.3210, 555555.5555],
            'cost': [888888.8888, 666666.6666, 333333.3333],
            'profit_margin': [0.123456789, 0.987654321, 0.456789123]
        })
        
        # Amounts keep 2 decimal places, profit margin keeps 4 decimal places
        revenue_result = control_decimal_precision(financial_df, ['revenue', 'cost'], 2)
        margin_result = control_decimal_precision(revenue_result, ['profit_margin'], 4)
        
        assert margin_result['revenue'].tolist() == ["1234567.89", "987654.32", "555555.56"]
        assert margin_result['cost'].tolist() == ["888888.89", "666666.67", "333333.33"]
        assert margin_result['profit_margin'].tolist() == ["0.1235", "0.9877", "0.4568"]
    
    def test_empty_dataframe(self):
        """Test empty DataFrame"""
        empty_df = pd.DataFrame()
        result = control_decimal_precision(empty_df, [], 2)
        
        assert result.empty
        assert result is not empty_df  # Ensure a copy is returned
    
    def test_single_row_dataframe(self):
        """Test single-row DataFrame"""
        single_row_df = pd.DataFrame({
            'value': [123.456789]
        })
        
        result = control_decimal_precision(single_row_df, ['value'], 3)
        assert result['value'].tolist() == ["123.457"]
    
    def test_large_dataframe_performance(self):
        """Test large DataFrame performance (simple verification)"""
        # Create a larger DataFrame
        large_df = pd.DataFrame({
            'values': np.random.uniform(0, 1000, 1000).tolist()
        })
        
        # Mainly verify no errors occur, not specific performance
        result = control_decimal_precision(large_df, ['values'], 2)
        
        assert len(result) == 1000
        assert pd.api.types.is_string_dtype(result['values'])
        
        # Verify all values are valid numeric strings or empty strings
        for value in result['values']:
            if value != "":
                # Should be convertible back to number
                float(value)

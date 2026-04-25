# Map raw-data column names (left) to standardized column names (right)
_COLUMN_MAP = {
    "step": "Step_Count",
    "impedance_frequency": "EIS_f[Hz]",
    "real impedance": "EIS_Z_Real[Ohm]",
    "imaginary impedance": "EIS_Z_Imag[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
_MISSING_REQUIRED_COLUMNS = [
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Test_Time[s]",
    "Date_Time",
    "EIS_DC[A]",
]

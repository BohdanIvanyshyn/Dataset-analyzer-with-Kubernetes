import pandas as pd


def detect_column_type(series):
    # Numeric columns
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # Date columns
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"

    # Try to detect dates stored as strings
    if series.dtype == "object":
        non_null = series.dropna()

        if len(non_null) > 0:
            converted = pd.to_datetime(
                non_null,
                errors="coerce"
            )

            if converted.notna().mean() > 0.8:
                return "date"

    # Empty column
    if series.dropna().empty:
        return "unknown"

    # Likely ID
    unique_ratio = series.nunique() / len(series)

    if unique_ratio > 0.95:
        return "likely ID"

    # Categorical
    if unique_ratio < 0.1:
        return "categorical"

    # Everything else
    return "text"


def detect_outliers(df):
    outliers = {}

    numeric_columns = df.select_dtypes(include="number").columns

    for col in numeric_columns:
        series = df[col].dropna()

        if series.empty:
            outliers[col] = 0
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = (
            (series < lower_bound) |
            (series > upper_bound)
        ).sum()

        outliers[col] = int(outlier_count)

    return outliers


def generate_warnings(df, column_types, outliers):
    warnings = []

    # Missing value warnings
    for col in df.columns:
        missing_percentage = df[col].isnull().mean() * 100

        if missing_percentage >= 50:
            warnings.append(
                f"{col} has {missing_percentage:.1f}% missing values."
            )

        elif missing_percentage >= 20:
            warnings.append(
                f"{col} has {missing_percentage:.1f}% missing values."
            )

    # Likely ID warnings
    for col, column_type in column_types.items():
        if column_type == "likely ID":
            warnings.append(
                f"{col} appears to be a likely ID column."
            )

    # Constant column warnings
    for col in df.columns:
        if df[col].nunique(dropna=False) <= 1:
            warnings.append(
                f"{col} contains only one unique value."
            )

    # Outlier warnings
    for col, count in outliers.items():
        if count > 0:
            percentage = (count / len(df)) * 100

            if percentage >= 10:
                warnings.append(
                    f"{col} contains {count} outliers ({percentage:.1f}% of rows)."
                )

    return warnings


def analyze(df):
    numeric_df = df.select_dtypes(include="number")

    column_types = {
        col: detect_column_type(df[col])
        for col in df.columns
    }

    outliers = detect_outliers(df)

    warnings = generate_warnings(
        df,
        column_types,
        outliers
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),

        "missing_values": df.isnull().sum().to_dict(),

        "data_types": df.dtypes.astype(str).to_dict(),

        "duplicate_rows": int(df.duplicated().sum()),

        "numeric_summary": df.describe().to_dict(),

        "categorical_frequencies": {
            col: df[col].value_counts(dropna=False).to_dict()
            for col in df.select_dtypes(
                include=["object", "category"]
            ).columns
        },

        "column_types": column_types,

        "outliers": outliers,

        "correlations": numeric_df.corr().to_dict(),

        "warnings": warnings
    }
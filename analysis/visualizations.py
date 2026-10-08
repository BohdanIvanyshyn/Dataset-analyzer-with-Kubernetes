import plotly.express as px


def create_histogram(df, column):
    fig = px.histogram(
        df,
        x=column,
        title=f"Distribution of {column}"
    )

    return fig.to_html(full_html=False)


def create_category_chart(df, column):
    counts = df[column].value_counts().head(15)

    fig = px.bar(
        x=counts.index,
        y=counts.values,
        title=f"Top Values in {column}",
        labels={
            "x": column,
            "y": "Count"
        }
    )

    return fig.to_html(full_html=False)


def create_missing_chart(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        return "<p>No missing values.</p>"

    fig = px.bar(
        x=missing.index,
        y=missing.values,
        title="Missing Values by Column",
        labels={
            "x": "Column",
            "y": "Missing Values"
        }
    )

    return fig.to_html(full_html=False)


def create_correlation_heatmap(df):
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return "<p>Not enough numeric columns for a correlation heatmap.</p>"

    correlation = numeric_df.corr()

    fig = px.imshow(
        correlation,
        text_auto=True,
        title="Correlation Matrix"
    )

    return fig.to_html(full_html=False)
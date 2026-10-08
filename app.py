from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
from io import BytesIO

from analysis.analyzer import analyze
from analysis.visualizations import (
    create_histogram,
    create_category_chart,
    create_missing_chart,
    create_correlation_heatmap
)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Data Explorer</title>
        </head>
        <body>
            <h1>Data Explorer</h1>

            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv">
                <button type="submit">Analyze Dataset</button>
            </form>
        </body>
    </html>
    """


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))

    result = analyze(df)

    # Create visualizations
    numeric_columns = df.select_dtypes(include="number").columns

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns

    histograms = "".join(
        create_histogram(df, col)
        for col in numeric_columns
    )

    category_charts = "".join(
        create_category_chart(df, col)
        for col in categorical_columns
    )

    missing_chart = create_missing_chart(df)

    correlation_heatmap = create_correlation_heatmap(df)

    return f"""
    <html>
        <head>
            <title>Data Explorer Results</title>
        </head>

        <body>
            <h1>Dataset Information</h1>

            <p><strong>File:</strong> {file.filename}</p>
            <p><strong>Rows:</strong> {result["rows"]}</p>
            <p><strong>Columns:</strong> {result["columns"]}</p>
            <p><strong>Duplicate rows:</strong> {result["duplicate_rows"]}</p>

            <h2>Warnings</h2>

            <ul>
                {"".join(
                    f"<li>{warning}</li>"
                    for warning in result["warnings"]
                )}
            </ul>

            <h2>Columns</h2>

            <ul>
                {"".join(
                    f"<li>{col}</li>"
                    for col in result["column_names"]
                )}
            </ul>

            <h2>Missing Values</h2>

            {pd.DataFrame.from_dict(
                result["missing_values"],
                orient="index",
                columns=["Missing Values"]
            ).to_html()}

            <h2>Data Types</h2>

            {pd.DataFrame.from_dict(
                result["data_types"],
                orient="index",
                columns=["Data Type"]
            ).to_html()}

            <h2>Column Type Detection</h2>

            {pd.DataFrame.from_dict(
                result["column_types"],
                orient="index",
                columns=["Detected Type"]
            ).to_html()}

            <h2>Numeric Summary</h2>

            {pd.DataFrame(
                result["numeric_summary"]
            ).to_html()}

            <h2>Outliers</h2>

            {pd.DataFrame.from_dict(
                result["outliers"],
                orient="index",
                columns=["Outlier Count"]
            ).to_html()}

            <h2>Categorical Frequencies</h2>

            {"".join(
                f'''
                <h3>{col}</h3>

                {pd.DataFrame.from_dict(
                    frequencies,
                    orient="index",
                    columns=["Count"]
                ).to_html()}
                '''
                for col, frequencies
                in result["categorical_frequencies"].items()
            )}

            <h2>Correlations</h2>

            {pd.DataFrame(
                result["correlations"]
            ).to_html()}

            <h1>Visualizations</h1>

            <h2>Missing Values</h2>

            {missing_chart}

            <h2>Numeric Distributions</h2>

            {histograms}

            <h2>Categorical Variables</h2>

            {category_charts}

            <h2>Correlation Heatmap</h2>

            {correlation_heatmap}

            <br>

            <a href="/">Analyze another dataset</a>
        </body>
    </html>
    """
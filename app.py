from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
from io import BytesIO

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

    return f"""
    <html>
        <head>
            <title>Data Explorer Results</title>
        </head>
        <body>
            <h1>Dataset Information</h1>

            <p><strong>File:</strong> {file.filename}</p>
            <p><strong>Rows:</strong> {len(df)}</p>
            <p><strong>Columns:</strong> {len(df.columns)}</p>

            <h2>Columns</h2>
            <ul>
                {"".join(f"<li>{col}</li>" for col in df.columns)}
            </ul>

            <h2>Missing Values</h2>
            {df.isnull().sum().to_frame("Missing Values").to_html()}

            <h2>Data Types</h2>
            {df.dtypes.to_frame("Data Type").to_html()}

            <br>
            <a href="/">Analyze another dataset</a>
        </body>
    </html>
    """
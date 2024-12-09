from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import os
from megaparse import MegaParse
from langchain_openai import ChatOpenAI
from megaparse.parser.megaparse_vision import MegaParseVision
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(
    title="Zartis PDF Parser API",
    description="API to parse PDFs and return their content as strings.",
    version="1.0.0",
)

# Initialize MegaParse with the model
model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))  # type: ignore
parser = MegaParseVision(model=model)
megaparse = MegaParse(parser)


@app.post("/parse", summary="Parse PDF", description="Parses a single PDF file and returns the extracted text.")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Endpoint to parse a single PDF and return its content.
    """
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"./{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())

        # Parse the PDF using MegaParse
        response = megaparse.load(temp_file_path)

        # Clean up temporary file
        os.remove(temp_file_path)

        return {"filename": file.filename, "content": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {e}")


@app.post("/parse_multiple", summary="Parse Multiple PDFs", description="Parses multiple PDF files and returns their contents.")
async def parse_multiple_pdfs(files: List[UploadFile] = File(...)):
    """
    Endpoint to parse multiple PDFs and return their content.
    """
    parsed_files = []

    try:
        for file in files:
            # Save each uploaded file temporarily
            temp_file_path = f"./{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(await file.read())

            # Parse the PDF using MegaParse
            response = megaparse.load(temp_file_path)

            # Append parsed content
            parsed_files.append({"filename": file.filename, "content": response})

            # Clean up temporary file
            os.remove(temp_file_path)

        return {"parsed_files": parsed_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing files: {e}")


@app.get("/", summary="Health Check", description="Check if the API is running.")
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return JSONResponse(content={"status": "API is running"}, status_code=200)

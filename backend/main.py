import io
from dotenv import load_dotenv
load_dotenv()
import requests
import mimetypes

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from backend.search import search, Match
from PIL import Image, ImageOps

app = FastAPI()

# Define the list of allowed origins
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

# Add the CORSMiddleware to the app with the specified allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Define request body
# Screenshot is file
class IconSearchRequest(BaseModel):
    url: Optional[str] = None
    file: Optional[UploadFile] = None

# Read file from requestbody form data
@app.post("/search")
async def getIcon(req: IconSearchRequest):
    print('reading file')

    print(req)

    if req.url is not None:
        response = requests.get(req.url)
        contentType = response.headers.get('content-type')
        if contentType is None:
            return {"output": "invalid image"}

        file = io.BytesIO(response.content)
        
        print("read img file")
        img = Image.open(file)
        print("convert to grayscale")
        grayscale_img_bytes = io.BytesIO()
        
        # get img format from contentType
        imgFormat = mimetypes.guess_extension(contentType)
        if imgFormat is None:
            return {"output": "invalid image format"}

        print(imgFormat)
        img.save(grayscale_img_bytes, format=imgFormat.replace('.', ''))

        matches = search(f = grayscale_img_bytes)
        
        inverted_grayscale_img = ImageOps.invert(img.convert('L'))
        inverted_grayscale_img_bytes = io.BytesIO()
        inverted_grayscale_img = inverted_grayscale_img.convert('RGBA')
        inverted_grayscale_img.save(inverted_grayscale_img_bytes, format=imgFormat.replace('.', ''))

        invertedMatch = search(f= inverted_grayscale_img_bytes)

        uniqueMatchIds: list[str] = []
        uniqueMatches: list[Match] = []
        for match in matches+invertedMatch:
            if match.id not in uniqueMatchIds:
                uniqueMatchIds.append(match.id)
                uniqueMatches.append(match)


        # combine the two lists
        return {"output": uniqueMatches}

    return {"output": "error"}


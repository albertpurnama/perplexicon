import replicate

# load environment variables from .env file using dotenv library
from dotenv import load_dotenv
from typing import Any, Optional
import io

load_dotenv()

import pinecone
import os
from pydantic import BaseModel

index_name = 'image-fast-search'

apiKey = os.getenv("PINECONE_API_KEY")
if apiKey is None:
    raise Exception("PINECONE_API_KEY is not defined")

# get API key from environment variable
pinecone.init(api_key=apiKey, environment='us-west1-gcp-free')
index = pinecone.Index(index_name)

folder_path = './assets'

class IconMetadata(BaseModel):
    icon_pack: str
    icon_name: str
    homepage_url: str
    label: str
    svg_url: Optional[str] = None

    def getSVGPath(self):
        return f'{self.icon_pack}/{self.icon_name}.svg'

def isImageFile(file):
    return file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.svg')

def updateMetadataPinecone(id: str, metadata: IconMetadata):
    index.update(id, None, metadata.model_dump())


def uploadToPineconeBytes(b: io.BytesIO, metadata: IconMetadata): 
    # Create embeddings
    output: Any = replicate.run("krthr/clip-embeddings:1c0371070cb827ec3c7f2f28adcdde54b50dcd239aa6faea0bc98b174ef03fb4",input={"image": b})
    print(metadata.icon_name, metadata.model_dump())

    index.upsert([
        (metadata.icon_name, output['embedding'], metadata.model_dump()),
    ])

def uploadToPinecone(folder_path: str = './assets'):
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)) and isImageFile(file):
            with open(os.path.join(folder_path, file), 'rb') as f:
                # Create embeddings
                output: Any = replicate.run("krthr/clip-embeddings:1c0371070cb827ec3c7f2f28adcdde54b50dcd239aa6faea0bc98b174ef03fb4",input={"image": f})

                print(file)

                # remove file extension
                icon_name = file.split('.')[0]

                index.upsert([
                    (icon_name, output['embedding'], {'icon_pack': 'phosphoricon', 'icon_name': icon_name}),
                ])

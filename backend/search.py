import replicate
import pinecone
import os
import io
from typing import Any, List
from pydantic import BaseModel
from backend.upload_pinecone import IconMetadata  
from dotenv import load_dotenv
load_dotenv()

class Match(BaseModel):
  id: str
  metadata: IconMetadata
  score: float
  values: List[float]

def search(f: io.BytesIO):
  pineconeKey = os.getenv("PINECONE_API_KEY")
  if pineconeKey is None:
    raise Exception("PINECONE_API_KEY is not defined")

  # We explicitly type cast this because we know what the return value is
  # maybe we should use pydantic here to define the return value.
  output: Any = replicate.run("krthr/clip-embeddings:1c0371070cb827ec3c7f2f28adcdde54b50dcd239aa6faea0bc98b174ef03fb4",input={"image": f});

  pinecone.init(api_key=pineconeKey, environment='us-west1-gcp-free')
  index = pinecone.Index("image-fast-search")

  # return the first match (the most similar image)
  queryResult = index.query(
    vector= output['embedding'], 
    top_k= 3,
    include_metadata=True
  )

  matches = queryResult.to_dict()['matches']

  try:
    return [Match(**match) for match in matches]
  except Exception as e:
    raise Exception(f"Error parsing match: {e}")


import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import io
import replicate
import pinecone
from typing import Any
from upload_pinecone import uploadToPineconeBytes, IconMetadata, updateMetadataPinecone
from PIL import Image, PngImagePlugin
from dotenv import load_dotenv
load_dotenv()

folder_path = './scraped'
icon_pack = 'react-icons/pi'
url = 'https://react-icons.github.io/react-icons/icons/pi/'
homepage_url = 'https://phosphoricons.com/'
label = 'phosphoricons'


import boto3
s3 = boto3.client('s3',
    region_name='us-east-1',
    endpoint_url=f'https://{os.getenv("SPACES_REGION")}.digitaloceanspaces.com',
    aws_access_key_id=os.getenv("SPACES_KEY"),
    aws_secret_access_key=os.getenv("SPACES_SECRET"),
)

s3BucketName = os.getenv("SPACES_NAME")

def scrapeIconsAndUpload(url: str = url, icon_pack: str = icon_pack, folder_path: str = folder_path):
  # Open the desired URL
  driver.get(url)

  # tell python to wait for 2 seconds to allow the page to fully render
  time.sleep(2)

  # Access the fully rendered HTML content
  html_content = driver.page_source

  soup = BeautifulSoup(html_content, 'html.parser')

  # find all icons
  iconsContainer = soup.find('div', {'class': 'icons'})
  if iconsContainer is None:
      raise Exception("Icons container is not found")

  items = driver.find_elements(By.CLASS_NAME, 'item')
  print(len(items))

  # take screenshot of all svg elements in the page
  for index, iconElement in enumerate(items):
      try: 
        # get the icon name
        name = iconElement.find_element(By.CLASS_NAME, 'name').text

        # get the svg element, screenshot it.
        icon = iconElement.find_element(By.TAG_NAME, 'svg')
        svgString = icon.get_attribute("outerHTML")

        print("Taking screenshot of " + name)
        
        meta = IconMetadata(icon_pack=icon_pack, icon_name=name, homepage_url=homepage_url, label=label)

        if svgString is not None:
          s3.upload_fileobj(
            io.BytesIO(svgString.encode('utf-8')),
            s3BucketName,
            meta.getSVGPath(),
            ExtraArgs={
              'ACL': 'public-read',
              'ContentType': 'text/html'
            }
          )
          meta.svg_url = f'https://{s3BucketName}.{os.getenv("SPACES_REGION")}.digitaloceanspaces.com/{meta.getSVGPath()}'

        uploadToPineconeBytes(io.BytesIO(icon.screenshot_as_png), meta)
        print("Uploaded " + name + "progress: " + str(index) + "/" + str(len(items)))
      except Exception as e:
        print('error')
        print(e)
        continue

def scrapeIconsAndUpdateMetadata():
   # Open the desired URL
  driver.get(url)

  # tell python to wait for 2 seconds to allow the page to fully render
  time.sleep(2)

  # Access the fully rendered HTML content
  html_content = driver.page_source

  soup = BeautifulSoup(html_content, 'html.parser')

  # find all icons
  iconsContainer = soup.find('div', {'class': 'icons'})
  if iconsContainer is None:
      raise Exception("Icons container is not found")

  items = driver.find_elements(By.CLASS_NAME, 'item')

  # take screenshot of all svg elements in the page
  for index, iconElement in enumerate(items):
      try: 
        svgString = iconElement.find_element(By.TAG_NAME, "svg").get_attribute("outerHTML")

        # get the icon name
        name = iconElement.find_element(By.CLASS_NAME, 'name').text
        
        meta = IconMetadata(icon_pack=icon_pack, icon_name=name, homepage_url=homepage_url, label=label)

        if svgString is not None:
          s3.upload_fileobj(
            io.BytesIO(svgString.encode('utf-8')),
            s3BucketName,
            meta.getSVGPath(),
            ExtraArgs={
              'ACL': 'public-read',
              'ContentType': 'text/html'
            }
          )
          meta.svg_url = f'https://{s3BucketName}.{os.getenv("SPACES_REGION")}.digitaloceanspaces.com/{meta.getSVGPath()}'

        updateMetadataPinecone(meta.icon_name, meta)
        print("Updated " + name + " progress: " + str(index) + "/" + str(len(items)))
      except Exception as e:
        print('error')
        print(e)
        continue

def scrapeIcons():
  # Open the desired URL
  driver.get(url)

  # tell python to wait for 2 seconds to allow the page to fully render
  time.sleep(2)

  # Access the fully rendered HTML content
  html_content = driver.page_source

  soup = BeautifulSoup(html_content, 'html.parser')

  # find all icons
  iconsContainer = soup.find('div', {'class': 'icons'})
  if iconsContainer is None:
      raise Exception("Icons container is not found")

  items = driver.find_elements(By.CLASS_NAME, 'item')
  print(len(items))

  # take screenshot of all svg elements in the page
  for index, iconElement in enumerate(items):
      try: 
        # get the icon name
        name = iconElement.find_element(By.CLASS_NAME, 'name').text

        # get the svg element, screenshot it.
        icon = iconElement.find_element(By.TAG_NAME, 'svg')
        svgString = icon.get_attribute("outerHTML")
        
        print("Taking screenshot of " + name)
        
        meta = IconMetadata(icon_pack=icon_pack, icon_name=name, homepage_url=homepage_url, label=label)

        if svgString is not None:
          directory = f'{folder_path}/{icon_pack}'
          os.makedirs(directory, exist_ok=True)
          # save to file
          with open(f'{folder_path}/{meta.getSVGPath()}', 'w') as f:
             f.write(svgString)

        svgImg = Image.open(io.BytesIO(icon.screenshot_as_png))
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("icon_meta", meta.model_dump_json())
        svgImg.save(f'{folder_path}/{name}.png', pnginfo=metadata)

        print("Uploaded " + name + "progress: " + str(index) + "/" + str(len(items)))
      except Exception as e:
        print('error')
        print(e)
        continue

def isImageFile(file):
    return file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.svg')

def readIcons(folder_path: str = './assets'):
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)) and isImageFile(file):
            with open(os.path.join(folder_path, file), 'rb') as f:
                img = Image.open(f)
                imgMeta = img.info.get("icon_meta")
                if imgMeta is None: 
                  continue
                
                iconMetadata = IconMetadata.model_validate_json(imgMeta)
                svgPath = os.path.join(folder_path, file)
                svgFile = open(svgPath, 'rb')
                svgString = str(svgFile.read())
                
                if svgString is not None:
                  s3.upload_fileobj(
                    io.BytesIO(svgString.encode('utf-8')),
                    s3BucketName,
                    iconMetadata.getSVGPath(),
                    ExtraArgs={
                      'ACL': 'public-read',
                      'ContentType': 'text/html'
                    }
                  )
                  iconMetadata.svg_url = f'https://{s3BucketName}.{os.getenv("SPACES_REGION")}.digitaloceanspaces.com/{iconMetadata.getSVGPath()}'

                print(f'Saving {iconMetadata.icon_name}')
                image_bytes = io.BytesIO()
                img.save(image_bytes, format='png')

                uploadToPineconeBytes(image_bytes, iconMetadata)
            print(f'removing file {os.path.join(folder_path, file)}')
            os.remove(os.path.join(folder_path, file))

# Initialize the WebDriver
# driver = webdriver.Chrome()

readIcons(folder_path)
# scrapeIcons()

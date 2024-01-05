
from PIL import Image
import pytesseract

# Load an image
# image = Image.open('./.seed-knowledge/passport-max-exposure.png')
image = Image.open('./.seed-knowledge/sample-usa-passport.jpg')

# Perform OCR
text = pytesseract.image_to_string(image)
print(text)

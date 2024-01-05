from PIL import Image, ImageOps
import io

file = "test.png"
img = Image.open(file)
print("convert to grayscale")
img = img.convert('L')

inverted = ImageOps.invert(img)

inverted = inverted.convert('RGBA')

inverted.save('invertedgg.png')

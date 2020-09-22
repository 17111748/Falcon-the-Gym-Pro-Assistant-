from PIL import Image 

image = Image.open('images/test.jpg')
new_image = image.resize((160, 120))
new_image.save('images/image_160x120.jpg')






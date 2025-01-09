import time
from   globals import IMAGES_CASH, TTL

def get_image(image_path):
    current_time = time.time()
    cached_image = IMAGES_CASH.get(image_path)
    if cached_image and current_time - cached_image['timestamp'] < TTL:
        return cached_image['data']
    else:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        IMAGES_CASH[image_path] = {'data': image_data, 'timestamp': current_time}
        return image_data
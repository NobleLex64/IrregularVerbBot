import time
from   globals import image_cache, TTL

def get_image(image_path):
    current_time = time.time()
    cached_image = image_cache.get(image_path)
    if cached_image and current_time - cached_image['timestamp'] < TTL:
        return cached_image['data']
    else:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image_cache[image_path] = {'data': image_data, 'timestamp': current_time}
        return image_data
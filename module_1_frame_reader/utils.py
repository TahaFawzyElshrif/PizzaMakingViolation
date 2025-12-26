import cv2
import base64
def estimate_kafka_message_size(image):
    """
    Estimates the Kafka message size (in bytes) if an image is sent as Base64.
    
    Parameters:
    - image: NumPy array (OpenCV image)
    
    Returns:
    - size_bytes: estimated message size in bytes
    - size_mb: estimated size in MB
    """
    # Encode image as JPEG
    _, buffer = cv2.imencode('.jpg', image)
    
    # Encode to Base64
    jpg_as_text = base64.b64encode(buffer)
    
    # Get size
    size_bytes = len(jpg_as_text)
    size_mb = size_bytes / (1024 * 1024)
    
    return size_bytes, size_mb
#estimate_kafka_message_size(camera.read()[1])
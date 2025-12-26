import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import base64
import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import cv2
import re
folder_path_parent = "D:\\Study\\EagleVision\\PreTrainTask\\violations_folder\\"




def get_image_from_base64(byte_encoded_img):
    '''
    Given base64 image got from stream --> get image array
    '''
    # Decode base64 to bytes
    jpg_original = base64.b64decode(byte_encoded_img)

    # Convert bytes to numpy array
    nparr = np.frombuffer(jpg_original, np.uint8)

    # Decode image
    frame_recovered = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame_recovered




def save_to_database(conn,name_img_file,time_stamp):
    cursor = conn.cursor()
    query = """
    INSERT INTO violations (warned_frame_ingred, time_stamp_ingred, warned_frame_pizza)
    VALUES (%s, %s, %s)
    """
    values = (name_img_file, time_stamp, name_img_file)

    cursor.execute(query, values)


    conn.commit() 
    conn.close()



def save_image(conn,logged_frame):

    img_array = get_image_from_base64(logged_frame['warned_frame_ingred'])


    fig, ax = plt.subplots(figsize=(12, 8)) # Act as image area defination
    ax.imshow(img_array)

    # ADD HAND
    x1, y1, x2, y2 = logged_frame['warned_boxes']['BOX'] 
    rect = patches.Rectangle((x1, y1), x2-x1, y2-y1,
                                linewidth=2, edgecolor='red', facecolor='red',alpha=.2)
    ax.add_patch(rect)
    ax.text(x1, y1-5, logged_frame['warned_boxes']["label"], color='red', fontsize=12)

    # ADD ROI
    x1, y1, x2, y2 = logged_frame['warned_boxes']['ROI'] 
    rect = patches.Rectangle((x1, y1), x2-x1, y2-y1,
                                linewidth=2, edgecolor='blue', facecolor='blue',alpha =.2)
    ax.add_patch(rect)
    ax.text(x1, y1-5, "ROI", color='blue', fontsize=12)

    # Other options
    ax.axis('off')
    plt.tight_layout()

    # convert to numpy and prepare for save
    fig.canvas.draw()  
    w, h = fig.canvas.get_width_height()
    plot_img = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)  # RGBA
    plot_img = cv2.cvtColor(plot_img, cv2.COLOR_RGBA2RGB)  # لو عايز BGR استخدم cv2.COLOR_RGBA2BGR

    plt.close(fig)

    # finally save
    safe_time = re.sub(r'[:\s]', '_', logged_frame['time_stamp_ingred']) # refine name from errors
    name_img = f"{folder_path_parent}Violation_{safe_time}.jpg"

    cv2.imwrite(name_img, plot_img)
    print(f"Saved: {name_img}")
    save_to_database(conn,name_img,logged_frame['time_stamp_ingred'])
    print("Saved to database")
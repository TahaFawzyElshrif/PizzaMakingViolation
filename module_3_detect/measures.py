from datetime import datetime

x_ing, y_ing, w_ing, h_ing  = (377, 272, 159, 438)
roi_ingredients = [x_ing, y_ing, x_ing + w_ing, y_ing + h_ing]  # detected by roi = cv2.selectROI("Select Ingredient Area", frame_i_img, False, False)

def inside_roi(box): 
    '''
    Check if box exist in ROI
    '''
    x1, y1, x2, y2 = box
    rx1, ry1, rx2, ry2 = roi_ingredients
    return bool(x1 >= rx1 and y1 >= ry1 and x2 <= rx2 and y2 <= ry2)


thresould_hand_pizza = 30
thresould_hand_scooper = 30
thresould_hand_body = 98 
n_second_thresould = 10 


def distance_between_edges(box1, box2): 
    '''
    Check if 2 boxes are near by any edge
    '''
    x1,y1,x2,y2 = box1
    a1,b1,a2,b2 = box2

    dx = max(a1 - x2, x1 - a2, 0)
    dy = max(b1 - y2, y1 - b2, 0)

    return (dx**2 + dy**2) ** 0.5


def check_if_the_timeFrame_isOld(frame_time_stamp_first,frame_new_time_stamp_last):
    # 1️⃣ حوله لـ datetime object
    st = datetime.strptime(frame_time_stamp_first, "%Y-%m-%d %H:%M:%S.%f")

    lst = datetime.strptime(frame_new_time_stamp_last, "%Y-%m-%d %H:%M:%S.%f")

    diff = lst - st  

    return (diff.total_seconds() > (n_second_thresould))


from keys import *
from collections import deque
from connections import *
from utils import *
from model_functions import *
from measures import *
from IPython.display import display, clear_output

queue_frames = deque(maxlen = fps * delay_frame * buffer) 
stop_event_filling_queue = threading.Event()

filler_thread = threading.Thread(target=consumer_fill_queue, args=(queue_frames, stop_event_filling_queue), daemon=True)
filler_thread.start()
#stop_event_filling_queue.set() 
time.sleep(60) # wait minutes before start until queue get values(only start)



warned_case = {
    "warned_frame_dict" : None,
    "warned_id_hand" : None,
    "warned_id_near_pizza" : False,
    "warned_id_near_pizza_frame": None,
    "warned_id_near_scooper" : True ,
    "warned_boxes" : None
}

logged_frame = {
    "warned_frame_ingred":None,   
    "time_stamp_ingred":None,  
    "warned_frame_pizza":None ,
    "warned_boxes" : None
}



while True:
    frame_i_dict = queue_frames.popleft()#queue_frames[i]
    frame_i_img = get_image_from_base64(frame_i_dict['frame_data'])
    

    # Draw Figure
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(frame_i_img, cv2.COLOR_BGR2RGB))
    
    # Draw ROI rectangle
    x1, y1, x2, y2 = roi_ingredients
    rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=2, edgecolor='blue', facecolor='none')
    plt.gca().add_patch(rect)
    plt.text(x1, y1, 'ROI', color='blue', fontsize=20)


    
    
    # Predict using yolo model and update trackers
    predictions = model(frame_i_img)
    boxes_labels = get_boxes_by_labels(predictions)
    tracks, detections = update_tracker(predictions,frame_i_img)


    
    for t in tracks: 

        box = t.to_ltrb()
        x11, y11, x21, y21 = map(float, box)
        print(f"{t.det_class} {t.track_id} , {t.det_conf}")

        # Draw predicated tracked object
        rect = patches.Rectangle((x11, y11), x21-x11, y21-y11, linewidth=2, edgecolor='green', facecolor='none')
        plt.gca().add_patch(rect)
        plt.text(x11, y11, f"{t.det_class} {t.track_id}", color='black', fontsize=20) 
    

        if (t.det_class == 'hand'):
            #print(f"BOX {box},{roi_ingredients}, inside {inside_roi(box) }")
            # At first check if hand in the ROI
            if(inside_roi(box) and (warned_case["warned_frame_dict"] is None)):
                warned_case["warned_frame_dict"] =  frame_i_dict
                warned_case["warned_id_hand"] = t.track_id 
                warned_case['warned_boxes'] = {"ROI":roi_ingredients,"BOX": box,"label":"hand"}
                print(f"---> Warned updated {warned_case['warned_frame_dict']['frame_data'][:45]} -- {t.track_id }")

                break # for simple condition just one check enough

            print((t.track_id ,warned_case["warned_id_hand"]))
            # given warning dict check other condition
            if ((warned_case["warned_frame_dict"] is not None) and (t.track_id == warned_case["warned_id_hand"])):
                print("Scoopers", boxes_labels['scooper'])
                print("Distances between ",box, " and ",[(pizza_i,distance_between_edges(box,pizza_i))  for pizza_i in boxes_labels['pizza']])

                if any([distance_between_edges(box,pizza_i) < thresould_hand_pizza for pizza_i in boxes_labels['pizza']]):
                    warned_case["warned_id_near_pizza"] = True
                    warned_case["warned_id_near_pizza_frame"] = frame_i_dict["frame_data"]
                    print(f"---> Touched pizza {warned_case['warned_id_near_pizza']}")
                if any([distance_between_edges(box,scooper_i)< thresould_hand_scooper for scooper_i in boxes_labels['scooper']]):
                    warned_case["warned_id_near_scooper"] = True 
                    print(f"---> Touched scooper {warned_case['warned_id_near_scooper']}")


    
    # Base cases store if all true or remove if time from it
    if ((warned_case["warned_frame_dict"] is not None)): #skip if repeated the vilance in same time
           
        #if (warned_case["warned_id_near_pizza"] and not warned_case["warned_id_near_scooper"]) and ( warned_case["warned_id_near_pizza"]) : # and already touch gradient
        if (True):
            # Store Case
            logged_frame = {
                        "warned_frame_ingred":warned_case["warned_frame_dict"]["frame_data"],   
                        "time_stamp_ingred":warned_case["warned_frame_dict"]["timeDate"],  
                        "warned_frame_pizza":warned_case["warned_id_near_pizza_frame"] ,
                        "warned_boxes" : warned_case['warned_boxes']
            }
                    
            # Reset warned_case
            warned_case  = {
                        "warned_frame_dict" : None,
                        "warned_id_hand" : None,
                        "warned_id_near_pizza" : False,
                        "warned_id_near_pizza_frame": None,
                        "warned_id_near_scooper" : True,
                        "warned_boxes" : None
            }
            print(f"----> Logged updated {logged_frame['warned_frame_ingred'][:45]}")
            save_image(conn,logged_frame)
    
            producer_to_violations.send(topic_violaltion, { "frame_data": logged_frame['warned_frame_ingred'],"timeDate": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))})

        
        elif (check_if_the_timeFrame_isOld(warned_case["warned_frame_dict"]["timeDate"],frame_i_dict['timeDate'])):
            # time from this action ,and first condition is false so remove it (shouldn't be forever)
            # Reset warned_case
            warned_case  = {
                        "warned_frame_dict" : None,
                        "warned_id_hand" : None,
                        "warned_id_near_pizza" : False,
                        "warned_id_near_pizza_frame": None,
                        "warned_id_near_scooper" : True,
                        "warned_boxes" : None
            }
            print(f"----> WARN RESET {warned_case['warned_id_hand']}")
        
    clear_output(wait=True)
    plt.axis('off')
    plt.title('Frame with Ingredient ROI')
    plt.tight_layout()
    plt.show()
            
                        

        
    
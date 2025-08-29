
import cv2 as cv

print(cv.__version__)

import argparse
import sys
import os.path
import numpy as np
import json
import matplotlib.pyplot as plt

#winName = "Augmented Reality using Aruco markers in OpenCV"

#parser = argparse.ArgumentParser(description='Augmented Reality using Aruco markers in OpenCV')
#parser.add_argument('--video', default='ar_in.avi', help='Path to the input video file.')
#args = parser.parse_args()

#if not os.path.isfile(args.video):
#    print("Input video file ", args.video, " doesn't exist")
#    parser.print_help()
#    sys.exit(1)
    
#cap = cv.VideoCapture(args.video)
#vidPath = '/home/yoyo/Apps/videoHand1.webm'
#cap = cv.VideoCapture( vidPath )

# Initialize the detector parameters - picked a working combination from millions of random examples


mD = [
    [cv.aruco.DICT_4X4_50, 50, '4x4'],
    [cv.aruco.DICT_5X5_100, 100, '4x4'],
    [cv.aruco.DICT_6X6_250, 250 ,'6x6'],
    [cv.aruco.DICT_6X6_1000, 1000, '6x6'],
    [cv.aruco.DICT_ARUCO_ORIGINAL, 300, 'org']

]


for m in mD:

    aruco_dict = cv.aruco.getPredefinedDictionary(
        m[0]
        #cv.aruco.DICT_6X6_250
        #cv.aruco.DICT_4X4_100
        
        )

    for i in [1,2,5,45]:
        print("have aruco_dict")
        marker_id = i
        marker_size = m[1]  # Size in pixels
        marker_image = cv.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
        marker_image = np.pad(marker_image, pad_width=int(m[1]*0.1), constant_values=255)

        cv.imwrite(f"markers/{m[2]}_{m[1]}_{marker_id}.png", marker_image)
        #plt.imshow(marker_image, cmap='gray', interpolation='nearest')
        #plt.axis('off')  # Hide axes
        #plt.title(f'ArUco Marker {marker_id}')
        #plt.show()


exit(1)


detected_markers={}
frame_counter = 0
while cv.waitKey(1) < 0:
    frame_counter += 1
    try:
        # get frame from the video
        hasFrame, frame = cap.read()
        #frame = cv.resize( frame, (640,480) )
        # Stop the program if reached end of video
        if not hasFrame:
            print("Done processing !!!")
            cv.waitKey(3000)
            break
                
        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(frame, dictionary, parameters=parameters)
        print('frame: {} ids: {}'.format(frame_counter, markerIds.tolist()))
        im_out = cv.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        # Showing the original image with the markers drawn on it
        cv.imshow(winName, im_out.astype(np.uint8))

    except Exception as inst:
        print(inst)
    
cv.destroyAllWindows()


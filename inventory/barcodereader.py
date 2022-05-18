# # An OpenCV barcode and QR code scanner with ZBar
# # import the necessary packages
# from imutils.video import VideoStream
# from pyzbar import pyzbar
# import argparse
# import datetime
# import imutils
# import time
# import cv2

# # camera = cv2.VideoCapture(1)

# def serve_frames():  
#     while True:
#         success, frame = camera.read()  # read the camera frame
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             print(b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

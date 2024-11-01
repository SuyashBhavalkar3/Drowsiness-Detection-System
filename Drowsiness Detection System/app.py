import cv2
import numpy as np
import dlib
from imutils import face_utils
import time
import threading
import pygame

cap = cv2.VideoCapture(0)

hog_face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

pygame.mixer.init()
buzzer_sound = pygame.mixer.Sound("buzzer.mp3")

sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2
    elif 0.21 < ratio <= 0.25:
        return 1
    else:
        return 0

def process_frames():
    global sleep, drowsy, active, status, color

    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = hog_face_detector(gray)

        for face in faces:
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            face_frame = frame[y1:y2, x1:x2]  
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_blink = blinked(landmarks[36], landmarks[37],
                                 landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = blinked(landmarks[42], landmarks[43],
                                  landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            if left_blink == 0 or right_blink == 0:
                sleep += 1
                drowsy = 0
                active = 0
                if sleep > 6:
                    buzzer_sound.play()
                    time.sleep(2)
                    status = "SLEEPING !!!"
                    color = (0, 0, 255)

            elif 0.21 < left_blink <= 0.25 or 0.21 < right_blink <= 0.25:
                sleep = 0
                active = 0
                drowsy += 1
                if drowsy > 6:
                    buzzer_sound.play()
                    time.sleep(2)
                    status = "Drowsy !"
                    color = (0, 0, 255)

            else:
                drowsy = 0
                sleep = 0
                active += 1
                if active > 6:
                    status = "Active"
                    color = (0, 0, 255)
                    # Stop the buzzer sound if it's playing
                    buzzer_sound.stop()

            cv2.putText(frame, status, (100, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            for (x, y) in landmarks:
                cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(24)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

thread = threading.Thread(target=process_frames)
thread.start()

thread.join()
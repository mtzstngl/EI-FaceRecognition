#!/home/smartmirror/MagicMirror/modules/EI-FaceRecognition/Gesichtserkenung/venv/bin/python3
import json  # rausschreiben
import os
import sys
import time

sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# -----------------------------------------
import face_recognition  # Face_Recognition
import cv2
import numpy as np
# -----------------------------------------
# import cv2                                             #Emotion Detection
# import numpy as np
from keras.models import load_model
from statistics import mode
from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
# --------------------------------------------- Datei einlesen
from os import walk

# Json Objekt festlegen
send_away = {
    "name": None,
    "index": None,
    "emotion": None
}

#Fehlermeldungen
Error_USB = ""
Error_Kamera = ""

#Zyklus
zykluszeit = 30
zyklus = 1


#Mittelung der Namen
old_name=""
array_names = []
anzahl_namen = 0
wahrscheinlichster_name = ""
anzahl_index_name = []

#Mittelung der Emotionen
wahrscheinlichste_emotion = ""
array_emotionen = []
anzahl_index_emotion = []

sys.stderr = sys.__stderr__
while True:
    if os.path.ismount("/media/smartmirror/UNTITLED/"):
        break
    else:
        Error_USB = "Der USB-Stick ist nicht angeschlossen! Stecken Sie den USB-Stick erneut an und aus!"
        print(json.dumps(Error_USB), file=sys.stderr)

    time.sleep(15)

USB_path = "/media/smartmirror/UNTITLED/"  # Pfad anpassen /media/Benutzer/USB_Name/Datei

while True:
    video_capture = cv2.VideoCapture(6)

    if(not(video_capture.isOpened())):
        Error_Kamera = "Die Kamera ist nicht angeschlossen! Stecken Sie die Kamera erneut an und aus!"
        print(json.dumps(Error_Kamera), file=sys.stderr)
    else:
        #print("Kamera ist angeschlossen!", file=sys.stderr)
        break

    time.sleep(15)

sys.stderr = open(os.devnull, 'w')

# Emotion Detection
# parameters for loading data and images
emotion_model_path = '/home/smartmirror/MagicMirror/modules/EI-FaceRecognition/Gesichtserkennung/venv/models/emotion_model.hdf5'
emotion_labels = get_labels('fer2013')
# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)
# loading models
face_cascade = cv2.CascadeClassifier(
    '/home/smartmirror/MagicMirror/modules/EI-FaceRecognition/Gesichtserkennung/venv/models/haarcascade_frontalface_default.xml')
emotion_classifier = load_model(emotion_model_path)
# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# Face_Recognition
# Einlesen der Bild Dateien von USB-Stick
# Einlesen der Namen von USB-Stick
known_face_names = []
known_images = []
known_face_encodings = []

for (dirpath, dirnames, filenames) in walk(USB_path):
    known_face_names.extend(filenames)

# Einlesen der Bilder
for i in range(0, len(known_face_names)):
    if (known_face_names[i].find('.jpg') != -1):
        known_images.append(face_recognition.load_image_file(USB_path + known_face_names[i]))
        known_face_encodings.append(face_recognition.face_encodings(known_images[i])[0])
        anzahl_namen = anzahl_namen+1
    else:
        break


# Bearbeiten der Bilder (Face Recognition)
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

sys.stdout = sys.__stdout__
while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Paramter fx, fy für speedup kleiner machen
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        face_detection_name = ''
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_detection_name = "Unknown.jpg"

            # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #    first_match_index = matches.index(True)
            #    face_detection_name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if (len(face_distances) != 0):
                best_match_index = np.argmin(face_distances)
            else:
                continue

            if matches[best_match_index]:
                face_detection_name = known_face_names[best_match_index]
            face_names.append(face_detection_name)

    process_this_frame = not process_this_frame

    # Emotion Detection

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
    emotion_text = None
    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]
        # print(emotion_text)
        # print(face_detection_name)

    array_names.append(face_detection_name)
    array_emotionen.append(emotion_text)


    if(zykluszeit == zyklus):
        for i in range(0, anzahl_namen):                        #vorbelegen des Index Arrays Namen mit 0
            anzahl_index_name.append(0)

        for i in range(0, 6):                                   #vorbelegen des Index Arrays Emotion mit 0
            anzahl_index_emotion.append(0)

        for i in range(0, anzahl_namen):                        #ermitteln wie oft ein Name vorkommt
            for j in range(0, len(array_names)):
                if(array_names[j]==known_face_names[i]):
                    anzahl_index_name[i]=anzahl_index_name[i]+1

        for i in range(0, len(anzahl_index_name)):              #ermitteln des Namen der am häufigsten vorkam
            if(anzahl_index_name[i] == 0):
                wahrscheinlichster_name='Unknown.jpg'
            else:
                wahrscheinlichster_name=known_face_names[np.argmax(anzahl_index_name)]
                break


        Keine_Person=0                                      #Wenn keine Person davor steht dann ist an jeder array_name
        for i in range(0, len(array_names)):                #Position ein leerer string
            if(array_names[i] == ""):                       #dann soll wahrscheinlichster_name auch ein leerer string sein
                Keine_Person=Keine_Person+1

        if(Keine_Person == zykluszeit):
            wahrscheinlichster_name = ""


        for i in range(0, len(array_emotionen)):                           #mittelung der emotion
            if(array_emotionen[i]=="happy"):
                anzahl_index_emotion[0]=anzahl_index_emotion[0]+1
            elif(array_emotionen[i] == "sad"):
                anzahl_index_emotion[1] = anzahl_index_emotion[1] + 1
            elif(array_emotionen[i] == "angry"):
                anzahl_index_emotion[2] = anzahl_index_emotion[2] + 1
            elif(array_emotionen[i] == "surprise"):
                anzahl_index_emotion[3] = anzahl_index_emotion[3] + 1
            elif(array_emotionen[i] == "fear"):
                anzahl_index_emotion[4] = anzahl_index_emotion[4] + 1
            else:                                                           #sonst neutral
                anzahl_index_emotion[5] = anzahl_index_emotion[5] + 1

        if(np.argmax(anzahl_index_emotion) == 0):
            wahrscheinlichste_emotion = "happy"
        elif(np.argmax(anzahl_index_emotion) == 1):
            wahrscheinlichste_emotion = "sad"
        elif(np.argmax(anzahl_index_emotion) == 2):
            wahrscheinlichste_emotion = "angry"
        elif(np.argmax(anzahl_index_emotion) == 3):
            wahrscheinlichste_emotion = "surprise"
        elif(np.argmax(anzahl_index_emotion) == 4):
            wahrscheinlichste_emotion = "fear"
        elif(np.argmax(anzahl_index_emotion) == 5):
            wahrscheinlichste_emotion = "neutral"



        if(old_name != wahrscheinlichster_name):                            #nur rausschreiben wenn eine andere Person dort steht
        # Json File zum rausschicken
            if (wahrscheinlichster_name == 'Unknown.jpg'):                  #Wenn unbekannte Person davor steht
                name_Json = None
                index_Json = -1
                emotion_Json = wahrscheinlichste_emotion
            else:                                                           #Wenn bekannte Person davor steht
                name_Json = wahrscheinlichster_name[:-4]
                emotion_Json = wahrscheinlichste_emotion
                index_Json = np.argmax(anzahl_index_name)

            # if(face_detection_name!=''):
            # print(name_Json)
            # print(emotion_Json)
            # emotion: angry, sad, neutral, happy, surprise, fear
            if (name_Json == ''):                                           #Falls keine Person davor steht
                name_Json = None
                emotion_Json = None
                index_Json = -1
            send_away["name"] = name_Json
            send_away["emotion"] = emotion_Json
            send_away["index"] = int(index_Json)

            print(json.dumps(send_away))

            #print(name_Json, end=" ")
            #print(emotion_Json, end=" ")
            #print("Index: ", end="")
            #print(index_Json)

        old_name=wahrscheinlichster_name
        array_names.clear()
        anzahl_index_name.clear()

        array_emotionen.clear()
        anzahl_index_emotion.clear()

        zyklus = 0

    zyklus = zyklus+1

# Verbindung zu WebCam trennen
video_capture.release()







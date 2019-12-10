# face_recog.py

import face_recognition
import cv2
import camera
import os
import numpy as np
import datetime

class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def __del__(self):
        del self.camera

    def get_frame(self):
        # Grab a single frame of video
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)

                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                name = "Unknown"

                if min_value < 0.35:
                    index = np.argmin(distances)

                    name = self.known_face_names[index]

                if name != 'Hyoin':
                    name = ""

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if name == 'Hyoin':
                font = cv2.FONT_HERSHEY_DUPLEX
                # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
                # cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), 2)
                sub_face = frame[top:bottom, left:right]
                # apply a gaussian blur on this new recangle image
                sub_face = cv2.GaussianBlur(sub_face, (23, 23), 30)
                # merge this blurry rectangle to our final image
                # 타입 1
                frame[top:bottom, left:right] = sub_face

                # 타입 2
                # alpha_s = sub_face[:, :, 3] / 255.0
                # alpha_l = 1.0 - alpha_s
                #
                # for c in range(0, 3):
                #     frame[top:bottom, left:right, c] = (alpha_s * sub_face[:, :, c] +
                #                               alpha_l * frame[top:bottom, left:right, c])

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()


if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)

    capture = cv2.VideoCapture("face5.mp4")

    fps = 5.0
    width = int(capture.get(3))
    height = int(capture.get(4))
    fcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    out = cv2.VideoWriter(datetime.datetime.now().strftime("%d_%H-%M-%S.avi"), fcc, fps, (width, height))

    while True:
        frame = face_recog.get_frame()

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        out.write(frame)

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    capture.relaese()
    cv2.destroyAllWindows()
    print('finish')

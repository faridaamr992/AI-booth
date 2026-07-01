import cv2
import mediapipe as mp
import random
import time
import pygame
import os
import sys

pygame.mixer.init()

def resource_path(relative_path):
    """Works for both Python and PyInstaller EXE."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

scan_sound = pygame.mixer.Sound(resource_path("assets/scan.mp3"))
success_sound = pygame.mixer.Sound(resource_path("assets/success.mp3"))

# -----------------------
# Face Detector
# -----------------------
mp_face = mp.solutions.face_detection
detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.6
)

# -----------------------
# Camera
# -----------------------
cap = cv2.VideoCapture(0)

scan_start = None
is_scanning = False
scan_complete = False
scan_sound_playing = False

profile = {}

last_seen = 0

# -----------------------
# Generate Fake Profile
# -----------------------
def generate_profile():

    versions = [
        "v25.7",
        "v26.1",
        "v24.9",
        "v31.0 Beta"
    ]

    bugs = [
        "Occasionally forgets why they entered a room",
        "Requires coffee to compile",
        "Responds positively to pizza",
        "Cannot function before 9 AM",
        "Downloads random hobbies every month",
        "Overthinks simple decisions",
        "Runs better on weekends",
        "Needs reboot after Mondays"
    ]

    statuses = [
        "Needs Weekend Update",
        "Running Smoothly",
        "Low Battery",
        "Weekend Patch Available",
        "Stable Build",
        "Experimental Build"
    ]

    ratings = [
        "Premium Human",
        "Enterprise Edition",
        "Limited Edition",
        "Ultra Human",
        "Gold Member"
    ]

    return {

        "version": random.choice(versions),

        "status": random.choice(statuses),

        "bugs": random.sample(bugs,3),

        "coffee": random.randint(0,4),

        "energy": random.randint(55,100),

        "age": random.randint(20,38),

        "mood": random.choice([
            "Happy",
            "Focused",
            "Curious",
            "Sleepy",
            "Excited"
        ]),

        "quality": round(random.uniform(96.0,99.9),1),

        "rating": random.choice(ratings)

    }

# -----------------------
# Main Loop
# -----------------------
while True:

    ret, frame = cap.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = detector.process(rgb)

    h,w,_ = frame.shape

    detected = False

    if results.detections:

        detected = True

        det = results.detections[0]

        box = det.location_data.relative_bounding_box

        x = int(box.xmin*w)
        y = int(box.ymin*h)
        bw = int(box.width*w)
        bh = int(box.height*h)

        cv2.rectangle(
            frame,
            (x,y),
            (x+bw,y+bh),
            (0,255,0),
            3
        )

        # -----------------------
        # New Face
        # -----------------------

        if not is_scanning and not scan_complete:

            is_scanning = True
            scan_start = time.time()

            if not scan_sound_playing:
                scan_sound.play(-1)      # loop forever
                scan_sound_playing = True

        # -----------------------
        # Scanning Screen
        # -----------------------
        elapsed = time.time() - scan_start

        if elapsed < 3:

            cv2.putText(
                frame,
                "NEW HUMAN DETECTED",
                (40,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0,255,255),
                2
            )

            cv2.putText(
                frame,
                "Initializing Personality Scan...",
                (40,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255,255,255),
                2
            )

            progress = int((elapsed/3)*300)

            cv2.rectangle(
                frame,
                (40,110),
                (340,140),
                (255,255,255),
                2
            )

            cv2.rectangle(
                frame,
                (40,110),
                (40+progress,140),
                (0,255,0),
                -1
            )

        else:

            if not scan_complete:

                profile = generate_profile()

                if scan_sound_playing:
                    scan_sound.stop()
                    scan_sound_playing = False

                success_sound.play()

                scan_complete = True

            x0 = 20
            y0 = 40

            lines = [

                "★★★★★",

                f"Human Version : {profile['version']}",

                f"Software Status : {profile['status']}",

                "",

                "Known Bugs:",

                f"- {profile['bugs'][0]}",

                f"- {profile['bugs'][1]}",

                f"- {profile['bugs'][2]}",

                "",

                f"Coffee Required : {profile['coffee']} cups",

                f"Energy : {profile['energy']}%",

                f"Estimated Age : {profile['age']}",

                f"Mood : {profile['mood']}",

                "",

                "Warranty : Expired",

                f"Human Quality : {profile['quality']}%",

                "",

                f"Overall Rating : {profile['rating']}"

            ]

            for i,line in enumerate(lines):

                cv2.putText(

                    frame,

                    line,

                    (x0,y0+i*25),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.65,

                    (0,255,0),

                    2

                )

    else:

        if scan_sound_playing:
            scan_sound.stop()
            scan_sound_playing = False

        is_scanning = False
        scan_complete = False

    cv2.imshow("INFOTRAFF AI",frame)

    if cv2.waitKey(1)==27:
        break
pygame.mixer.quit()
cap.release()
cv2.destroyAllWindows()
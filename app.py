import cv2
from gpiozero import DigitalInputDevice, Buzzer
from datetime import datetime
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

SENSOR_PINS = [4, 17, 23, 24, 25]  
BUZZER_PIN = 18

IMAGE_SAVE_PATH = f'/home/hamza/Desktop/oop_project/images'  

class Devices:
	def is_triggered(self):
		pass
class Sensor(Devices):
    def __init__(self, pin):
        self.sensor = DigitalInputDevice(pin)
        print(f"Sensor on pin {pin} initialized")

    def is_triggered(self):
        return not self.sensor.value

class BuzzerDevice(Devices):
    def __init__(self, pin):
        self.buzzer = Buzzer(pin)
        print("Buzzer initialized")

    def activate(self):
        self.buzzer.on()
        print("Buzzer activated")

    def deactivate(self):
        self.buzzer.off()
        print("Buzzer deactivated")

 
class Camera(Devices):
    def __init__(self):
        #self.cap = cv2.VideoCapture(self.get_gstreamer_pipeline(), cv2.CAP_GSTREAMER)
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            raise ValueError("Failed to open camera")
        print("Camera initialized")


    def capture_image(self):
		#cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        ret, frame = self.cap.read()
        if ret:
            try:
                if not os.path.exists(IMAGE_SAVE_PATH):
                    os.makedirs(IMAGE_SAVE_PATH)
                timestamp = datetime.now().strftime("%d-%m-%y_(%H-%M-%S)")
                image_path = os.path.join(IMAGE_SAVE_PATH, f'image_{timestamp}.jpg')
                cv2.imwrite(image_path, frame)
                print(f"Image saved: {image_path}")
                return image_path
            except PermissionError:
                print(f"Permission denied: Unable to save image to {IMAGE_SAVE_PATH}")
                return None
        else:
            print("Failed to capture image")
            return None

    def release(self):
        self.cap.release()
        print("Camera released")


def main():
    sensors = [Sensor(pin) for pin in SENSOR_PINS]
    buzzer = BuzzerDevice(BUZZER_PIN)
    camera = Camera() 

    try:
        while True:
           
            if any(sensor.is_triggered() for sensor in sensors):
                buzzer.activate()
                time.sleep(0.3)  
                image_path = camera.capture_image()  
                if image_path:
                    print(f"Image Save Successfully")
                email = 'xxxxx@gmail.com'
                remail = 'xxxxx@gmail.com'
                app_password = 'xxxxxxxxxxxx'

                subject = f"Theft is detected on system at {timestamp}"

                message = f"Theft is detected on system at {timestamp} \nHere is the attachment:\n"

                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = remail
                msg['Subject'] = subject

                msg.attach(MIMEText(message, 'plain'))

                

                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-Disposition', 'attachment', filename='image.jpg')
                    msg.attach(img)

                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls() 
                    server.login(email, app_password)

                    server.sendmail(email, remail, msg.as_string())
                    print('Email sent successfully!')
                except Exception as e:
                    print(f'Failed to send email: {e}')
                finally:
                    server.quit()

                
                
                time.sleep(2)  
            else:
                buzzer.deactivate() 
            time.sleep(0.5)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        camera.release()
        for sensor in sensors:
            sensor.sensor.close()
        buzzer.buzzer.close()

main()

import cv2, base64, asyncio, json, requests
from redis import Redis
import numpy as np
import urllib.request


redis = Redis()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
URL = "http://10.38.78.243:8080/video"
cap = cv2.VideoCapture(URL)
# cap = cv2.VideoCapture('images/100.mp4')

async def Stream():
	print('Start !')

	while True:
		rect , frame = cap.read()

		gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)

		faces = face_cascade.detectMultiScale(gray, 1.3,1)

		for (x,y,w,h) in faces:
			cv2.rectangle(frame, (x,y), (x+w , y+h), (255,0,0), 5)

		imgResize = cv2.resize(frame, (960, 540))
		# cv2.imshow('Image', imgResize)

		# encode image as jpeg
		_, img_encoded = cv2.imencode('.jpg', imgResize)
		imgWebsocket = base64.b64encode(img_encoded).decode('utf-8')
		# 'subscribe COMPUTER_VISION'
		redis.publish( 
			'COMPUTER_VISION', json.dumps({
				'img' : imgWebsocket
			})
		)
		
		if cv2.waitKey(20) & 0xFF == ord('q'):
			break

	print('Quit')
	cap.release()
	cv2.destroyAllWindows()

asyncio.run(Stream())


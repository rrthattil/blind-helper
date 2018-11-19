import RPi.GPIO as GPIO 
import random 
import smtplib 
import serial 
import time,os,subprocess 
from espeak import espeak 
from threading import Timer 
from decimal import * 
import cv2 
import tensorflow as tf,sys 
import numpy as np 
sflag=0 
video_capture = cv2.VideoCapture(0) 
def find(str, ch): 
	for i, ltr in enumerate(str): 
	if ltr == ch: 
		yield i 
def locate(): 
	delay = 1 
	GPIO.setmode(GPIO.BOARD) 
	port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1) 
	ck=0 
	fd='' 
	rcv = port.read(10) 
	fd=fd+rcv 
	if '$GPRMC' in fd: 
		ps=fd.find('$GPRMC') 
		dif=len(fd)-ps 
	if dif &gt; 50: 
		data=fd[ps:(ps+50)] 
		print data 
		p=list(find(data, ",")) xiv 
		lat=data[(p[2]+1):p[3]] 
		lon=data[(p[4]+1):p[5]] 
		s1=lat[2:len(lat)] 
		s1=Decimal(s1) 
		s1=s1/60 
		s11=int(lat[0:2]) 
		s1=s11+s1 
		s2=lon[3:len(lon)] 
		s2=Decimal(s2) 		
		s2=s2/60 
		s22=int(lon[0:3]) 
		s2=s22+s2 
		return s1,s2 
def send(): 
	lat,lon=locate() 
	s = smtplib.SMTP('smtp.example.com', 587) 
	s.starttls() 
	n=random.randint(0,5) 
	s.login("someone1@example.com", "12345678") 
	message = "I am at "+lat[n]+" , "+lon[n] 
	s.sendmail("someone1@example.com", "someone2@example.com", message) 
	s.quit() 
def inform(): 
	GPIO.setup(17,GPIO.IN) 
	state=GPIO.input(17) 
	if(state is True): 
		send() 
	else: 
		pass 
def callhelp(): 
	timer = Timer(60, inform) 
	timer.start() 
def capture(): 
	img_path="front.jpg" xv 	
	ret,frame = video_capture.read() 
	cv2.imwrite(img_path,frame) 
def detect(): 
	img_path="front.jpg" 
	graph_path = 'data/classify_image_graph_def.pb' 
	labels_path = 'data/imagenet_synset_to_human_label_map.txt' 
	image_data = tf.gfile.FastGFile(img_path, 'rb').read() 
	label_lines = [line.rstrip() for line 
	in tf.gfile.GFile(labels_path)] with tf.gfile.FastGFile(graph_path, 'rb') as f: 
		graph_def = tf.GraphDef() 
		graph_def.ParseFromString(f.read()) 
		_ = tf.import_graph_def(graph_def, name='') 
		with tf.Session() as sess: 
			softmax_tensor = sess.graph.get_tensor_by_name('softmax:0') 
			predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data}) 
			predictions = np.squeeze(predictions) 
		top_k = predictions[0].argsort()[-len(predictions[0]):][::-1] 
		thing='none' 
		value=0.0 
		for node_k in top_k: 
			human_string = label_lines[node_k] 
		score = predictions[0][node_k] 
		if score>value: 
			thing=human_string 
			value=score 
			thing=thing.split('\t') 
			thing=thing[1] 
			thing=thing.split(',') 
			thing=thing[0] 
			thing=thing.split('(') 
			thing=thing[0] 
	return thing xvi 
def calculate(): 
	GPIO.setmode(GPIO.BCM) 
	TRIG = 23 
	ECHO = 24 
	GPIO.setwarnings(False) 
	GPIO.setup(TRIG,GPIO.OUT) 
	GPIO.setup(ECHO,GPIO.IN) 
	GPIO.output(TRIG, False) 
	time.sleep(3) 
	GPIO.output(TRIG, True) 
	time.sleep(0.00001) 
	GPIO.output(TRIG, False) 
	while GPIO.input(ECHO)==0:
		pulse_start = time.time() 
	while GPIO.input(ECHO)==1: 
		pulse_end = time.time() 
	pulse_duration = pulse_end - pulse_start 
	distance = pulse_duration * 17150 
	distance = round(distance, 2) 
	if distance > 50 and distance < 400: 
		ret,frame = video_capture.read() 
		capture() 
	object=detect() 
	espeak.synth("There is an "+object +" "+str(distance)+" centimeteres from you") 
	else: 
		espeak.synth("Your route is clear") 
	time.sleep(5) 
GPIO.setup(15,GPIO.IN) 
cond=GPIO.input(15) 
while(cond is True): 
	calculate() 
	callhelp() 
video_capture.release() 
cv2.destroyAllWindows()

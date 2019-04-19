from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import azure.cognitiveservices.speech as speechsdk
import time
from slack import slack
from zulip_bot import relay_messages
from textsum import Summ

global global_string_keeper
global circular_string_cue
global_string_keeper = []
circular_string_cue = []
global speech_recognizer

app = Flask(__name__)

speech_key, service_region = "64a03d07175243919c278f91a3726775", "westus"

# Creates a recognizer with the given settings
done = False
zulip_message_relay = False
slack_message_relay = False

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def pre_process():
	mystr = ""
	for sent in global_string_keeper:
		mystr += sent.strip()
	return mystr

def speech_recognize_continuous_from_file():
	"""performs continuous speech recognition with input from an audio file"""
	print('Configuring files')
	done = False

	def stop_cb(evt):
		"""callback that stops continuous recognition upon receiving an event `evt`"""
		print('CLOSING on {}'.format(evt))
		speech_recognizer.stop_continuous_recognition_async()
		nonlocal done
		done = True

	# def recognize_statement(evt):
	# 	my_str_recg = evt.result.text
	# 	print('RECOGNIZING {}'.format(my_str_recg))
		
	def recognized_statment(evt):
		my_str = evt.result.text
		print("RECOGNIZED {}".format(my_str))
		if my_str != "":
			global_string_keeper.append(my_str)
			# update circular queue
			if len(circular_string_cue) < 10:
				circular_string_cue.append(my_str)
			else:
				del(circular_string_cue[0])
				circular_string_cue.append(my_str)

		if zulip_message_relay == True:
			relay_messages(my_str)
		if slack_message_relay == True:
			slack(my_str)
		

	speech_recognizer.recognized.connect(lambda evt: recognized_statment(evt))
	speech_recognizer.session_stopped.connect(lambda evt : stop_cb(evt))
	speech_recognizer.canceled.connect(lambda evt : stop_cb(evt))
	speech_recognizer.start_continuous_recognition_async()
	while not done:
		time.sleep(4)

@app.route('/transcripts')
def trans():
	print("Circular: ", circular_string_cue)
	if circular_string_cue != []:
		return render_template('listed.html', queue = circular_string_cue)
	else:
		return render_template('listed.html', queue = ['You will see transcripts here!'])
@app.route('/global')
def inti():
	print("Global: ",global_string_keeper)
	total_str = pre_process()
	summ = Summ(total_str)
	# print("SUMMARIZED = ", summ + "\n TOTAL" + total_str)
	return render_template('confirm.html', txt = summ)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live')
def recordUp():
	speech_recognize_continuous_from_file()

@app.route('/shutdown')
def recordDown():
	speech_recognizer.stop_continuous_recognition_async()
	return 'done'


if __name__ == '__main__':
    app.run(debug=True)
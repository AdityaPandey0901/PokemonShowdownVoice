#Pokemon Showdown Voice Controller
#Training Data Generation Script
#Aditya Pandey, Nitish Mallick, Savya Sachi Pandey, Vivek Kumar
#Note: Check the README and report for a full understanding of how this works

from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer
from difflib import SequenceMatcher
import asyncio
import time
import speech_recognition as sr
import keyboard
import pandas as pd
import random
import requests
import openai
import wave
import pyaudio



########################
def MicMove():
	'''This Mic Move is identical to the one used in the main game, with the caveat that this
	 only takes in the shift key press to activate '''


	# Initialize the recognizer
	r = sr.Recognizer()
	start=time.time()

	# Start listening for audio input from the microphone
	with sr.Microphone() as source:

		delay=0

		while True:

		    if keyboard.is_pressed('shift') or time.time()-delay<5: #Essentially, we wanted the mic to keep listening 5 seconds after key released.

		        print("Listening...")

		        #Ambient Noise Adjustment
		        r.adjust_for_ambient_noise(source)
		        audio = r.listen(source)

		        #Time Checks for System Status
		        stop=time.time()
		        if (stop-start)>30:
		        	print("Time Passed:",round(stop-start)," s")

		        try:
		            #Google SR
		            text = r.recognize_google(audio)
		            print("Text detected:",text)
		            return text
		            
		        except sr.UnknownValueError:
		            print("Unknown Value Error")
		        except sr.RequestError as e:
		            print("API Request Error {0}".format(e))

		        #Starts the Delay Check
		        if keyboard.is_pressed('shift')==False:
		        	#Delay timer
		        	delay=time.time()


def test1(n=40):
	'''This function generates n random attack prompts for users to create data off'''

	pokemons=pd.read_csv('data/pokemon.csv')['Name']
	moves=pd.read_csv('data/Pokemon-Moves.csv')['Name   ']
	random.shuffle(pokemons)
	random.shuffle(moves)

	Inputs=[]
	Correct=[]

	for i in range(0,n):
		print('Test ',i)
		move_string=pokemons[i]+' use '+ moves[i]
		print(move_string)
		this_move=MicMove()
		print('Text Parsed: ',this_move)
		Inputs.append(this_move)
		Correct.append(move_string)
		print()

	Output_DF=pd.DataFrame()
	Output_DF['Voice_Text']=Inputs
	Output_DF['Actual_Text']=Correct
	pd.to_csv('data/test1.csv',index=False)

	return

def test2(n=40):
	'''This function generates n random switch prompts for users to create data off'''
	pokemons=pd.read_csv('data/pokemon.csv')['Name']
	pokemons2=pd.read_csv('data/pokemon.csv')['Name']
	random.shuffle(pokemons)
	random.shuffle(pokemons2)

	Inputs=[]
	Correct=[]

	statements=[' come back. Go ',' switch for ',' swap for ']

	for i in range(0,n):
		print('Test ',i)
		move_string=pokemons[i]+statements[i%3]+ pokemons2[i]
		print(move_string)
		this_move=MicMove()
		print('Text Parsed: ',this_move)
		Inputs.append(this_move)
		Correct.append(move_string)
		print()

	Output_DF=pd.DataFrame()
	Output_DF['Voice_Text']=Inputs
	Output_DF['Actual_Text']=Correct
	pd.to_csv('data/test1.csv',index=False)

	return
#Pokemon Showdown Voice Controller
#Main Game Integration File
#Aditya Pandey, Nitish Mallick, Savya Sachi Pandey, Vivek Kumar
#Note: Check the README and report for a full understanding of how this works
from poke_env import PlayerConfiguration
from poke_env.player import Player, RandomPlayer
from difflib import SequenceMatcher
import asyncio
import time
import speech_recognition as sr
import keyboard
from fuzzywuzzy import fuzz
import fuzzy
from transformers import BertModel
import torch
import torch.nn as nn
from transformers import BertTokenizer
import numpy as np
import pandas as pd
import openai
import time
import os
from functools import partial
import random
from collections import Counter
import tqdm
import re
import pyautogui
import IDM_Functions as idm
import IDM_BertBinaryClassifier as BertBinaryClassifier
import Baseline_Functions as Baseline


#################################################################
def MicMove():
	'''This function initializes the system audio input, cleans up some of the incoming audio, and parses it
	into text using the Googel Speech Recognition Library'''

	# Initialize the recognizer
	r = sr.Recognizer()
	start=time.time()

	# Start listening
	with sr.Microphone() as source:

		# Adjust for ambient noise
		delay=0
		pressed=False

		while True:

			#Listens on average for 15 seconds, unless text recognized.

	    	#Auto Mute System Audio
	        if pressed==False:
	        	pyautogui.press('volumemute')
	        	pressed=True

	        
	        #Ambient Noise Reduction
	        r.adjust_for_ambient_noise(source)
	        audio = r.listen(source)


	        stop=time.time()
	        if (stop-start)>30:
	        	print("Time Passed:",round(stop-start)," s")

	        try:
	            # Use the google speech reognizer recognizer to convert speech to text
	            text = r.recognize_google(audio)
	            pyautogui.press('volumemute')
	            print("Text Detected:",text)
	            return text
	            
	        except sr.UnknownValueError:
	            print("Sorry, couldn't recognize what you said")

	        except sr.RequestError as e:
	            print("Sorry, an error has occurred with the API {0}".format(e))

#################################################################
def callMicOnKeyWordOrPress(key,button='shift'):
	'''This function calls the above Mic Move Function either when the shift key is pressed, or when a keyword 
	is spoken.'''

	# Initialize the recognizer
	r = sr.Recognizer()
	start=time.time()

	with sr.Microphone() as source:
	    print("Listening for Keyword....")

	    #Again, ambient Noise Reduction
	    r.adjust_for_ambient_noise(source)

	    while True:

	        audio = r.listen(source)

	        #Safeguard to end the loop if 60 seconds pass
	        stop=time.time()
	        if (stop-start)>60:
	        	return False
	        
	        try:
	            # Use the recognizer to convert speech to text
	            text = r.recognize_google(audio)
	            
	            #Core Condition
	            if get_phonetic_similarity(key.lower(),text.lower())>50 or keyboard.is_pressed(button):
	            	print("Starting to Listen for command")
	            	return True
	            
	        except sr.UnknownValueError:
	            print("Sorry, couldn't recognize what you said")

	        except sr.RequestError as e:
	            print("Sorry, an error has occurred with the API {0}".format(e))

#################################################################
def display(battle):
	'''This function just displays the battle state in a Pokemon Showdown Game'''

	print('*'*50)
	print()
	print('Attack Moves:')
	for i in range(0,3,2):

		if i+1<len(battle.available_moves):
			print(f"{battle.available_moves[i].id:<15}{battle.available_moves[i+1].id}")

		elif i<len(battle.available_moves):
			print(battle.available_moves[i].id)

	print()
	print()
	print('Pokemon in Team:')
	for each in battle.available_switches:
		print(each.species)

	print()


#################################################################
class Voice_Player(Player):
	'''This class Governs the Voice Player, and extends the poke-env Player class.'''
    #Launch:node pokemon-showdown start --no-security


    def choose_move(self, battle):
    	'''Our function of interest, the logic that governs choosing the move. It prompts for mic input, and then
    	 makes the corresponding in game action.'''

    	#Print the battle state
    	display(battle)

    	#The Name of the users current active pokemon, to be used as the keyword for Mic Activation
    	key=battle.active_pokemon.species

    	#Takes in Mic Input
    	if callMicOnKeyWordOrPress(key):
    		usermove=MicMove()

    	#Pipeline of a Move:
    	#1. Intent
    	#2. Object ID
    	#3. Phoneme Similarity


    	Intent=idm.predict_text(usermove)
    	print("User Intent:",Intent)

    	Object=idm.pred_gpt(usermove).split(",")[1].split(")")[0]

    	print("Object Id: ",Object)

    	best_move=idm.mostsimilarphone(battle,Object,Intent)

    	if best_move!=False:
    		return self.create_order(best_move)

    	else:
    		print("Sorry, thats an invalid move!")
    		return self.choose_move(battle)

###############################################################################################

async def main():
	'''The main method runs the game loop, starting one voice player battle. 
	In theory, this class can be expanded to any number of players.'''

    start = time.time()

    # We create two players.
    random_player = RandomPlayer(
        battle_format="gen8randombattle",
    )
    voice_player = Voice_Player(
        battle_format="gen8randombattle",
    )

    # Now, let's evaluate our players
    await voice_player.battle_against(random_player, n_battles=1)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
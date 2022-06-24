import time
import json

from pathlib import Path

try:
	import mouse, keyboard
except ModuleNotFoundError:
	print('Mouse and keyboard modules not found. Did you forget to [pip install -r requirements.txt]?')
	exit(1)
except ImportError:
	print('Sorry, you have to be on root to use this on Linux due to a limitation with the keyboard and mouse modules.')
	exit(1)

def main():
	print('''Starting SSBot. Don't use this to fake a score, you won't get away with it.''')
	if Path('./config.json').exists():
		try:
			with open('./config.json','r') as config_file:
				config = json.load(config_file)
			i = input('Would you like to reset config?\n[Y] for yes, [Not Y] for no\n')
			do_config = i.lower() == 'y'
		except:
			print('Config file invalid, resetting config...')
			do_config = True
	else:
		print('''Config file not found. Assuming this is your first time using SSBot:
1: In SS+, go to Settings > Camera & Control.
2: Set your sensitivity to 1.
3: Uncheck "Lock Mouse".

Now calibrating playfield. Please open a map and pause the game.''')
		do_config = True
	if do_config:
		with open('./config.json','w+') as config_file:
			config = json.dump({'first_time':True},config_file)
	def move_to(x,y,center):
		x, y = ((1-x)*55.3333333333)+center[0], ((1-y)*55.3333333333)+center[1]
		mouse.move(x,y)
	i = None
	while i not in ['1','2']:
		i = input('Input a song with:\n[1] Data file path [.txt]\n[2] Paste in data\n')
	match i:
		case '1':
			while 1:
				i = input('Input file path: ')
				try:
					with open(i,'r') as f:
						song_data = f.read()
					break
				except FileNotFoundError:
					continue
		case '2':
			song_data = input('Input song data: ')
	song_raw = [[float(n) for n in note.split('|')] for note in song_data.split(',')[1:]]
	song = []
	notes = []
	avg = lambda args: sum(args)/len(args)
	for note in song_raw:
		if len(notes):
			if note[2]-notes[0][2] < 10:
				notes.append(note)
			else:
				song.append([avg([note[0] for note in notes]),avg([note[1] for note in notes]),notes[0][2]])
				notes = [note]
		else:
			notes.append(note)
	if len(notes):
		song.append([avg([note[0] for note in notes]),avg([note[1] for note in notes]),notes[0][2]])
	print('Song loaded, click play\nPress F7 when the first note is at the timing window to start')
	keyboard.wait(65) #wait for F7
	center = mouse.get_position()
	old_time = time.perf_counter()
	offset = song[0][2]
	print(f'\rOffset set to {offset}ms',end='                     ')
	move_to(*song[0][:2],center)
	old_note = song.pop(0)
	easing = lambda t: (t - 1) * (t - 1) * (t - 1) + 1
	while len(song):
		note = song[0]
		try:
			delta = (time.perf_counter()-(old_time + ((old_note[2]-offset)/1000)))/(((note[2]-offset)/1000)-((old_note[2]-offset)/1000))
			delta = easing(delta)
		except ZeroDivisionError:
			delta = 1
		move_to(*[(old*(1-delta))+(new*delta) for old, new in zip(old_note[:2],note[:2])],center)
		if delta >= 1:
			old_note = song.pop(0)
		if keyboard.is_pressed(77):
			if kr:
				kr = False
				offset += 10 if keyboard.is_pressed('shift') else 1
				print(f'\rOffset set to {offset}ms',end='                     ')
		else:
			kr = True
		if keyboard.is_pressed(75):
			if kl:
				kl = False
				offset -= 10 if keyboard.is_pressed('shift') else 1
				print(f'\rOffset set to {offset}ms',end='                     ')
		else:
			kl = True
		if keyboard.is_pressed(57) or keyboard.is_pressed(1):
			print('\n[!] Song stopped prematurely.')
			break
	print('\nSong finished!')


if __name__ == "__main__":
	main()
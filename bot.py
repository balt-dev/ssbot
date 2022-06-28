import math
import os
import time
import json
import struct
import easing_functions
from pathlib import Path

try:
	import mouse, keyboard
except ModuleNotFoundError:
	print('Mouse and keyboard modules not found. Did you forget to [pip install -r requirements.txt]?')
	exit(1)
except ImportError:
	print('Sorry, you have to be on root to use this on Linux due to a limitation with the keyboard and mouse modules.')
	exit(1)

def load_sspm(file):
	'''
	Load the notes from a .sspm. Pass in a file object.
	'''
	assert file.read(4) == b'SS+m', 'Invalid header! Did you select a .sspm?' # Header
	version = int.from_bytes(file.read(2),'little')
	if version == 1:
		assert int.from_bytes(file.read(2),'little') == 0, 'Reserved bytes were not 0! Did you try to load a modchart?'
		while file.read(1) != b'\x0A': pass #id
		while file.read(1) != b'\x0A': pass #name
		while file.read(1) != b'\x0A': pass #creator
		file.seek(4,1) #ms length
		file.seek(4,1) #note count
		file.seek(1,1) #difficulty + 1
		match int.from_bytes(file.read(1),'little'): #is there a cover
			case 1:
				file.read(2) #im width
				file.read(2) #im height
				file.read(1) #mip (huh?)
				file.read(1) #format
				clen = file.read(8) #content length
				file.read(int.from_bytes(clen,'little'))
			case 2:
				clen = file.read(8) #content length
				file.read(int.from_bytes(clen,'little'))
		file.read(1) #music storage type
		clen = file.read(8) #content length
		file.read(int.from_bytes(clen,'little')) #music data
		notes = []
		while len(timing_raw := file.read(4)): #for the rest of the file
			timing = int.from_bytes(timing_raw,'little') #timing
			if int.from_bytes(file.read(1),'little'): #if it's a quantum note
				x,y = struct.unpack('f',file.read(4))[0],struct.unpack('f',file.read(4))[0] #float coords
			else:
				x,y = int.from_bytes(file.read(1),'little'),int.from_bytes(file.read(1),'little') #int coords
			notes.append([2-x,2-y,timing])
		return notes[1:] #for some reason there's a weird note that doesn't actually exist in-game, so i clip it off here
	#elif version == 2: ...
	else:
		raise AssertionError('Unsupported map version!')

def main():
	print('''\x1b[H\x1b[2JStarting SSBot. Don't use this to fake a score, you won't get away with it.''')
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
3: Uncheck "Lock Mouse".''')
		do_config = True
	if do_config:
		easings = {k:v for k,v in easing_functions.__dict__.items() if (not k.startswith('__')) and (k != 'easing')}
		print('Pick an easing function to use:')
		for i, easing in enumerate(easings):
			print(f'[{i}] {easing}')
		while (i := int(input('> '))) not in range(len(easings.keys())): pass
		with open('./config.json','w+') as config_file:
			config = {'easing':list(easings.keys())[i]}
			json.dump(config,config_file)
	easing = easing_functions.__dict__[config['easing']](start=0,end=1)
	def move_to(x,y,center):
		x, y = ((1-x)*55.3333333333)+center[0], ((1-y)*55.3333333333)+center[1]
		mouse.move(x,y)
	is_text = True
	while True:
		i = input('\x1b[H\x1b[2JInput a song with:\n[1] Raw data [paste in]\n[1] Raw data [.txt]\n[3] SS+ map file [.sspm]\n[4] SS+ map pack [.sspmr] (Legacy)\n[5] Vulnus map [.json]\n')
		if i == '1':
			song_raw = [[float(n) for n in note.split('|')] for note in input('Input song data: ').split(',')[1:]]
		else:
			while (not Path(f_path := input('Input file path: ')).exists()): pass
			match i:
				case '2':
					with open(f_path,'r') as f:
						song_raw = [[float(n) for n in note.split('|')] for note in f.read().split(',')[1:]]
					break
				case '3':
					try:
						with open(f_path,'rb') as f:
							song_raw = load_sspm(f)
					except AssertionError as e:
						print(f'Error while parsing map!\n{e.args[0]}\n')
				case '4':
					songs = {}
					with open(f_path,'r') as f:
						for line in f.readlines():
							if line.startswith('#'):
								pass
							else:
								s = line.split(':~:')
								songs[s[2]] = s[-1] #name: data
					page = 0
					while True:
						print("\x1b[H\x1b[2J", end="")
						song_names = list(songs.keys())
						song_names.sort()
						for i, name in enumerate(song_names[page*10:(1+page)*10]):
							print(f'[{i}] {name}')
						print(f'\nPage {page}/{len(songs)//10}\n[.] Next page\n[,] Previous page')
						i = input('> ')
						if i in [str(n) for n in range(10)]: #isnumeric sucks
							song_raw = [[float(n) for n in note.split('|')] for note in songs[song_names[page*10+int(i)]].split(',')[1:]]
							break
						elif i == ',':
							page = (page-1)%math.ceil(len(songs)/10)
						elif i == '.':
							page = (page+1)%(len(songs)//10)
				case _:
					print("\x1b[H\x1b[2J", end="")
					continue
		break
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
	start_timing = song[0][2]
	offset = start_timing
	print(f'\rOffset set to {offset-start_timing}ms',end='                     ')
	move_to(*song[0][:2],center)
	old_note = song.pop(0)
	while len(song):
		note = song[0]
		try:
			t = (time.perf_counter()-(old_time + ((old_note[2]-offset)/1000)))/(((note[2]-offset)/1000)-((old_note[2]-offset)/1000))
			t = min(max(t,0),1) #clamp between 0 and 1
			delta = easing(t)
		except ZeroDivisionError:
			delta = 1
		move_to(*[(old*(1-delta))+(new*delta) for old, new in zip(old_note[:2],note[:2])],center)
		if delta >= 1:
			old_note = song.pop(0)
		if keyboard.is_pressed(77):
			if kr:
				kr = False
				offset += 10 if keyboard.is_pressed('shift') else 1
				print(f'\rOffset set to {offset-start_timing}ms',end='                     ')
		else:
			kr = True
		if keyboard.is_pressed(75):
			if kl:
				kl = False
				offset -= 10 if keyboard.is_pressed('shift') else 1
				print(f'\rOffset set to {offset-start_timing}ms',end='                     ')
		else:
			kl = True
		if keyboard.is_pressed(57) or keyboard.is_pressed(1):
			print('\n[!] Song stopped prematurely.')
			break
	print('\nSong finished!')


if __name__ == "__main__":
	main()
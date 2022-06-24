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
	print('SSPlusBot v3')
	if Path('./config.json').exists():
		try:
			with open('./config.json','r') as config_file:
				config = json.load(config_file)
				center = config['center']
			i = input('Would you like to recalibrate?\n[Y] for yes, [Any else] for no\n')
			do_config = i.lower() == 'y'
		except:
			print('Config file invalid, recalibrating...')
			do_config = True
	else:
		print('Config file not found, calibrating...')
		do_config = True
	if do_config:
		print('Move your cursor to the top left of the play field and press F8.')
		keyboard.wait('f8')
		top_left = mouse.get_position()
		print('Move your cursor to the bottom right of the play field and press F8.')
		keyboard.wait('f8')
		bottom_right = mouse.get_position()
		center = [(a+b)//2 for a,b in zip(top_left,bottom_right)]
		with open('./config.json','w+') as config_file:
			config = json.dump({'center':center},config_file)
	def move_to(x,y):
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
	song = [[float(n) for n in note.split('|')] for note in song_data.split(',')[1:]]
	print('Song loaded, click play and press F8\nPress F7 when the first note is at the timing window to start')
	keyboard.wait(66)
	mouse.move(*center)
	keyboard.wait(65) #wait for F7
	old_time = time.perf_counter()
	offset = song[0][2]
	print(f'\rOffset set to {offset}ms',end='                     ')
	move_to(*song[0][:2])
	old_note = song.pop(0)
	while len(song):
		note = song[0]
		delta = (time.perf_counter()-(old_time + ((old_note[2]-offset)/1000)))/(((note[2]-offset)/1000)-((old_note[2]-offset)/1000))
		move_to(*[(old*(1-delta))+(new*delta) for old, new in zip(old_note[:2],note[:2])])
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
	print('\nSong finished!')


if __name__ == "__main__":
	main()
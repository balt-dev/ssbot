try:
	import win32api, win32con
except ModuleNotFoundError:
	print('Modules win32api and win32con not found. Did you forget to [pip install -r requirements.txt]?')
	exit()
import time

def move_to_note(note,old_note):
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,int(((2-note[0])-(2-old_note[0]))*200*0.3),int(((2-note[1])-(2-old_note[1]))*200*0.3))

if __name__ == "__main__":
	print('SSPlusBot v0.0.1')
	song = [[float(n) for n in note.split('|')] for note in input('Paste song data string here:\n').split(',')[1:]]
	print('Song loaded')
	while not win32api.GetAsyncKeyState(ord('P')):
		time.sleep(0.01)

	old_note = [1.0,1.0,0]
	dtime = time.time()
	offset = 320
	print(f'Offset set to 320ms',end='                     ')
	while len(song):
		if dtime <= (dtime + (song[0][3]+offset)/1000) <= time.time():
			move_to_note(song[0],old_note)
			old_note = song.pop(0)
		if win32api.GetAsyncKeyState(win32con.VK_RIGHT):
			if kr:
				kr = False
				offset += 10 if win32api.GetAsyncKeyState(win32con.VK_SHIFT) else 1
				print(f'\rOffset set to {offset}ms',end='                     ')
		else:
			kr = True
		if win32api.GetAsyncKeyState(win32con.VK_LEFT):
			if kl:
				kl = False
				offset -= 10 if win32api.GetAsyncKeyState(win32con.VK_SHIFT) else 1
				print(f'\rOffset set to {offset}ms',end='                     ')
		else:
			kl = True
	print('Song finished!')
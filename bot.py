import time
import winreg
import sys
import os

try:
	import win32api, win32con
except ModuleNotFoundError:
	print('Modules win32api and win32con not found. Did you forget to [pip install -r requirements.txt]?')
	exit(1)

def main():
	print('SSPlusBot v0.1.0')
	reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
	with winreg.OpenKeyEx(reg, 'Control Panel\Mouse', 0, winreg.KEY_READ) as regkey:
		print('Read-only access gained to registry key HKEY_CURRENT_USER\Control Panel\Mouse')
		if not winreg.QueryValueEx(regkey,'MouseSpeed')[0]:
			sys.stderr.write('''"Enhance pointer precision" is currently on in mouse settings,
which makes this unusable. 
Please turn it off and reopen.''')
			os.system('start ms-settings:mousetouchpad')
			return
		speed = int(winreg.QueryValueEx(regkey,'MouseSensitivity')[0])
		# i made a data table and this seems to be piecewise? i may be wrong
		if speed < 5:
			ratio = (2**(6-speed))
			d_ratio = f'2^{6-speed}'
		elif 5 <= speed < 9:
			ratio = (12-speed)/3
			d_ratio = f'{12-speed}/3'
		else:
			ratio = 2/((speed/2))
			d_ratio = f'2/{int(speed/2) if int(speed/2) == speed/2 else speed/2}'
		print(f'Calculated inverse of mouse sensitivity ratio for raw pixel movement: {d_ratio} ({ratio:.6f})')
	def move_to_note(note,old_note):
		win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,int(((2-note[0])-(2-old_note[0]))*200*ratio),int(((2-note[1])-(2-old_note[1]))*200*ratio))
	song = [[float(n) for n in note.split('|')] for note in input('Paste song data string here:\n').split(',')[1:]]
	print('Song loaded, press F7 to start')
	while not win32api.GetAsyncKeyState(win32con.VK_F7):
		time.sleep(0)
	old_time = time.time()
	offset = song[0][2]
	print(f'\rOffset set to {offset}ms',end='                     ')
	move_to_note(song[0],[1.0,1.0,0])
	old_note = song.pop(0)
	while len(song):
		x, y = [], []
		for note in song[:10]:
			if (old_time + ((old_note[2]-offset)/1000)) <= (old_time + ((note[2]-offset)/1000)) <= time.time():
				x.append(note[0])
				y.append(note[1])
				timing = song.pop(0)[2]
		if len(x):
			move_to_note([sum(x)/len(x),sum(y)/len(y)],old_note)
			old_note = [sum(x)/len(x),sum(y)/len(y),timing]
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
	print('\nSong finished!')


if __name__ == "__main__":
	main()
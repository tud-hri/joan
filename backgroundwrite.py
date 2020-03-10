# Python3 program to write file in 
# background 

# Importing the threading and time 
# modules 
import threading 
import time 

# Inherting the base class 'Thread' 
class AsyncWrite(threading.Thread): 

	def __init__(self, text, out): 

		# calling superclass init 
		threading.Thread.__init__(self) 
		self.text = text 
		self.out = out 

	def run(self): 

		f = open(self.out, "a") 
		f.write(self.text + '\n') 
		f.close() 

		# waiting for 2 seconds after writing 
		# the file 
		time.sleep(2) 
		print("Finished background file write to", 
										self.out) 

def Main(): 
	
	message = "Geeksforgeeks"
	background = AsyncWrite(message, 'out.txt') 
	background.start() 
	
	print("The program can continue while it writes") 
	print("in another thread") 
	print("100 + 400 = ", 100 + 400) 

	# wait till the background thread is done 
	background.join() 
	print("Waited until thread was complete") 

if __name__=='__main__': 
	Main() 

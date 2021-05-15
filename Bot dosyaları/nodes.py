from selenium import webdriver
import keyboard,time
import os
import wmi



driver = webdriver.Chrome("C:\Program Files\Google\Chrome\Application\chromedriver.exe")
driver.get("https://www.ethernodes.org/tor-seed-nodes")





while 1:
	os.system("start cmd")
	time.sleep(1)
	keyboard.write("cd..")

	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("cd..")

	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("cd..")
	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("cd..")
	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("cd program files")
	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("cd geth")
	keyboard.press("enter")
	time.sleep(0.01)
	keyboard.write("geth attach \\\.\pipe\geth.ipc")
	keyboard.press("enter")
	time.sleep(0.01)
	

	brs=driver.find_elements_by_class_name('text-white')

	
	

	file1 = open("enodes.txt","w")
		
	for element in brs:
	    file1.write(str(element.text))
	    
	file1.close()
	file1 = open("enodes.txt","r")
	Lines = file1.readlines()
	
	for line in Lines:
		keyboard.write('admin.addPeer("{}")'.format(line.strip()))
		time.sleep(0.01)
		keyboard.press("enter")

	file1.close()
	keyboard.write('net.peerCount')
	keyboard.press("enter")
	time.sleep(5)
	#ti = 0  
	#name = 'geth.exe'
	#f = wmi.WMI()
	#for process in f.Win32_Process():
	    
	 #   if process.name == name:
	  #      process.Terminate()
	   #     ti += 1

	#if ti == 0:
	  #  print("Process not found!!!")
	keyboard.press_and_release('ctrl+d') 
	time.sleep(1)    
	os.system("taskkill /f /im cmd.exe")
	#os.system("taskkill /f /im chromedriver.exe")
	time.sleep(10)
	
	
	
	driver.refresh()
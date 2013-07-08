#Author: Alex Anderson
#Date: 2013-5-7
#This script generates a text file for a scanning + stretching experiment which
#is subsequently parsed by the "Exerimental Sequencer" running in Labview.
#
#The format for commands written to file is important and should not be
#modified.

import os

#Set the processes required (1 = yes)
scopecam = 1
motors = 1

#Set the limits of travel (um)
lower_lim = 0
upper_lim = 1000
step_size = 200
step_time = 1 #seconds

#Set Cam Capture Frequency (Hz)
img_cap_freq = 100
img_count = 2

#If it's a stretching experiment define the final stretch and stretch increments
#Final stretch is determined in terms of  initial muscle length.
muscle_length = upper_lim - lower_lim
final_stretch = 40 #percent muscle length
stretch_inc = 5
stretch_step = (final_stretch/stretch_inc/100.0) * muscle_length

#Generate the stretch steps range
stretch = range(0, final_stretch, final_stretch/stretch_inc)

#Generate the scan steps range
scan = range(lower_lim,upper_lim,step_size)

#Get target dest and open file
folder = raw_input("Enter folder location: ")
os.chdir(folder)
filename = raw_input("Enter file name: ")
seq_file = open(filename, "w")

seq_file.write("#Initialising\n") #Demarcating a section
#Open necessary UIs and Init Processes
if scopecam == 1:
    seq_file.write("Launch Scope Cam UI\n")
    seq_file.write("Init Cam," + str(img_cap_freq) + "\n")

if motors == 1:
    seq_file.write("Launch Gen HW UI\n")
    seq_file.write("Init Motors\n")

#Always initialise data storage
seq_file.write("Init Data Storage\n")
 
i = 0
while i <= stretch_inc:
	#This for prints "Scan Relative" commands in increments of step_size. If the final
	#step would take us past the upper limit, then the final command is regenerated
	#sufficient to take us not further than the limit.
	dist_travelled = 0
	seq_file.write("#Scanning\n") # This is just to break up the text a little bit
	for step in scan:
		seq_file.write("Capture Image," + str(img_count) + "\n")	
		dist_travelled += step_size
		if dist_travelled < upper_lim:
			seq_file.write("Scan Relative," + str(step_size) + "," + str(step_time) + "\n")
		else:
			dist_travelled -= step_size
			last_step = upper_lim - dist_travelled
			seq_file.write("Scan Relative," + str(last_step) + "," + str(step_time) + "\n")
			dist_travelled += last_step
	
	
	#Capture final images then return
	seq_file.write("Capture Image," + str(img_count) + "\n")
	seq_file.write("Scan Relative," + str(-dist_travelled) + "," + str(step_time) + "\n")
	
	#Stretch the muscle
	seq_file.write("#Stretching\n")
	#Make sure we don't stretch one too far
	if i < stretch_inc:
		seq_file.write("Move Relative,US," + str(stretch_step) + "," + str(step_time) + "\n")
	i += 1

seq_file.write("Move Relative,US," + str(-(stretch_inc*stretch_step)) + "," + str(step_time) + "\n")

seq_file.write("End Experiment\n")
seq_file.close()

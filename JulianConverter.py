#___________________________JULIAN DAY CALCULATOR____________________________________#
#This program converts a traditional calendar date to a Julian Day, and visa versa

print "*****Julian Day/Calendar Day Calculator*****"
print "Press Ctrl Z any time to exit"
kr= 1                             #Creates an infinite loop to ease continuous use (kr= keep running)
while kr==1:


    a= range(1, 32)               # Creating variables that correspond to the three ranges of days
    b= range(1, 29)               # a month can have
    c= range(1, 31)

    bl= range(1, 30)              # This range if for the month of February during a Leap year
    print " "                     #Provides a blank space to ease use


    quest= int(input("Julian to Calendar (1), Calendar to Julian (2)  "))# Asks user for input
    print " "                     #Provides a blank space to ease use


    if quest == 1: 	          # If the user wants to convert a Julian Day to a traditional date format, this loop is executed
        julian= int(input("Enter Julian day number  "))              #Asks user for Julian Day 
	  
        leap= int(input("Is it a leap year? Y= 1 N= 2  "))               #Asks user to specify whether it is a leap year or not
	  
        if leap == 2:             #This loop executes if it is not a Leap year
            if julian >0 and julian <32:        #Specifies range of Julan Days that January falls in
                month= "January"                #If the Julian day falls within that range, then the month is January
                day= a[julian-1]                # Subtracts difference between first day of month and place within range
                print month, day			#Outputs the month and day of the specified Julian Day to the user

            elif julian >=32 and julian <60:
                month= "February"
                day= b[julian-32]
                print month, day

            elif julian >=60 and julian <91:
                month= "March"
                day= a[julian-60]
                print month, day

            elif julian >=91 and julian <121:
                month= "April"
                day= c[julian-91]
                print month, day

            elif julian >=121 and julian <152:
                month= "May"
                day= a[julian-121]
                print month, day

            elif julian >=152 and julian <182:
                month= "June"
                day= c[julian-152]
                print month, day

            elif julian >=182 and julian <213:
                month= "July"
                day= a[julian-182]
                print month, day

            elif julian >=213 and julian <244:
                month= "August"
                day= a[julian-213]
                print month, day

            elif julian >=244 and julian <274:
                month= "September"
                day= c[julian-244]
                print month, day

            elif julian >=274 and julian <305:
                month= "October"
                day= a[julian-274]
                print month, day

            elif julian >=305 and julian <335:
                month= "November"
                day= c[julian-305]
                print month, day

            elif julian >=335 and julian <366:
                month= "December"
                day= a[julian-335]
                print month, day

        if leap == 1:
            if julian >0 and julian <32:
                month= "January"
                day= a[julian-1]
                print month, day

            elif julian >=32 and julian <61:
                month= "February"
                day= bl[julian-32]
                print month, day

            elif julian >=61 and julian <92:
                month= "March"
                day= a[julian-61]
                print month, day

            elif julian >=92 and julian <122:
                month= "April"
                day= c[julian-92]
                print month, day

            elif julian >=122 and julian <153:
                month= "May"
                day= a[julian-122]
                print month, day

            elif julian >=153 and julian <183:
                month= "June"
                day= c[julian-153]
                print month, day

            elif julian >=183 and julian <214:
                month= "July"
                day= a[julian-183]
                print month, day

            elif julian >=214 and julian <245:
                month= "August"
                day= a[julian-214]
                print month, day

            elif julian >=245 and julian <275:
                month= "September"
                day= c[julian-245]
                print month, day

            elif julian >=275 and julian <306:
                month= "October"
                day= a[julian-275]
                print month, day

            elif julian >=306 and julian <336:
                month= "November"
                day= c[julian-306]
                print month, day

            elif julian >=336 and julian <367:
                month= "December"
                day= a[julian-336]
                print month, day
                
    n=[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334] 
    nl= [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

    if quest == 2:
        month= int(input("Enter month number  "))
	  
        day= int(input("Enter the day number  "))
	  
        leap= int(input( "Is it a leap year? Y= 1 N= 2  "))
	   

        x = 1
        if leap == 2:
            if month>12 or day > 31:
                print('Please enter a valid entry')
            while x <=12:
                if month == x:
                    julian = n[x-1]+ day
                    print julian
                x = x+1
                    
                
        elif leap == 1:
            if month>12 or day > 31:
                print('Please enter a valid entry')
            while x <=12:
                if month == x:
                    julian = nl[x-1]+ day
                    print julian
                x = x+1      




x = range(10)

#Lambda method
adjustment = 2
print 'Simple lambda function',map(lambda i: i**2 + adjustment,x)


#Function method
def square_adjust(x,adjustment = 2):
    return x**2 + adjustment

print 'Map declared function',map(square_adjust,x)

import itertools
#Iter option
def square_adjust_2_arguments(x,adjustment):
    return x**2 + adjustment

#Use map for
print 'Map declared function 2 arguments',map(square_adjust_2_arguments,x,range(len(x)))

#This does not work
print 'Map lambda function 2 arguments',map(lambda x,adjustment: x**2 + adjustment,x, range(len(x)))

#Can use itertools if the parameter is always the same
print 'Itertools',map(square_adjust_2_arguments,x,itertools.repeat(2,len(x)))


#Lambda filter
print 'Lambda filter', filter(lambda x: x > 5, x)



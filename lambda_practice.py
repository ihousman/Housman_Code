import os, sys
import operator, numpy
from scipy import stats
##
##def call_func(f, *args):
##    return f(*args)
##
##x = call_func(operator.countOf, ['hello', 'there'], ['l', 'e'])
###print x
###print operator.countOf(range(50), 5)
##
##x = numpy.array(range(200))
##x = x.reshape ((4, 5, 10))
##print x
##
##
###y = x**2
###y = call_func(operator.getslice, x[0:], x)
###print x
###print y
###print operator.getslice(x[0])
##def power(x, n):
####    """
####    Computes the result of x raised to the power of n.
####
####        >>> power(2, 3)
####        8
####        >>> power(3, 2)
####        9
####    """
##    if n == 0:
##        return 1
##    else:
##        print n
##        return x * power(x, n-1)
##
##print power(2,5)
#for i in range(10):
    #exec('var_' + str(i) + '=' + str(i))
dim = (40,5,2)
z = numpy.array(range(400)).reshape(dim)
print z
z = numpy.transpose(z)
#z = numpy.reshape(z, dim)
print
print z
print
print
i = 0
List =  numpy.array(list(z.flat)).reshape((dim[1] * dim[2], dim[0]))
print List
x = range(dim[0])
t_array = []
for i in x:
    t_array.append(numpy.array([i] * (dim[1] * dim[2])).reshape([dim[1], dim[2]]))
print t_array
t_array = numpy.array(t_array)
print t_array
#x = numpy.array(range(10)*40).reshape(dim)
print 'x',len(x)

#stat_list = [list(stats.pearsonr(range(len(List[i])), List[i])) for i in range(len(List))]
#print stat_list
##for row in List:
##    print row
##    
##    print numpy.polyfit(range(len(row)), row, 2) 
##    stat = list(stats.linregress(range(len(row)), row))
##    print stat
    
#List = 
##incrementer = dim[0]
##while i < len(List):
##    print List[i:i + incrementer]
##    i += incrementer
##List = numpy.array(List)
##List = List.reshape((dim[2], dim[1], dim[0]))
##List = numpy.transpose(List)
#print List
#print z.ndim

import random
import time
import datetime
import sys

#maximum possible time
NEVER = sys.float_info.max

def weibull_random(shape, scale):
    #random.weibullvariate(alpha,beta), where alpha is the scale and beta the shape
    return random.weibullvariate(scale, shape)

#returns a death time in the future (drawn from the weibull distribution with shape 0.4 and the provided scale)
#returns the maximum available time if scale == 0. This means that the peer will never die.
#the return type is a float (number of seconds after the initial time, the epoch)
def new_death_time(scale):
    if scale == 0:
        return NEVER   #maximum float
    else:
        return time.mktime(time.localtime()) + weibull_random(0.4,scale)

#returns true if the present moment in time is beyond death_time
def time_to_die(death_time):
    return (death_time-time.mktime(time.localtime())<=0)

'''
i=0
while i<100:
    print(weibull_random(0.4,30))
    i += 1
'''
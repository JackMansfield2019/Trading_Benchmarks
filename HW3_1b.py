import random
import numpy as np
#import Tkinter
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import math
import random

def parse(filename : str):

    with open(filename, 'r') as f:
        lines = f.readlines()
    n = len(lines)
    data = np.zeros(shape = (n,2))

    i = 0
    for line in lines:
        arr = line.split(" ")
        data[i][0] = float(arr[0])
        data[i][1] = float(arr[1].replace("\n", ""))
        i+=1

    return data

def calc_non_risk_adjusted(data, Bond, flag):
    n = len(data)
    
    cul_returns = 0.0
    cul_returns_squared = 0.0
    max_cul_returns = -9999
    MDD = -9999
    for i in range(1,n):
        r =  math.log(data[i][1]/data[i-1][1]) #- math.log(Bond[i][1]/Bond[i-1][1])
        cul_returns += r
        cul_returns_squared += r*r

        if (cul_returns > max_cul_returns):
            max_cul_returns = cul_returns
        
        if(max_cul_returns - cul_returns > MDD):
            MDD = max_cul_returns - cul_returns
    mean = cul_returns/n
    mean = mean * 19500
    var = (1/n)*(cul_returns_squared) - math.pow( (1/n)*cul_returns ,2)
    var = var * 19500
    sharp = mean/math.sqrt(var)
    if(flag == 1):
        sterling = 0
    else:    

        sterling = mean/MDD
    #sterling = 0
    return (mean,var,sharp,sterling)

def calc_stats_stocks(data, Bond, flag):
    n = len(data)
    
    cul_returns = 0.0
    cul_returns_squared = 0.0
    max_cul_returns = -9999
    MDD = -9999
    for i in range(1,n):
        r =  math.log(data[i][1]/data[i-1][1]) - math.log(Bond[i][1]/Bond[i-1][1])
        cul_returns += r
        cul_returns_squared += r*r

        if (cul_returns > max_cul_returns):
            max_cul_returns = cul_returns
        
        if(max_cul_returns - cul_returns > MDD):
            MDD = max_cul_returns - cul_returns
    mean = cul_returns/n
    mean = mean * 19500
    var = (1/n)*(cul_returns_squared) - math.pow( (1/n)*cul_returns ,2)
    var = var * 19500
    if(flag == 1):
        sterling = 0
        sharp = 0
        var = 0
    else:    
        var = var * 19500
        sharp = mean/math.sqrt(var)
        sterling = mean/MDD
    #sterling = 0
    return (mean,var,sharp,sterling)


def random_strat(IBM,Bond, tf):
    n = len(IBM)
    cul_returns = 0.0
    cul_returns_squared = 0.0
    max_cul_returns = -9999
    MDD = -9999
    stock = False
    for i in range(1,n):
        r = 0.0
        if(random.uniform(0, 1) >= 0.5 ):
            r =  math.log(IBM[i][1]/IBM[i-1][1]) - math.log(Bond[i][1]/Bond[i-1][1])
            if(not stock):
                r = r - tf
            stock = True
        else:
            if(stock):
                r = r - tf

        cul_returns += r
        cul_returns_squared += r*r

        if (cul_returns > max_cul_returns):
            max_cul_returns = cul_returns
        
        if(max_cul_returns - cul_returns > MDD):
            MDD = max_cul_returns - cul_returns
    mean = cul_returns/n
    mean = mean * 19500
    var = (1/n)*(cul_returns_squared) - math.pow( (1/n)*cul_returns ,2)
    var = var * 19500
    sharp = mean/math.sqrt(var)
    sterling = mean/MDD
    return (mean,sharp,sterling)

def optimal_strat(data0,data1,Bond, tf):
    n = len(data0)
    #create DP table 
    #DP[i][0] = stock (data0)
    #DP[i][1] = bond  (data1)
    DP = np.zeros(shape = (2,n))
    #Create optimal strategy 
    for i in range(0,n):

        r0 =  data0[i] - Bond[i]
        r1 =  data1[i] - Bond[i]
        
        if i == 0:

            DP[0][0] = (r0 - tf)
            DP[1][0] = r1
        else:
            DP[0][i] = max(DP[0][i-1]+r0,DP[1][i-1]+(r0-tf))
            DP[1][i] = max(DP[0][i-1]+(r1-tf),DP[1][i-1]+r1)
        #print(DP)
        #print()
    #print("best ending in stock:",(DP[0][n-1]))
    #print("best ending in bond:", DP[1][n-1])


    #backtrack and find optimal positons at each time step
    moves = np.zeros(shape = (n))
    if DP[0][n-1] > DP[1][n-1]:
        moves[n-1] = 0
    else:
        moves[n-1] = 1

    for i in reversed(range(0,n-1)):
        if(moves[i+1] == 0):
            if DP[0][i] > DP[1][i] - tf:
                moves[i] = 0
            else:
                moves[i] = 1
            
        else:
            if DP[1][i] >= DP[0][i] - tf:
                moves[i] = 1
            else:
                moves[i] = 0

    #calulate statistics for the optimal strat 
    cul_returns = 0.0
    cul_returns_squared = 0.0
    max_cul_returns = -9999
    MDD = -9999
    cul_returns_array = np.zeros(shape = (n))
    for i in range (0,n):


        if(i == 0):
            if(moves[i] == 0):
                r = data0[i] - Bond[i] 
                r = r - tf
            else:
                r = data1[i] - Bond[i]
        else:
            if(moves[i] == 0):
                r = data0[i] - Bond[i] 
                if(moves[i-1] == 1):
                    r = r - tf
            else:
                r = data1[i] - Bond[i]
                if(moves[i-1] == 0):
                    r = r - tf

        cul_returns += r
        cul_returns_array[i] = cul_returns
        cul_returns_squared += r*r
        if (cul_returns > max_cul_returns):
            max_cul_returns = cul_returns
        
        if(max_cul_returns - cul_returns > MDD):
            MDD = max_cul_returns - cul_returns
    mean = cul_returns/n
    mean = mean * 19500
    var = (1/n)*(cul_returns_squared) - math.pow( (1/n)*cul_returns ,2)
    var = var * 19500
    sharp = mean/math.sqrt(var)
    if(MDD == 0):
        sterling = 0
    else:
        sterling = mean/MDD
    return (mean,var,sharp,sterling,cul_returns_array)


IBM = parse("ibm.txt")
Dell = parse("Dell.txt")
Bond = parse("Bond.txt")
n = len(IBM)
'''
print(IBM)
print(Dell)
print(Bond)
print()
'''
print("Non risk adjusted statstics:")
#print(calc_stats_stocks(Bond))
top = "{:<16}".format("") + "{:<21}".format("mean") + "{:<20}".format("variance") + "{:<20}".format("sharp") + "{:<20}".format("sterling")

print(top)

tmp = calc_non_risk_adjusted(IBM,Bond,0)
print("IBM:  " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])
tmp = calc_non_risk_adjusted(Dell,Bond,0)
print("DELL: " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])
tmp = calc_non_risk_adjusted(Bond,Bond,1)
print("BOND: " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])

print()
print("risk adjusted statistics:")
#print(calc_stats_stocks(Bond))
top = "{:<16}".format("") + "{:<21}".format("mean") + "{:<20}".format("variance") + "{:<20}".format("sharp") + "{:<20}".format("sterling")

print(top)

tmp = calc_stats_stocks(IBM,Bond,0)
print("IBM:  " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])
tmp = calc_stats_stocks(Dell,Bond,0)
print("DELL: " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])
#tmp = calc_stats_stocks(Bond,Bond,1)
#print("BOND: " ,tmp[0],"  ",tmp[1],"  " ,tmp[2],"  ",tmp[3])

print("Bond: ","{:<23}".format("0"),"{:<23}".format("0"),"{:<23}".format("0"),"0")

top = "{:<25}".format("") + "{:<23}".format("0") + "{:<23}".format("0.0001") + "{:<23}".format("0.0002") + "{:<25}".format("0.0005")

#print("Bond: ","{:<23}".format("0"),"{:<23}".format("0"),"{:<23}".format("0"))
print()


costs = [0, 0.0001, 0.0002, 0.0005]
data = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
j = 0
for tf in costs:
    avg_mean = 0
    avg_sharp = 0
    avg_sterling = 0
    for i in range(0,1):
        answer = random_strat(IBM,Bond, tf)
        avg_mean += answer[0]
        avg_sharp += answer[1]
        avg_sterling += answer[2]
    avg_mean = avg_mean / 1
    avg_sharp = avg_sharp/ 1
    avg_sterling = avg_sterling / 1
    data[0][j] = avg_mean
    data[1][j] = avg_sharp
    data[2][j] = avg_sterling
    j +=1
print("random Strategy benchmark:")
stat_headers = ["avg_mean", "avg_sharp", "avg_sterling"]
y_headers = ["0", "0.0001", "0.0002", "0.0005"]
print(top)
for header, row in zip(stat_headers, data):
    header = header +":" 
    header = "{:<15}".format(header)
    print(header,"{:<20}".format(row[0]),"  ","{:<20}".format(row[1]),"  ","{:<20}".format(row[2]),"  ","{:<20}".format(row[3]))

IBM_returns = np.zeros(shape = (n-1))

Dell_returns = np.zeros(shape = (n-1))

Bond_returns = np.zeros(shape = (n-1))

for i in range(0,n-1):
    IBM_returns[i] = math.log(IBM[i+1][1]/IBM[i][1])
    Dell_returns[i] = math.log(Dell[i+1][1]/Dell[i][1]) 
    Bond_returns[i] = math.log(Bond[i+1][1]/Bond[i][1])

'''
example from class
s = [1,-2,3,2,1]
b = [1,1,1,1,1]
result = optimal_strat(s,b,b,1)
'''
print()
print("optimal Strategy benchmark:")
result = optimal_strat(IBM_returns,Dell_returns,Bond_returns,0.02)
top = "{:<16}".format("") + "{:<21}".format("mean") + "{:<20}".format("sharp") + "{:<20}".format("sterling")
print(top)
result = optimal_strat(IBM_returns,Bond_returns,Bond_returns,0.02)
g, = plt.plot( np.arange(0,n-1), result[4],label = "(IBM,BOND)")
print("IBM,BOND: ", "{:<20}".format(result[0]),"{:<20}".format(result[2]),"{:<20}".format(result[3]))
result = optimal_strat(Dell_returns,Bond_returns,Bond_returns,0.02)
g, = plt.plot( np.arange(0,n-1), result[4],label = "(DELL,BOND)")
print("DELL,BOND: ", "{:<20}".format(result[0]),"{:<20}".format(result[2]),"{:<20}".format(result[3]))
result = optimal_strat(IBM_returns,Dell_returns,Bond_returns,0.02)
g, = plt.plot( np.arange(0,n-1), result[4],label = "(DELL,IBM)")
print("IBM,DELL: ", "{:<20}".format(result[0]),"{:<20}".format(result[2]),"{:<20}".format(result[3]))



cul_bond = np.zeros(shape = (n))

cul_r = 0.0
for i in range(1,n):
    r = math.log(Bond[i][1]/Bond[i-1][1])
    cul_r += r
    cul_bond[i] = cul_r

#PLOT THE LINE
#g, = plt.plot( np.arange(0,n), cul_bond)

#g, = plt.plot( np.arange(0,n-1), result[4])
plt.legend()
plt.title("Culmative returns vs. time")
plt.ylabel('Culmative returns')
plt.xlabel('Time (5-min intervals)')
plt.savefig("HW3_1c.pdf")
plt.show()
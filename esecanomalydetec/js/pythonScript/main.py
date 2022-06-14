import re
from getip import GetIPAddress
mainPath = '/var/www/esecanomalydetec/js'

ip = GetIPAddress().getIt()[0]
print(ip)
config = mainPath+'/script_config.js'
testing = mainPath+'/script_testing.js'
training = mainPath+'/script_training.js'
status = mainPath+'/script_status.js'
result = mainPath+'/script_result.js'

all = [config,training,testing,status,result]

filecount = 0
for file in all:
    filecount += 1
    fHandle = open(file, "r")
    lines = fHandle.readlines()
    lineCount = 0
    fHandle.close()
    for line in lines:
        x = re.search('var HostIP',line)
        if(x is not None):
            lines[lineCount] = "var HostIP = '{}';\n".format(ip)
            f2 = open(file,'w')
            f2.writelines(lines)
            f2.close()    
            break
        lineCount+=1
print('finish')
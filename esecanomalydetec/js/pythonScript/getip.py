import netifaces as ni

class GetIPAddress:
    def __init__(self):
        return
    def mac_for_ip(self,ip,device):
        addrs = ni.ifaddresses(device)
        try:
            if_mac = addrs[ni.AF_LINK][0]['addr']
            if_ip = addrs[ni.AF_INET][0]['addr']
        except IndexError: #ignore ifaces that dont have MAC or IP
            if_mac = if_ip = None
        except KeyError: #ignore ifaces that dont have MAC or IP
            if_mac = if_ip = None
        if if_ip == ip:
            return if_mac.upper()
    def getIP_MAC(self,device= 'wlp0s20f3'):
        try:
            ip = ni.ifaddresses(device)[ni.AF_INET][0]['addr']
            return str(ip),self.mac_for_ip(str(ip),device)
        except:
            return '127.0.0.1',None

    def getIt(self):
        wifi = self.getIP_MAC('wlp0s20f3')
        eth = self.getIP_MAC('enp89s0')
        if(eth[0] == '127.0.0.1' or eth[0] == '0.0.0.0'):
            return wifi
        return eth


# if __name__ == '__main__':
#     a = GetIPAddress()
#     #print(a.getIP_MAC('wlp0s20f3'))
#     #print(a.getIP_MAC('enp89s0'))
#     print(a.getIt())
#     #ETH Port enp89s0
#     #WIFI Port wlp0s20f3
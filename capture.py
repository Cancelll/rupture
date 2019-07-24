import sys
from scapy.all import *

def main():
	capture_filter = ''
	t = int(sys.argv[1])
	url = sys.argv[2]
	iplist = open(r"./backend/current_iplist.txt", "r")
	while True:
		ip = iplist.readline()[:-2]
		if ip == '':
			break
		capture_filter = capture_filter + 'src host ' + ip
		capture_filter = capture_filter + ' or dst host ' + ip + ' or '
	capture_filter = capture_filter[:-3] + 'and tcp'
	pkts = sniff(
		iface='eth0',
		filter=capture_filter,
		timeout=t
		)
	if len(pkts) != 0:
		wrpcap(url+"_"+".pcap", pkts)

if __name__ == '__main__':
	main()
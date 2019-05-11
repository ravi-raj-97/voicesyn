import wave as w
import argparse
import traceback


def generator(ipfn,opfn,spf):
	iw=w.open(ipfn,'rb')
	ow=w.open(opfn,'wb')
	inc=iw.getnchannels()
	isw=iw.getsampwidth()
	ifr=iw.getframerate()
	inf=iw.getnframes()
	ofr=ifr*float(spf)
	ow.setnchannels(inc)
	ow.setsampwidth(isw)
	ow.setframerate(ofr)
	ow.writeframesraw(iw.readframes(inf))
	iw.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is a test')
	parser.add_argument('input_file', help='Name of audio file to use')
	parser.add_argument('output_file', help='Name of output file to write')
	parser.add_argument('speed_factor', help='The factor of increase or decrease in speed')
	args = parser.parse_args()
	ipf=args.input_file
	opf=args.output_file
	sf=args.speed_factor
	try:
		generator(ipf,opf,sf)
	except Exception as E:
		print(E, traceback.print_exc())
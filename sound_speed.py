import wave as w
import argparse
import traceback

def generator(ipfn,opfn):
	iw=w.open(ipfn,'rb')
	ow=w.open(opfn,'wb')
	inc=iw.getnchannels()
	isw=iw.getsampwidth()
	ifr=iw.getframerate()
	inf=iw.getnframes()
	ofr=ifr*0.6 #makes frame rate 60% of the original 
	ow.setnchannels(inc)
	ow.setsampwidth(isw)
	ow.setframerate(ofr)
	ow.writeframesraw(iw.readframes(inf))
	iw.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is a test')
	parser.add_argument('input_file', help='Name of audio file to use')
	parser.add_argument('output_file', help='Name of output file to write')
	args = parser.parse_args()
	ipf=args.input_file
	opf=args.output_file
	try:
		generator(ipf,opf)
	except Exception as E:
		print(E, traceback.print_exc())
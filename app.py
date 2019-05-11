from flask import Flask, render_template, redirect, request, url_for, flash, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os
import create_soundlist as cs
import play_words_2 as pw2
import re

UPLOAD_FOLDER = '/home/chraviraj/voicesyn/uploaded_recordings'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__,static_url_path = '/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'hello'

name_list=[]
pass_list=[]
cons_list=[]
speaker_num=0

track="/home/chraviraj/Desktop/Frontend/infinity_war.mp3"

with open('namelist.txt') as nf:
	for line in nf:
		row=line.strip().split(',')
		speaker_num+=1
		cons_list.append(row)
		temp=[speaker_num,row[1]]
		name_list.append(temp)
		temp=[speaker_num,row[2]]
		pass_list.append(temp)
nf.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/playSong')
def playSong():
    return track.play()

@app.route('/#home')
@app.route('/')
def home():
	return render_template('index.html',names=name_list)
@app.route('/#about')
def about():
	return render_template('index.html',names=name_list)
@app.route('/#train',methods=['GET','POST'])
def train():
	return render_template('index.html',names=name_list)
@app.route('/#generate')
def generate():
	return render_template('index.html',names=name_list)
@app.route('/#contact')
def contact():
	return render_template('index.html',names=name_list)

@app.route('/upload',methods=['POST'])
def upload():
	if request.method=='POST':
		filename=''
		speakername=request.form['speakername']
		speakerpass=request.form['speakerpass']
		x=request.files.getlist('files[]')
		uploadedfiles=[]
		print(x)
		for file in x:
			if file.filename == '':
				flash('No selected file')
				return redirect(request.url)
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
			print(filename,speakername,speakerpass)
			totalpath=UPLOAD_FOLDER+'/'+speakername
			flag=0
			count=0
			for row in name_list:
				count+=1
				if speakername == row[1]:
					flag=1
					serialnum=row[0]
					if pass_list[serialnum-1][1] != speakerpass:
						flash('Special Key Error')
						return redirect('/#train')
			if flag==0:
				count+=1
				name_list.append([count,speakername])
				pass_list.append([count,speakerpass])
				os.mkdir(totalpath)
				os.mkdir(totalpath+'/diphones')
				with open('namelist.txt','a') as nf:
					newline=str(count)+","+speakername+","+speakerpass+"\n"
					nf.write(newline)
				nf.close()
			file.save(os.path.join(totalpath, filename))
			filepath='uploaded_recordings/'+speakername+'/'+filename
			uploadedfiles.append(filepath)
			print(uploadedfiles)
			flash(filename+' uploaded and extracted succesfully.')
			fne,ext=filename.split('.')
			print(fne)
			textpath='uploaded_recordings/'+fne+'.txt'
			folderpath='uploaded_recordings/'+speakername+'/diphones'
			cs.generate_diphones(filepath,textpath,folderpath)
		#audio_file, transcript_file, output_folder, pre_padding=0.0, post_padding=0.0)
		return redirect('/#train')

@app.route('/synthesizer',methods=['POST'])
def syn():
	if request.method=='POST':
		speakername=request.form['speakername']
		textcontent=request.form['converttext']
		speakerpass=request.form['speakerpass']
		count=0
		for row in name_list:
			count+=1
			if speakername == row[1]:
				serialnum=row[0]
				if pass_list[serialnum-1][1] != speakerpass:
					flash('Special Key invalid. Please re-enter.')
					return redirect('/#generate')
		folderpath='uploaded_recordings/'+speakername+'/diphones'
		res=re.findall(r'\w+',textcontent)
		print(res)
		pw2.output(folderpath,res,'split.txt',0.01,0.02,'generated.wav')
		#source_folder, word_list, dict_file, diphone_silence=.01, word_silence=.2, name=None
		flash('The uploaded text is synthesized in the voice of '+speakername+'.')
		flash('Click Play or Download now.')
	return redirect('/#generate') 

@app.route('/generatedfile')
def down():
	return send_file('/home/chraviraj/voicesyn/generated.wav',attachment_filename="generated")

@app.route('/transcript.txt')
def openfile():
	text = open('transcript.txt', 'r+')
	content = text.read()
	text.close()
	return render_template('fileview.html', text=content)

if __name__ == '__main__':
	app.debug = True
	app.run(host='127.0.0.1', port=5000)
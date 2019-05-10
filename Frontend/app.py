from flask import Flask, render_template, redirect, request, url_for, flash, send_from_directory, send_file
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/home/chraviraj/Desktop/Frontend/uploaded_recordings'
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
		if 'file' not in request.files:
			flash('No file selected')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
	print(filename,speakername,speakerpass)
	tpath=UPLOAD_FOLDER+'/'+speakername
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
		os.mkdir(tpath)
		with open('namelist.txt','a') as nf:
			newline=str(count)+","+speakername+","+speakerpass+"\n"
			nf.write(newline)
		nf.close()
	file.save(os.path.join(tpath, filename))
	flash(filename+' uploaded succesfully')
	return redirect('/#generate')

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
		flash('The uploaded text is synthesized in the voice of '+speakername+'.')
		flash('Click Play or Download now.')
	return redirect('/#generate') 


@app.route('/download-file')
def down():
	return send_file('/home/chraviraj/Desktop/Frontend/uploaded_recordings/infinity_war.mp3',attachment_filename="infinity_war.mp3")

@app.route('/alphabet.txt')
def openfile():
	text = open('alphabet.txt', 'r+')
	content = text.read()
	text.close()
	return render_template('fileview.html', text=content)

if __name__ == '__main__':
	app.debug = True
	app.run(host='127.0.0.1', port=5000)
from flask import Flask, render_template, redirect, request, url_for
app = Flask(__name__,static_url_path = '/static')

name_list=[]
pass_list=[]
cons_list=[]
speaker_num=0

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
@app.route('/upload',methods=['GET','POST'])
def upload():
	if request.method=='POST':
		filepath=request.form['wavpath']
		speakername=request.form['speakername']
		speakerpass=request.form['speakerpass']
	print(filepath,speakername,speakerpass)
	flag=0
	count=0
	for row in name_list:
		count+=1
		if speakername == row[1]:
			flag=1
			serialnum=row[0]
			if pass_list[serialnum-1][1] != speakerpass:
				errmsg="Special Key Error"
				return redirect('/#train')
	if flag==0:
		count+=1
		name_list.append([count,speakername])
		pass_list.append([count,speakerpass])
		with open('namelist.txt','a') as nf:
			newline=str(count)+","+speakername+","+speakerpass+"\n"
			nf.write(newline)
		nf.close()
		print('what shit')
	print("reached successfully")
	return redirect('/#generate')

@app.route('/alphabet.txt')
def openfile():
	text = open('alphabet.txt', 'r+')
	content = text.read()
	text.close()
	return render_template('fileview.html', text=content)

if __name__ == '__main__':
	app.debug = True
	app.run(host='127.0.0.1', port=5000)
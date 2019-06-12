from flask import Flask, render_template, redirect, request, flash, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
import create_soundlist as cs
import play_words_2 as pw2
import re

UPLOAD_FOLDER = 'uploaded_recordings'
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'hello'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
name_list = set()
users = dict()


def num_to_str(str_with_num: str):
    str_without_num = str_with_num.replace('1', 'one ')\
                        .replace('2', 'two ')\
                        .replace('3', 'three ')\
                        .replace('4', 'four ')\
                        .replace('5', 'five ')\
                        .replace('6', 'six ')\
                        .replace('7', 'seven ')\
                        .replace('8', 'eight ')\
                        .replace('9', 'nine ')\
                        .replace('0', 'zero ')
    return str_without_num


def fill_namelist():
    with open('namelist.txt') as nf:
        global name_list
        name_list = []
        for line in nf:
            row = line.strip().split(',')
            name = row[0]
            passwd = row[1]
            users[name] = passwd
            name_list.append(name)


fill_namelist()


def allowed_file(filename):
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return True if re.match(r"wl\d\d?.wav", filename) else False


@app.route('/#home')
@app.route('/')
def home():
    return render_template('index.html', names=name_list)


@app.route('/#about')
def about():
    return render_template('index.html', names=name_list)


@app.route('/#train', methods=['GET', 'POST'])
def train():
    return render_template('index.html', names=name_list)


@app.route('/#generate')
def generate():
    return render_template('index.html', names=name_list)


@app.route('/#contact')
def contact():
    return render_template('index.html', names=name_list)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        filename = ''
        speakername = request.form['speakername']
        speakerpass = request.form['speakerpass']
        x = request.files.getlist('files[]')
        uploadedfiles = []
        print(x)
        for file in x:
            if file.filename == '':
                flash('No selected file')
                return redirect('/#train')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
            else:
                flash('Error in filename/format')
                return redirect('/#train')
            print(filename, speakername, speakerpass)
            totalpath = UPLOAD_FOLDER + '/' + speakername

            if users.get(speakername, None):
                if users[speakername] != speakerpass:
                    flash('Special Key Error')
                    return redirect('/#train')
                else:
                    if not os.path.exists(totalpath):
                        os.mkdir(totalpath)
                        os.mkdir(totalpath + '/diphones')
                    print('\n\n\n\n\n\nadding extra files')
            else:

                if not os.path.exists(totalpath):
                    os.mkdir(totalpath)
                    os.mkdir(totalpath + '/diphones')
                    with open('namelist.txt', 'a') as nf:
                        newline = speakername + "," + speakerpass + "\n"
                        nf.write(newline)
            fill_namelist()
            file.save(os.path.join(totalpath, filename))
            filepath = 'uploaded_recordings/' + speakername + '/' + filename
            uploadedfiles.append(filepath)
            print(uploadedfiles)
            flash(filename + ' uploaded and extracted succesfully.')
            fne, ext = filename.split('.')
            print(fne)
            textpath = 'uploaded_recordings/' + fne + '.txt'
            folderpath = 'uploaded_recordings/' + speakername + '/diphones'
            try:
                cs.generate_diphones(filepath, textpath, folderpath, 0.01, 0.05)
            except Exception as e:
                flash('Error occured for file', file.filename)
                flash('Please retry')
                return redirect('/#train')
        # audio_file, transcript_file, output_folder, pre_padding=0.0, post_padding=0.0)
        return redirect('/#train')


@app.route('/synthesizer', methods=['POST'])
def syn():
    if request.method == 'POST':
        speakername = request.form['speakername']
        textcontent = request.form['converttext']
        speakerpass = request.form['speakerpass']
        if textcontent == '':
            flash('No text')
            return redirect('/#generate')
        if users.get(speakername, None) is None or users[speakername] != speakerpass:
            flash('Key error')
            return redirect('/#generate')

        diphone_path = UPLOAD_FOLDER + '/' + speakername + '/diphones'
        output_path = UPLOAD_FOLDER + '/' + speakername + '/generated'
        textcontent = num_to_str(textcontent)
        res = re.findall(r'\w+', textcontent)
        print('words are ', res)
        op = pw2.output(diphone_path, res, 'split.txt', 0.2, output_path)
        if len(op) < 1:
            flash('Word not found')
            return redirect('/#generate')
        # source_folder, word_list, dict_file, diphone_silence=.01, word_silence=.2, name=None
        # flash('The uploaded text is synthesized in the voice of ' + speakername + '.')
        # flash('Click Play or Download now.')
        return redirect('/generatedfile/'+speakername, 303)


@app.route('/generatedfile/<speakername>')
def down(speakername):
    directory = UPLOAD_FOLDER + '/' + speakername
    r = make_response(send_from_directory(directory=directory, filename='generated.wav',
                                          attachment_filename='aud.wav', as_attachment=True, cache_timeout=0))
    r.headers["x-filename"] = 'generated.wav'
    r.headers["Access-Control-Expose-Headers"] = 'x-filename'
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/transcript.txt')
def openfile():
    text = open('transcript.txt', 'r+')
    content = text.read()
    text.close()
    return render_template('fileview.html', text=content)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

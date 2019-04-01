# voicesyn
Made the repo. Please clone. Will be adding you guys as contributors soon.

## Cloning our repo

1) Navigate to the directory where you want to install the repo. Don't create new folder for it.

2) Open terminal and navigate to that folder and type:

	```
	git clone https://github.com/ravi-raj-97/voicesyn.git
	```


## Updating your repo before starting work
1) Open the directory of the repo in the terminal.
2) Type the command
 
	```
	git pull
	```


## Pushing your work
1) Open the directory of the repo in the terminal.

2) Stage the files using git add .
	```
	git add .
	```
3) Use

	```
	git commit -m "Whatever message you want to pass for others to know."
	```

4) Type
	```
	git push
	```

    Enter your username and password in the prompt 

## Setting up the environment
1) Install the [gentle](https://github.com/lowerquality/gentle) library by cloning the gentle repo anywhere in the system and running the ./install.sh file. Follow the instructions in the "issues" tab of the project when there are errors.

2) Use the command
	```
	pip install -r pip_req.txt
	```
    Inside your virtual environment to install the required python libaries. 

3) Then create a file called gentle.pth in  'venv/lib/python3.6/site-packages/'
   and type the full path to your gentle installation there. (venv is the virtual environment)

## Basic usage
Some things to be kept in mind
* Single folder per user
* The folder should contain the .txt and .wav files
* The names of the .txt and .wav files has to be the same
* In gen_diphone set the filename of the wav and txt file and the output directory. TODO: Make this commandline param
* In play_words set the diphones_folder to the output_directory of gen_diphone. TODO: Make this command line param

Usage
```
python gen_diphones.py 
```

```
python play_words.py
```
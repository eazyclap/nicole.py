from flask import Flask, render_template
from threading import Thread

# TODO Review the website, maybe add some functions or stats, at this point there is no point in keeping it static

app = Flask('', template_folder="web-files", static_folder="web-files/static")

@app.route('/')
def home():
  return render_template("home.html")
    
def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()

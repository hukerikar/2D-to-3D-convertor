from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hr_interview')
def hr_interview():
    return render_template('hr_interview.html')

@app.route('/technical_interview')
def technical_interview():
    return render_template('technical_interview.html')

if __name__ == '__main__':
    app.run(debug=True)

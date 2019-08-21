'''
Webserver for the Penguin Guano Classification AI4Earth API

To run:
export FLASK_APP=frontend-server.py
python -m flask run --host=0.0.0.0

To access the website, enter your IP address:5000 into a browser.
e.g., http://127.0.0.1:5000/
'''


from flask import Flask, send_from_directory

print("Running frontend server")

app = Flask(__name__, static_url_path='')

# front-end server stuff
@app.route('/')
def root():
	return send_from_directory('', 'index.html')

@app.route('/about.html')
def send_about():
	return send_from_directory('', 'about.html')

@app.route('/static/static-templates/<path:path>')
def send_templates(path):
    return send_from_directory('static/static-templates', path)

@app.route('/static/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)
	
@app.route('/static/images/<path:path>')
def send_image(path):
    return send_from_directory('static/images', path)	

if __name__ == '__main__':
    app.run()

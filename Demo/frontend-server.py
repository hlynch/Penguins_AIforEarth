'''
Webserver for the Penguin Guano Classification AI4Earth API

To run:
export FLASK_APP=frontend-server.py
python -m flask run --host=0.0.0.0

To access the website, enter your IP address:5000 into a browser.
e.g., http://127.0.0.1:5000/
'''


from flask import Flask, send_from_directory, request
import requests

print("Running frontend server")

API_ENDPOINT = "http://40.81.15.231:80/v1/pytorch_api/classify"

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


@app.route('/get-classification', methods=['GET', 'POST'])
def get_classification():
	if request.form['type'] == 'sample':
		# TODO: enforce strict pathing to static image dir only
		data = open('.' + request.form['file'], 'rb').read()
	else:
		data = request.files.get('file', '')
	r = requests.post(url = API_ENDPOINT, data = data, 
			headers={'Content-Type': 'application/octet-stream'})
	return 'https://icebergblob.blob.core.windows.net/penguinapi/' + r.text


if __name__ == '__main__':
    app.run()

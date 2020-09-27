from flask import Flask, request, abort, jsonify
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from PIL import Image
from unet_model import UnetModel
from azure.storage.blob import BlockBlobService, PublicAccess
from io import BytesIO
from os import getenv
import numpy as np
import uuid
import sys

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream', 'image/jpeg']
blob_access_duration_hrs = 1
app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a
# logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles
# concurrent requests.
with app.app_context():
	ai4e_service = APIService(app, log)

# Load the model
# The model was copied to this location
# when the container was built; see ../Dockerfile
model_path = '/app/pytorch_api/300_net_G.pth'
model = UnetModel()
model.initialize(model_path)


def process_request_data(request):
	return_values = {'image_bytes': None}
	try:
		# Attempt to load the body
		return_values['image_bytes'] = BytesIO(request.data)
	except:
		log.log_error('Unable to load the request data')
	return return_values


# POST, async API endpoint example
@ai4e_service.api_sync_func(
	api_path = '/classify', 
	methods = ['POST'], 
	request_processing_function = process_request_data,
	maximum_concurrent_requests = 50,
	content_types = ACCEPTED_CONTENT_TYPES,
	content_max_length = 10000000, # In bytes
	trace_name = 'post:classify')


def post(*args, **kwargs):
	try:
		# classifying image
		image_bytes = kwargs.get('image_bytes')
		out_im = model.png_predict(image_bytes) 

		local_file_name = str(uuid.uuid4()).replace('-','') + '.png'
		full_path_to_file = './' + local_file_name
		out_im[out_im>255] = 255
		Image.fromarray(out_im.astype(np.uint8)).save(full_path_to_file)

		# Create the BlockBlockService that is used to call the Blob service for the storage account
		block_blob_service = BlockBlobService(account_name='icebergblob',
				account_key='b+sB+qbZvfqR81KThZwor2DjZmkEEo0X1/rpbxUdeIoJUoeIwUSelTnAoULyVtnxdxc8hc2MLMusA0PTFeusuA==')
		# Create a container called 'penguinapi'.
		container_name ='penguinapi'
		block_blob_service.create_container(container_name)

		# Set the permission so the blobs are public.
		block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

		# Upload the created file, use local_file_name for the blob name
		block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)
		
		# get the URL of the classified image in our blob
		url = block_blob_service.make_blob_url(container_name, local_file_name)

		return_dict = {'image_url' : url}
		return jsonify(return_dict)
	except Exception as err:
		log.log_exception(sys.exc_info()[0])
		abort(400, '{0}: {1}'.format(type(err).__name__, err))

if __name__ == '__main__':
	app.run()

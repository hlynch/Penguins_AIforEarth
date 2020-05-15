# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request, abort
from flask_restful import Resource, Api

from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from sas_blob import SasBlob
from PIL import Image
from unet_model import UnetModel
from azure.storage.blob import BlockBlobService, PublicAccess
import pytorch_classifier
from io import BytesIO
from os import getenv
import requests

# defining the api-endpoint  
API_ENDPOINT = "https://52.180.95.115:80/v1/pytorch_api/classify"

import uuid
import sys

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream', 'image/jpeg']
blob_access_duration_hrs = 1
app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
#model_path = '/app/pytorch_api/iNat_2018_InceptionV3.pth.tar'
model_path = '/app/pytorch_api/300_net_G.pth'
#model = pytorch_classifier.load_model(model_path)
model = UnetModel()
model.initialize(model_path)
# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    print('Processing data...')
    return_values = {'image_bytes': None}
    try:
        # Attempt to load the body
        return_values['image_bytes'] = BytesIO(request.data)
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path = '/classify', 
    methods = ['POST'], 
    request_processing_function = process_request_data, # This is the data process function that you created above.
    maximum_concurrent_requests = 5, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ACCEPTED_CONTENT_TYPES,
    content_max_length = 1000000, # In bytes
    trace_name = 'post:classify')



def post(*args, **kwargs):
    print('Post called')
    image_bytes = kwargs.get('image_bytes')
    ai4e_service.api_task_manager.UpdateTaskStatus(taskId, 'running - segmentating the image')
    try:
        out_im = model.png_predict(image_bytes) 

        local_file_name = str(uuid.uuid4()).replace('-','') + '.png'
        full_path_to_file = './' + local_file_name
        print(full_path_to_file)

        Image.fromarray(out_im).convert('L').save(full_path_to_file, format='png',mode='L')
        
        print(out_im.shape)

        try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
            block_blob_service = BlockBlobService(account_name='icebergblob', account_key='b+sB+qbZvfqR81KThZwor2DjZmkEEo0X1/rpbxUdeIoJUoeIwUSelTnAoULyVtnxdxc8hc2MLMusA0PTFeusuA==')
            # Create a container called 'penguinapi'.
            container_name ='penguinapi'
            block_blob_service.create_container(container_name)

            # Set the permission so the blobs are public.
            block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
            # Upload the created file, use local_file_name for the blob name
            block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)

            ai4e_service.api_task_manager.CompleteTask(taskId, 'completed')        
        except 
            raise IOError('Cannot save file to blob')

        return local_file_name
    except:
        log.log_exception(sys.exc_info()[0], taskId)
        ai4e_service.api_task_manager.FailTask(taskId, 'failed: ' + str(sys.exc_info()[0]))

if __name__ == '__main__':
    app.run()

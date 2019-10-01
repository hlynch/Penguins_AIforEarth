FROM mcr.microsoft.com/aiforearth/base-py:latest

# Copy the AI4E tools and libraries to our container.
COPY --from=mcr.microsoft.com/aiforearth/base-py:latest /ai4e_api_tools /ai4e_api_tools

# Add the AI4E API source directory to the PATH.
ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH
# Add the AI4E tools directory to the PYTHONPATH.
ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"
# Install Miniconda, Flask, Supervisor, uwsgi
#RUN ./ai4e_api_tools/requirements/install-api-hosting-reqs.sh 
COPY ./req /req
RUN ./req/install-api-hosting-reqs.sh
# Install Azure Blob SDK
RUN ./ai4e_api_tools/requirements/install-azure-blob.sh 
# Install Application Insights
RUN ./ai4e_api_tools/requirements/install-appinsights.sh
# Install Opencensus
RUN ./ai4e_api_tools/requirements/install-opencensus.sh
EXPOSE 55678 50001



RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas scipy \
    && conda install -y -c pytorch -n ai4e_py_api pytorch torchvision \
    #&& conda install -y -c kmdouglass -n ai4e_py_api tifffile
    && conda install -y -c conda-forge -n ai4e_py_api tifffile

RUN conda install -y -c conda-forge -n ai4e_py_api protobuf=3.7.1
# PIL will be installed with pytorch

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy your API code
COPY ./pytorch_api /app/pytorch_api/
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

COPY ./LocalForwarder.config /lf/

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY= \
    LOCALAPPDATA=/app_insights_data \
    OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_PyTorch_Example \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=AI4E_PyTorch_Example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/pytorch_api

ENV STORAGE_ACCOUNT_NAME = icebergblob \
    STORAGE_ACOUNT_KEY = b+sB+qbZvfqR81KThZwor2DjZmkEEo0X1/rpbxUdeIoJUoeIwUSelTnAoULyVtnxdxc8hc2MLMusA0PTFeusuA==

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=60s --start-period=20s \
  CMD curl -f http://localhost/${API_PREFIX}/  || exit 1
ENTRYPOINT [ "/startup.sh" ]

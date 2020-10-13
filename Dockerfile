# set base image (host OS)
FROM python:3.6

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

# define ENV
ENV bucket='stb-ml-cross-sale'
ENV input='inputs/sample_input.csv'
ENV model='./models/model_01.h5'
ENV output='outputs/sample_output.csv'

# command to run on container start
ENTRYPOINT python crosssale.py $bucket $input $model $output
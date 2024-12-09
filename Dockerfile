# syntax=docker/dockerfile:1

# use an official Python image as the base
FROM python:3.12.5-bookworm

# set the working directory
WORKDIR /ds_project

# copy requirements file into working directory
COPY requirements.txt requirements.txt

# install dependencies using pip
RUN pip install -r requirements.txt

# expose port for jupyter lab
EXPOSE 8050

# run the dashboard when we launch the container 
# CMD ["python3", "create_tables.py"]
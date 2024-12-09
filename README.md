# climate-ville

This is the repository for the semester long data engineering project for UVA's DS 6600. In this project, we attempt to link US Census Data to climate data scraped from the NOAA (National Oceanic and Atmospheric Administration) NCEI (National Centers of Environment Instite)

## How to run this code

This code is hosted locally, it is not a persistent web application. Therefore, there are a few things that you must do before you get this code working. 

1. Run the following code in your terminal:

```
python3 -m venv DSENV
source DSENV/bin/activate
pip install -r requirements.txt
```

This will download all the required packages needed for this project.

2. Launch Docker

3. Run the Docker compose command:

```
docker compose up
```

This will pull the image that was created for this project and allow you to interact with the database.

4. Interact with the database.


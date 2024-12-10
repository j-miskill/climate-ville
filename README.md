# climate-ville

This is the repository for the semester long data engineering project for UVA's DS 6600. In this project, we attempt to link US Census Data to climate data scraped from the NOAA (National Oceanic and Atmospheric Administration) NCEI (National Centers of Environment Instite)

## How to run this code

This code is hosted locally, it is not a persistent web application. Therefore, there are a few things that you must do before you get this code working.

1. `cd` to the `climate-ville` directory and run the following code in your terminal:

```
python3 -m venv DSENV
source DSENV/bin/activate
pip install -r requirements.txt
```

This will download all the required packages needed for this project.

\*\*also, set up a `.env` file with all variables you need.

I will send you the `.env` file that you need. Make sure the file is in the `climate-ville` directory.

2. Launch Docker on the side

3. Run the Docker compose command:

```
docker compose up
```

This will pull the image that was created for this project and allow you to interact with the database. The first time that you launch docker, it will likely take a few seconds for the dashboard to load up. The reason is that it is loading in the tables if it is your first time opening the dashboard.

4. Open a new terminal and run the app.

```
python3 app.py
```

I do this separately than the `docker compose` command because of the need to load in data for another user to use.

5. Give the dashboard a few seconds to load things up on the first try- it is reading in some data and may take a second.

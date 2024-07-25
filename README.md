# Flask File Management Application

## Overview

This application allows users to upload, view, download, and delete files through a web interface. It uses Flask for the web framework and SQLite for the database.

This project is done twice. The first time to do everything on the sheet including deleting files. The second time to give the user the ability to submit multiple files at once (and show off sql targeting abilities).

## Setup Instructions

### Step 1: Create a Virtual Environment

Run this command:
 `python3 -m venv venv`

 if you know there shouldn't be 3, remove it.

### Step 2: Start the venv and install the dependencies 

Run:
 - On Mac/Linux: `source venv/bin/activate`; or
 - On Windows: `venv\Scripts\activate`

Then run:
`pip install -r requirements.txt`

### Step 3a: Run one of the apps

I suggest `app_single_file.py`

### Step 4a: Run the other app

Now do `app_submissions.py`

### Step 3&4b: Visit the Site and play around

Add or remove files with ease at `localhost:5000` via any means on this device (preferably a browser for humans).

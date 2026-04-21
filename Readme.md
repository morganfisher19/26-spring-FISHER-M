# George Washington University Data Science Program
## UG Capstone Course GitHub Repo template

To run this project locally, you need to run the file run.bat. The first file that runs is the pipeline which extracts, transforms, and loads new data into the database. Essentially updating the existing database with new data. Next the pipeling runs the backend which is the app.py file. Lastly, the pipeline runs the react frontend.



Here is the outline of all the folders and important files:

I. Code
    Here includes all the code used in the project.

    A. Pipeline
        Runs a series of scripts to extract, transform, and load the data. Extract scripts load the data from APIs and web scraping techniques landing the files in the silver data folder. Transform scripts clean the silver data and land the cleaned files in the gold data folder. Load scripts take the cleaned data and update the database with the new data.

    B. Backend
        Contains app.py file which includes all python flask backend code to connect to the database and run the 

    C. Frontend
        Contains various React component .tsx files, CSS styling file, and D3.js visualizations embedded in .tsx files.

    D. EDA
        Contains exploratory jupyter notebooks to explore data and gather image files for frontend.

    E. Old
        Here includes code that was previously written but no longer used. Saved in case I need to referencing back to it.

II. Data
    Here includes all the data used for the project.

III. Planning
    Here includes .txt files used to plan out the project.

IV. Presentation
    Here includes the presentation used for the product demonstration.

V. Proposal
    Here includes the initial proposal document for the project.

VI. Report
    The final report will be added here.



Future steps:

As of now, the web app is not hosted on the internet. However, it is a major goal of the project to get a hosted web application accessible my a url.



Running the project initially on a different device:

Without an established postgreSQL database, the complete project will not run. The web application pulls from the database, so you would need to set up your own postgreSQL database locally.

Runing the pipeline initially, it pipeline will take a long time to run (possibly an hour or more) and might time out. If this happens, you can continue to run it, there are protections against this. After the pipeline is complete you should have all your data within the gold layer json files. However, the "load" part of the pipeline is dependent on having a database.

The next step would be to create your own postgreSQL database locally on your device. The SQL files in "old" would allow you to duplicate the database using an SQL Shell terminal. Also, the connection configurations would need to be updated.

After the database is established and connected to, running the run.bat file should run the pipeline again updating the data, run the backend, then run the frontend allowing you to have the app running locally on your device.

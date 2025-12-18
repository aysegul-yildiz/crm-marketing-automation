Running the Project:
    create a virtual environment:
        python3 -m venv venv
        source venv/bin/activate (mac)
        venv\Scripts\activate (Windows)

    install dependencies:
        pip install -r requirements.txt

    initialize the database:
        python app/database.py

    start the server:
        python run.py

    visit the application in the browser at http://127.0.0.1:5000

Running workflow executor script:
To run and execute pending workflow steps invoke the relevant python script, outside its containing folder (for include paths to resolve):
```
~/crm-marketing-automation$ python ./scripts/execute_workflows.py
```

Running Tests:
    tests are inside the app/tests folder, to run:
        pytest app/tests -q


CRM marketing automation system:
This project is a simplified CRM marketing automation platform built for CS411 course. It includes campaign management, segmentation, workflow automation and an analytics module. It uses Flask for the backend and CSV files to simulate a data warehouse. In a real system these CSV files would be replaced with a proper data warehouse but the logic and architecture would stay similar.

Project Structure:
    app/auth handles- login and access control.
    app/campaign- includes pages for creating campaigns and managing workflows
    app/marketing- contains the dashboard, analytics page and campaign listing page
    app/models-defines the data structures 
    app/repositories- loads and reads data from CSV files
    app/services- contains business logic such as analytics calculations, segmentation and campaign execution
    app/templates- HTML templates for the user interface
    app/data- contains all CSV files, simulation of a company’s data warehouse
    app/tests- automated tests for the marketing module
    config.py
    database.py
    run.py
    requirements.txt
    README.md

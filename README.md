    
    This project is built to showcase my skills as an aspiring data engineer and Python developer.'
    
    Highlights of this repo:
    
    - focus on delivering insights; we take care of the back-end so you can get what you need up front
    
    - abstraction of system design and practical code modularity
    
    - end-to-end data workflow, from source to delivery; similar to real-world cloud applications

    ...as well as being a great learning experience for me!

    Back-end with SQLAlchemy and Python:
        - database setup (SQLAlchemy ORM table models)
        - Automation/CRON jobs produce highly-available insight tables in the data warehouse
            - Customer Analytics Summary table
            - Customer Product Recommendations table

    API layer implemented with FastAPI:
        - main API script
        - pydantic 'schemas' to define API transactions
        - crud functions with endpoints
    
    Front-end with Streamlit:
        - streamlit 'server' accesses the running API 'server'
        - database can be wherever; as long as the API is open, the front-end can pull the data without incident.

### FILES IN THIS PACKAGE ###

# Database Setup and Functionality
`models.py` holds SQLAlchemy ORM models/database table schemas
`database.py` holds the engine and SessionLocal variables which instantiate and power our SQLALchemy Database
`my_url.py` is a secrets file

# API Functionality
`schemas.py` for the API transaction definitions; FastAPI/pydantic data models/schemas
`main.py` holds the FastAPI application with API endpoints
`crud.py` holds endpoint functions

# Streamlit Front-End
...WIP

![DunnHumby-2023-10-27-1224](https://github.com/np1919/DunnHumby/assets/78058496/489aff67-8389-4f51-8d34-b9168b69750d)
  

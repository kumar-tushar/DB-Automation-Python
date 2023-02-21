from psycopg2 import connect, extensions
import os, requests

connection = None
cursor = None
try:
    # connect to default database
    connection = connect(
        host='localhost',
        database='postgres',
        user='postgres',
        password='1793248650',
        port='5432',
    )

    cursor = connection.cursor()


    # auto commit the SQL queries
    auto_commit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
    connection.set_isolation_level(auto_commit)


    # new_database
    database_name = input('Enter Database name: ')


    # check if the new_database already exist
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
    result = cursor.fetchone()


    # terminate all the sessions of new_database if exist & drop new_database
    if result:
        print("----------------------------------------")
        drop_db = input(f"Database '{database_name}' already exists. Do you want to drop it? (Y/N): ")
        
        if drop_db.lower() == "y":
            cursor.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database_name}'")
            cursor.execute(f"DROP DATABASE {database_name}")
            print("----------------------------------------")
            print(f"Database '{database_name}' has been dropped.")
        else:
            print("----------------------------------------")
            print(f"Stopping further processes as database '{database_name}' already exists.")
            print("----------------------------------------")
            exit()


    # create new_database
    cursor.execute(f"CREATE DATABASE {database_name}")
    print("----------------------------------------")
    print(f"New Database '{database_name}' has been created.")
    print("----------------------------------------")


    # update db_name in root_config.py
    def update_db_config(new_db_name):
        with open("root_config.py", "r") as file:
            contents = file.readlines()
        for i, line in enumerate(contents):
            if "db_config = {" in line:
                break
        contents[i+1] = f'    "db_name": "{new_db_name}",\n'
        with open("root_config.py", "w") as file:
            file.writelines(contents)
    update_db_config(database_name)
    print(f"root_config.py updated with db_name as '{database_name}'.")
    print("----------------------------------------")


    # Run migrations
    print("RUNNING MIGRATIONS...")
    os.system("python manage.py migrate")
    print("----------------------------------------")
    
    
    # backend port number
    port = input("Enter your backend localhost port number: ")


    #superuser login
    superuser_login_data = {
        "email": "superuser_email",
        "password": "superuser_password"
        }
    
    superuser_login_response = requests.post(f'http://localhost:{port}/rest-auth/login/', json=superuser_login_data)


    #cookie & csrf token
    csrf_token = superuser_login_response.cookies['csrftoken']
    headers = {
        'Cookie': f'csrftoken={csrf_token}',
        'X-CSRFToken': csrf_token
        }


    # register a new user
    registration_url = f'http://localhost:{port}/rest-auth/registration/'

    registration_data = {
        "firstname": "first_name",
        "lastname": "last_name",
        "username": "test@test.com",
        "password1": "test@test",
        "password2": "test@test",
        "email": "test@test.com",
        "contact": "1234567890",
        "level": "L1"
        }

    registration_response = requests.post(registration_url, json=registration_data, headers=headers)

    if registration_response.status_code == 201:
        print("----------------------------------------")
        print("User registered successfully.")
        
        # creata a new user
        user_creation_url = f'http://localhost:{port}/create-new-user/'
        
        user_creation_data = {
            "CreatedBy": "superuser_email",
            "OrgName": "org_name",
            "contact": "1234567890",
            "email": "test@test.com",
            "firstname": "first_name",
            "hasWriteAcess": True,
            "lastname": "last_name",
            "level": "L1",
            "password1": "test@test",
            "password2": "test@test",
            "status": False,
            "username": "test@test.com",
            }
        
        user_creation_response = requests.post(user_creation_url, json=user_creation_data, headers=headers)
        
        if user_creation_response.status_code == 200:
            print("----------------------------------------")
            print("User created successfully.")
            print("----------------------------------------")
            print("Your login credentials are: email: test@test.com & password: test@test")
            print("----------------------------------------")
        else:
            print(f"User creation failed with status code {user_creation_response.status_code}.")
            
    else:
        print(f"User registration failed with status code {registration_response.status_code}.")


except Exception as e:
    print(e)

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

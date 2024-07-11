# Journaling App

Personal Journaling App.

## Description

A mobile application and a backend service for personal journaling. Users should be able to write journal entries, categorize them, and view a summary of their entries.

## Getting Started

## Backend Api

### Dependencies

* Python version used Python 3.10.12 but should not be a problem with most python distributions.
* Framework used FastApi (a python based framework) version details (FastAPI CLI version: 0.0.4) <a href='https://fastapi.tiangolo.com/#installation'>Fastapi source page here</a>
* Docker <a href="https://docs.docker.com/engine/install/">find docker source here</a>

### Installing

* Clone this reposiroty into your local machine ( repo link https://github.com/kinyodan/shamiri-case-study.git )
* CD into the cloned repository folder and then CD into the "/backend" folder
* Run below commands 

### Building the docker mage 

* While having docker installed in your machine (link shared above under dependecies)
* Step 1: To build the docker image Run
```
docker-compose build
```
* Step 2: Start the Docker Containers:
```
docker-compose up -d
```
* Step 3: Running Migrations:
   Create the migrations:
   ```
   docker-compose exec web alembic revision --autogenerate -m "init"
   ```
   Apply the Migration:
   ```
   docker-compose exec web alembic upgrade head
   ```
* If all is well the backend should be up and running on localhost <strong>( http://0.0.0.0:8000/ ) </strong>
   you can test it using api testng tools like <a href="https://www.postman.com/"> postman <a/> or any others to confirm all is well.


### Tests
Running the command at step 2 above will also run the tests at app initialization.
But to run test yourself, then after the steps outlined in the installation section above have been completed succesfully ,run below
command on terminal while in the root folder of the application.
```
docker-compose run test 
```
The test tool used is Pytest 

## Mobile app

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)

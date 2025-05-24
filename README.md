# Virtualization
## To run this project u need:
- Vagrant
- Docker (with compose plugin)
- VS Code (optionatl)
### 1. Clone repo
### 2. Export env variable named 'TOKEN' with your github token
### 3. Export env variable named 'sftp_pass' with your password
### 4. In /app create .env file with you credentials like in .env_example
### 5. In provision.sh change github repo url to yours
### 6. Run in /app folder:
    docker compose up --build -d in /app folder
### 7. Run in project folder:
    vagrant up --provision
### 8. Open in browser:
    localhost:5000/

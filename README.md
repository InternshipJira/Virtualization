# Virtualization
To run this project u need:
- Vagrant
- Docker (with compose plugin)
- VS Code (optionatl)
### 1. Clone repo
### 2. Export env variable TOKEN with your github token
### 3. In /app create .env file with you credentials like in .env_example
### 4. Run in /app folder:
    docker compose up --build -d in /app folder
### 5. Run in project folder:
    vagrant up --provision
### 6. Open in browser:
    localhost:5000/

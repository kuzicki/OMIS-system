# Buying and trading of digital goods platform

A system for trading and buying different types of digital goods by with many users. This application provides an interface to make trades, buy and find digital goods and more.

## Features

- User registration and authentication
- Find system
- Public your own digital goods
- Track goods
- Administrating features
- User edit capabilities

## Prerequisites

## Getting Started

Follow these steps to get the project running:

### 1. Clone the Repository

```bash
git clone https://github.com/kuzicki/OMIS-system.git
cd OMIS-system
```

### 2. Craate venv

Create a python virual environment in the project root

Type for installing necessary packages:
```
pip install -r requirements.txt
```

### 3. Create PostgreServer
Before running the app you have to create tables for the Postgre server.
Feel free to dockerize it or even create it locally on the host machine.
The script for creating the table is in the sql folder.

### 4. Change the database URI
After creating the postgre server you have to change the database URI in the config.py folder.

### 5. Start the app

Use Docker Compose to build and start the application:

```python
python main.py
```

### 6. Access the Application

Once the app is running, you can access the application at:

http://localhost:5000/

### 7. Stop the Application

Input the Keyboard Interrupt command(Ctrl + C)

---

Feel free to contribute and raise issues for any improvements or bugs!

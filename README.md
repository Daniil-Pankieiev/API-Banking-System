# Simple Banking System API

## Description

The Simple Banking System API is a RESTful API built with Flask that allows users to create accounts, log in, deposit money, withdraw money, and transfer funds between accounts. It includes features such as JWT-based authentication, rate limiting, and Swagger documentation.

## How It Works

### Endpoints

- **POST /create_account**: Create a new account.
- **POST /login**: Log in and get a JWT token.
- **POST /deposit**: Deposit money into an account (requires JWT token).
- **POST /withdraw**: Withdraw money from an account (requires JWT token).
- **POST /transfer**: Transfer money between accounts (requires JWT token).

### Authentication

- JWT (JSON Web Tokens) are used for authentication. Users receive a JWT token upon successful login, which must be included in the `Authorization` header of subsequent requests as a Bearer token.

### Rate Limiting

- Rate limiting is implemented to prevent abuse of the API. The default limits are 200 requests per day and 50 requests per hour.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Daniil-Pankieiev/API-Banking-System.git
```

2. Create a virtual environment:
```bash
python -m venv venv
```
3. Activate the virtual environment:

On macOS and Linux:
```bash
source venv/bin/activate
```
On Windows:
```bash
venv\Scripts\activate
```
4. Install project dependencies:
```bash
pip install -r requirements.txt
```
5. Copy .env_sample to .env and populate it with all required data:

JWT_SECRET_KEY=your_secret_key_here

6. Run the application:
```bash
python main.py
```
The API will be available at http://127.0.0.1:5000/swagger/.
Testing with Swagger

    Open your web browser and navigate to http://127.0.0.1:5000/swagger.

    You will see the Swagger UI, which allows you to interact with the API endpoints directly from the browser.

    Use the Swagger UI to create an account, log in, and perform deposit, withdraw, and transfer operations.

Contributing

Contributions are welcome! Please read the contributing guidelines to get started.

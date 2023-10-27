# enerBit Test

enerBit faces the challenge of efficiently recording and tracking service orders for a particular property or customer.

## Structure of the project

```linux
/app
 |-- main.py
 |-- database.py
 |-- config.py
 |-- models/
    |-- __init__.py
    |-- customer.py
    |-- work_order.py
 |-- repositories/
    |-- __init__.py
    |-- analytics_repository.py
    |-- customer_repository.py
    |-- work_order_repository.py
 |-- routers/
    |-- __init__.py
    |-- analytics_routers.py
    |-- customer_router.py
    |-- work_order_router.py
 |-- schemas/
       |-- __init__.py
       |-- schema.py
 |-- tasks/
   |-- __init__.py
   |-- redis.py
 |--tests/
    |-- __init__.py
 |-- requirements.txt
 |-- .gitignore
 |-- .env.example

```

## Getting started

To run this API on your local machine, follow these steps:

1. Clone the repository:

```bash
git clone git@github.com:JoseJulianMosqueraFuli/enerbit-test.git
```

2. Navigate into the cloned directory:

```bash
cd enerbit-test
```

3. Create a virtual environment:

```bash
python3 -m venv venv
```

4. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Create a `.env` file like `.env.example` :

```python
DATABASE_URL = <Here your DATABASE_URL>
REDIS_PORT = <Here your redis Port>
REDIS_HOST = <Here your redis Host>
```

7. Start the development server:

```bash
uvicorn main:app --reload
```

or

```bash
python main.py
```

## Improvements

- Create Tests and Analitycs
- Consider create access control for db (login)
- Template for visual analytics
- Consider Containers the app
- Always could be improved

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Build it by [Jose Julian Mosquera Fuli](https://github.com/JoseJulianMosqueraFuli).

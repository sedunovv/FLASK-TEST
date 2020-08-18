# FLASK-TEST

To run the project do the following
-
**1. build images**

docker-compose build

**2. launching containers**

docker-compose up db flask

**3. To apply migrations**

- docker-compose exec flask bash
- flask upgrade

**4. Added currencies**

POST api/update_currency

#
To run the container with tests
-

docker-compose run test

#
Main API methods
-

**1. Create user**

- Сurrencies must be created in the database prior to user creation
- POST api/users - data username (string), email (string), password (string), currency (string)

**2. To get info about user**

- POST api/tokens - with data email (string), password (string) to logged in user
- GET api/users/<int:id> - with auth token to get info about user

**3. Create transaction**

- user must be logged in
- POST api/transactions - with data sender (<int:id>), recipient (email (string)), transfer amount (float, int)

**4. To get user transactions**

- user must be logged in
- GET api/transactions/user/<int:id>
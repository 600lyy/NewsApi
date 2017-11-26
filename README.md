## Dependency Installation:
- `pip3 install -r requirement.txt`

## Database Setup:

- Alternative 1: Follow this tutorial to set up your PostgreSQL role & database
		[https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)
```
#!bash

# To solve the issue regarding 'password authentication failed for user postgres' when running models.py
# a password must be assigned to the user postgres
$ sudo -u postgres psql
$ ALTER USER postgres PASSWORD 'passwd'
```

## Build Test DB:

```
#!bash

# Assuming you have already created your database and configured your settings.py
$ cd ~/NewsExtractort
$ python3 ./models.py
$ Deleting and initializing tables, press Enter to continue...
# Press ENTER

```

## Configure Diffbot API Token:

-  Run the command below:

	`cp ./diffbot_lib/config.py.example ./diffbot_lib/config.py`

	Then update the API Token value with the valid one.

	_Note:_ token HAS TO BUYo.

## Run url extraction test:
- `python3 urlExtract.py`


## Run article_url Scrapy Spider Test:
1. Run & write results into database: `scrapy crawl article_url`
2. Run without updating database: `scrapy crawl article_url -a write_db=False`
3. Or `scrapy crawl article_url_test`
4. Generate a copy of parsed article url in json: `scrapy crawl article_url_test -o results.json`

## SQL query statement to see relations between index_url and article_url:

```
#!sql

SELECT s.index_url, a.article_url
FROM subscriptionarticle sa, article a, subscription s
WHERE sa.subscription_id=s.id AND sa.article_id = a.id;
```


## Download Top-Level Domain List:
https://data.iana.org/TLD/tlds-alpha-by-domain.txt

## Run test with docker

```
#!bash
# Assuming you have docker-ce installed on your machince and you do have interet access
# The following command will start 2 containers (PostgreSQL and Python) to initialize
# database and execute command "scrapy crawl article_url -o results.json"

$ make test

```

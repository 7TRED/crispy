# Scraper Service

Service to scraper tech news articles from various sites and store in a database.

## Prerequisites

- Python 3.10
- Pipenv

## Installation

To install pipenv run:

```bash
pip install pipenv
```

## Development

1. Clone the repository:

   ```bash
    git clone https://github.com/7TRED/crispy.git
    ```

2. Navigate to the project directory.
    - On Linux:

        ```bash
        cd ./crispy/services/scraper-service
        ```

    - On Windows:

        ```powershell
        cd .\crispy\services\scraper-service
        ```

3. Activate the virtual environment:

    ```bash
    pipenv shell
    ```

4. Install project dependencies:

    ```bash
    pipenv install
    ```

    This will install the project dependencies from Pipfile and Pipfile.lock.

5. Install new project dependencies:

    ```bash
    pipenv install <package-name>
    ```

    This will install the project dependency and will update the Pipfile and Pipfile.lock

6. Install development dependencies:

    ```bash
    pipenv install --dev <package-name>
    ```

## Create a new spider

To create a new Scrapy spider, follow these steps:

1. Navigate to the `news_scraper` directory in the `scraper_service`.

2. Run the following command to create a new spider:

    ```bash
    scrapy genspider <spider-name> <domain>
    ```

    Replace `<spider-name>` with the name of your spider and `<domain>` with the domain of the website you want to crawl. For example, to create a spider for the website `<https://quotes.toscrape.com>`, you would run:

    ```bash
    scrapy genspider quotes quotes.toscrape.com
    ```

    This command creates a new Python file in the `spiders` directory of your project. You can edit this file to define the behavior of your spider.

## Running Your Spider

To run your Scrapy spider, follow these steps:

1. Make sure you're in your `news_scraper` directory.

2. Run the following command to start your spider to test it locally:

    ```bash
    scrapy crawl <spider-name> -s DISABLE_MONGO_PIPELINE=True
    ```

    The `DISABLE_MONGO_PIPELINE` setting will disable the Mongodb pipeline, so that you can test the scraper locally.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

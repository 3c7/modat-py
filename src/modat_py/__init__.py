from logging import getLogger
from sys import exit, stderr
from time import sleep
from typing import Annotated

import requests


class Modat:
    def __init__(self, api_key: str, delay: int = 3):
        self.api_key = api_key
        self.base_url = "https://api.magnify.modat.io/"
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        self.session.headers["Authorization"] = self.api_key
        self.session.headers["Content-Type"] = "application/json"
        self.session.headers["User-Agent"] = "Modat-Py/0.1 (github.com/3c7)"
        self.logger = getLogger("modat-py")
        self.delay = delay

    def search_page(
        self,
        query: str,
        page: int,
        page_size: int = 10,
        facets: list | None = None,
        facet_size: int | None = None,
    ) -> dict:
        try:
            resp = self.session.post(
                url=f"{self.base_url}host/search/v1",
                json={
                    "query": query,
                    "page": page,
                    "page_size": page_size,
                    "facets": facets,
                    "facet_size": facet_size,
                },
            )
            resp.raise_for_status()
        except (requests.exceptions.BaseHTTPError, requests.exceptions.HTTPError):
            msg = "Exception while trying to fetch query results from Modat"
            if resp.text:
                msg += f": {resp.text}"
            self.logger.exception(msg)
            raise
        sleep(self.delay)
        return resp.json()

    def search(
        self,
        query: str,
        max_pages: int = -1,
        page_size: int = 10,
        facets: list = [],
        facet_size: int = 10,
    ) -> list:
        results = []
        current_page = 1
        total_pages = None
        while True:
            if (
                current_page + 1 == max_pages
                or total_pages
                and current_page == total_pages + 1
            ):
                return results

            try:
                self.logger.info(f"Retrieving page {current_page}...")
                data = self.search_page(
                    query=query,
                    page=current_page,
                    page_size=page_size,
                    facets=facets,
                    facet_size=facet_size,
                )
            except (requests.exceptions.BaseHTTPError, requests.exceptions.HTTPError):
                return results
            results.extend(data.get("page", []))
            total_pages = data.get("total_pages")
            current_page += 1
        return results


def main():
    try:
        import typer
        from typer import Typer
    except ImportError:
        print(
            'CLI dependencies not installed. Please install with "modat-py[cli]"',
            file=stderr,
        )
        exit(1)
    app = Typer()

    @app.command(name="search", help="Query the Modat API and return results.")
    def cli_search(
        query: Annotated[str, typer.Argument(help="Query to send to Modat API")],
        pages: Annotated[
            int,
            typer.Option("--pages", "-p", help="Pages to fetch, use -1 for all pages."),
        ] = 1,
        json: Annotated[
            bool, typer.Option("--json", "-j", help="Output as JSON to stdout.")
        ] = False,
    ):
        print("Not yet implemented.")

    app()

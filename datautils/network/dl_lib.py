"""Utility for downloading files from a website.
Uses the BeautifulSoup library for managing parsed HTML content.
"""

from bs4 import BeautifulSoup # type: ignore
import logging # type: ignore
from pathlib import Path, PurePath # Type: ignore
from typing import List, Optional # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.network import http_lib # type: ignore
from datautils.core.utils import Error, OK, Status # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output


logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################
# Download

def download(url: str,
             extensions: List[str],
             output_dir: str,
             base_url: Optional[str] = None,
             print_progress : bool = False,
             dry_run : bool = False
             ) -> Status:
    """"Non-recurseive download of given extensions into output folder.
    Args
        url: URL to extract list of links from
        extensions: list of string of file extensions to download
        output_dir: directory in which downlaods will be placed
        base_url: if page uses relative urls in hrefs, add base
        print_progress: print download progress by file count
        dry_run: construct directory and extract urls but don't download / save
    """
    status : Status = OK()

    r = http_lib.get(url)
    if r.status_code != 200:
        return Error('No valid HTTP result to parse')

    urls = parse_urls(r.text)
    urls_ = filter_urls(urls, extensions)

    if base_url:
        urls_ = [http_lib.url_join([base_url, url]) for url in urls_]

    if not urls_:
        status = Error('No links returned after filtering and parsing.')
    else:
        status = save_urls(urls_, output_dir, print_progress, dry_run)

    return status



################################################################################
# parser


def parse_urls(html: str) -> List[str]:
    """Parse HTML with BS, get <a> href attributes."""
    links = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            links.append(link.get('href'))
    except Exception as e:
        logger.error(f'Parse error: {e}')

    return links


################################################################################
# Processing


def filter_urls(urls: List[str], extensions: List[str]) -> List[str]:
    """Filter urls for target extensions."""
    return [url for url in urls
            if url and url.strip().split('.')[-1] in extensions]



################################################################################
# Saving Content


def save_urls(urls: List[str],
              output_dir: str,
              print_progress: bool,
              dry_run: bool) -> Status:
    """Save URLs."""
    status : Status = OK()

    try:
        root = f'./{output_dir}'
        Path(root).mkdir(parents=True, exist_ok=False)
        n = len(urls)
        for i, url in enumerate(urls):
            if dry_run:
                print(f'Dry run: get url {url}')
            else:
                save_url(url, root)
                if print_progress:
                    print(f'Processed {i + 1} of {n} urls.')
        status = OK(f'Done: processed {len(urls)} urls.')

    except Exception as e:
        status = Error(f'Saving failed: {e}')

    return status



def save_url(url: str, root: str):
    """"Save url raw content to target path."""

    try:
        r = http_lib.get(url)
        if r.status_code == 200:
            fname = url.split('/')[-1]
            path = PurePath.joinpath(Path(root), fname)
            with Path(path).open('wb') as f:
                f.write(r.content)
            logger.info(f'Download and save success: {path}')
        else:
            logger.error(f'Download failed for {url}')

    except Exception as e:
        logger.error(f'Download or save failed: {e}')


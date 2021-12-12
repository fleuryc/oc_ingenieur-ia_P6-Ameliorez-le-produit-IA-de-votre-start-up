"""
Make Dataset CLI.

This file defines the `make-dataset` command line.

usage: make-dataset.py [-h] [-t TEXT]

Download and save data from Yelp API.

optional arguments:
  -h, --help            show this help message and exit
  -t TEXT, --text TEXT  Input text of which we want to detect the language.
"""

import argparse
import json
import logging

# System modules
import os
import sys
from hashlib import md5

# ML modules
import pandas as pd
import requests
from dotenv import load_dotenv

# Import custom helper libraries
import src.data.helpers as data_helpers


def get_yelp_data(
    locations: list[str],
    category: str = "restaurants",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Get Yelp data from API.

    - iterate over the locations
        - build a GraphQL query to get the data
        - send the query to the Yelp API
        - parse the response
        - append to the dataframe
    - return the dataframes

    Params:
        locations: str[] (default: ["Paris"]) - List of Yelp locations to search
        category: str (default: "restaurants") - Yelp category (see
            https://www.yelp.com/developers/documentation/v3/all_category_list)

    Returns:
        businesses: pd.DataFrame - businesses data from Yelp API request
        reviews: pd.DataFrame - reviews data from Yelp API request
        photos: pd.DataFrame - photos data from Yelp API request
    """
    # businesses data (see
    #   https://www.yelp.com/developers/graphql/objects/business)
    businesses = pd.DataFrame(
        columns=[
            "business_alias",  # Unique Yelp alias of this business.
            "business_review_count",  # Total number of reviews
            "business_rating",  # Average of the ratings of all reviews
            "business_price",  # Price range, from "$" to "$$$$" (inclusive)
            "business_city",  # City of this business
            "business_state",  # ISO 3166-2 (with a few exceptions) state code
            # (see https://www.yelp.com/developers/documentation/v3/state_codes)
            "business_postal_code",  # Postal code
            # (see https://en.wikipedia.org/wiki/Postal_code)
            "business_country",  # ISO 3166-1 alpha-2 country code
            "business_latitude",  # Latitude
            "business_longitude",  # Longitude
            "business_categories",  # List of categories
            "business_parent_categories",  # List of parent categories
        ]
    )
    reviews = pd.DataFrame(
        columns=[
            "business_alias",  # Unique Yelp alias of the business.
            "review_text",  # Text excerpt of this review.
            "review_rating",  # Rating of this review.
        ]
    )
    photos = pd.DataFrame(
        columns=[
            "business_alias",  # Unique Yelp alias of the business.
            "photo_url",  # URL of the photo.
        ]
    )

    # Yelp's GraphQL endpoint
    url = "https://api.yelp.com/v3/graphql"
    # Request headers
    headers = {
        "Authorization": f"Bearer {YELP_API_KEY}",
        "Content-Type": "application/graphql",
    }
    count = 200  # Yelp's GraphQL API returns a maximum of 240 total results
    limit = 50  # Yelp's GraphQL API returns a maximum of 50 results per request

    for location in locations:
        for offset in range(0, count, limit):
            # Build the GraphQL query
            query = f'{{\n\
        search(\
            categories: "{ category }", \
            location: "{ location }", \
            offset: { offset }, \
            limit:  { limit }\
        ) {{\n\
            business {{\n\
                alias\n\
                review_count\n\
                rating\n\
                price\n\
                location {{\n\
                    city\n\
                    state\n\
                    postal_code\n\
                    country\n\
                }}\n\
                coordinates {{\n\
                    latitude\n\
                    longitude\n\
                }}\n\
                categories {{\n\
                    alias\n\
                    parent_categories {{\n\
                        alias\n\
                    }}\n\
                }}\n\
                photos\n\
                reviews {{\n\
                    text\n\
                    rating\n\
                }}\n\
            }}\n\
        }}\n\
    }}'
            # Send the query to the Yelp API
            response = requests.post(url, headers=headers, data=query)
            # Parse the response
            if not response.status_code == 200:
                raise Exception(
                    "Yelp API request failed with status code "
                    + str(response.status_code)
                    + f" . Response text: { response.text }"
                )

            # Parse the response
            data = response.json()

            if "errors" in data:
                raise Exception(
                    f"Yelp API request failed with errors: { data['errors'] }"
                )

            for business in data.get("data", {}).get("search", {}).get("business", []):
                # Add the business data to the dataframe
                businesses = businesses.append(
                    {
                        "business_alias": business.get("alias"),
                        "business_review_count": business.get("review_count"),
                        "business_rating": business.get("rating"),
                        "business_price": len(  # count the number of characters
                            business.get("price")
                        )
                        if business.get("price") is not None
                        else 0,
                        "business_city": business.get("location", {}).get("city"),
                        "business_state": business.get("location", {}).get("state"),
                        "business_postal_code": business.get("location", {}).get(
                            "postal_code"
                        ),
                        "business_country": business.get("location", {}).get("country"),
                        "business_latitude": business.get("coordinates", {}).get(
                            "latitude"
                        ),
                        "business_longitude": business.get("coordinates", {}).get(
                            "longitude"
                        ),
                        "business_categories": json.dumps(
                            list(
                                {  # convert to a set to remove duplicates
                                    cat.get("alias")
                                    for cat in business.get("categories", [])
                                }
                            )
                        ),
                        "business_parent_categories": json.dumps(
                            list(
                                set(  # keep unique values
                                    [
                                        parent_cat.get("alias")
                                        for cat in business.get("categories", [])
                                        for parent_cat in cat.get(
                                            "parent_categories", []
                                        )
                                    ]
                                )
                            )
                        ),
                    },
                    ignore_index=True,
                )

                for photo in business.get("photos", []) or []:
                    # Add the photo data to the dataframe
                    photos = photos.append(
                        {
                            "business_alias": business.get("alias"),
                            "photo_url": photo,
                            "file_name": business.get("alias")
                            + "_"
                            + md5(photo.encode("utf-8")).hexdigest()  # nosec: B303
                            + ".jpg",
                        },
                        ignore_index=True,
                    )

                for review in business.get("reviews", []) or []:
                    # Add the review data to the dataframe
                    reviews = reviews.append(
                        {
                            "business_alias": business.get("alias"),
                            "review_text": review.get("text"),
                            "review_rating": review.get("rating"),
                        },
                        ignore_index=True,
                    )

    # Return the dataframes
    return businesses, reviews, photos


def download_photos(
    photos: pd.DataFrame,
    target_path: str,
) -> None:
    """
    Download photos from the Yelp API and save them to the target path.

    Params:
        photos (pd.DataFrame): Dataframe containing the photos to download.
        target_path (str): Path to the directory where the photos should be saved.

    Returns:
        None
    """
    # Check if content path exists
    if not os.path.exists(target_path):
        logging.info("Creating %s", target_path)
        os.makedirs(target_path)

    for photo in photos.itertuples(index=False):
        file_path = os.path.join(target_path, photo.file_name)

        if not os.path.exists(file_path):
            # Download the photo
            request = requests.get(photo.photo_url)
            if not request.status_code == 200:
                logging.warning(
                    f"Photo URL : { photo.photo_url }\n"
                    + "Yelp API request failed with status code: "
                    + f"{ request.status_code }.\n"
                    + f"Response text: { request.text }"
                )
                continue

            photo_data = request.content
            with open(file_path, "wb") as f:
                # Write the photo to the file
                f.write(photo_data)


def main() -> None:
    """
    Download and save data and photos.

    Returns:
        None
    """
    businesses_csv_path = os.path.join(DATA_PATH, "businesses.csv")
    reviews_csv_path = os.path.join(DATA_PATH, "reviews.csv")
    photos_csv_path = os.path.join(DATA_PATH, "photos.csv")

    if (
        os.path.exists(businesses_csv_path)
        and os.path.exists(reviews_csv_path)
        and os.path.exists(photos_csv_path)
    ):
        logging.info("Data already downloaded")
        # Early exit if data already downloaded
        sys.exit(0)

    if not os.path.exists(DATA_PATH):
        logging.info("Creating %s", DATA_PATH)
        os.makedirs(DATA_PATH)

    logger.info("Downloading data")
    businesses_df, reviews_df, photos_df = get_yelp_data(
        locations=[
            "Paris",
            "New York City",
            "Tokyo",
            "Rio de Janeiro",
            "Sydney",
        ],
        category="restaurants",
    )
    logger.info("Data downloaded")

    # Fix dtypes
    businesses_df["business_alias"] = businesses_df["business_alias"].astype(str)
    businesses_df["business_review_count"] = businesses_df[
        "business_review_count"
    ].astype(int)
    businesses_df["business_rating"] = businesses_df["business_rating"].astype(float)
    businesses_df["business_price"] = businesses_df["business_price"].astype(int)
    businesses_df["business_city"] = businesses_df["business_city"].astype(str)
    businesses_df["business_state"] = businesses_df["business_state"].astype(str)
    businesses_df["business_postal_code"] = businesses_df[
        "business_postal_code"
    ].astype(str)
    businesses_df["business_country"] = businesses_df["business_country"].astype(str)
    businesses_df["business_latitude"] = businesses_df["business_latitude"].astype(
        float
    )
    businesses_df["business_longitude"] = businesses_df["business_longitude"].astype(
        float
    )
    businesses_df["business_categories"] = businesses_df["business_categories"].astype(
        str
    )
    businesses_df["business_parent_categories"] = businesses_df[
        "business_parent_categories"
    ].astype(str)

    reviews_df["business_alias"] = reviews_df["business_alias"].astype(str)
    reviews_df["review_text"] = reviews_df["review_text"].astype(str)
    reviews_df["review_rating"] = reviews_df["review_rating"].astype(float)

    photos_df["business_alias"] = photos_df["business_alias"].astype(str)
    photos_df["photo_url"] = photos_df["photo_url"].astype(str)
    photos_df["file_name"] = photos_df["file_name"].astype(str)

    # Reduce memory usage
    businesses_df = data_helpers.reduce_dataframe_memory_usage(businesses_df)
    reviews_df = data_helpers.reduce_dataframe_memory_usage(reviews_df)
    photos_df = data_helpers.reduce_dataframe_memory_usage(photos_df)

    # Save the dataframes
    logger.info("Saving data")
    businesses_df.to_csv(businesses_csv_path, index=False)
    reviews_df.to_csv(reviews_csv_path, index=False)
    photos_df.to_csv(photos_csv_path, index=False)
    logger.info("Data saved")

    # Save the photos
    logger.info("Downloading photos")
    download_photos(photos_df, target_path=os.path.join(DATA_PATH, "photos"))
    logger.info("Photos downloaded")


if __name__ == "__main__":
    # Read the command line arguments
    parser = argparse.ArgumentParser(
        description="Download Yelp data and save it to the target directory."
    )
    parser.add_argument(
        "-t",
        "--target_path",
        type=str,
        help="Path to the directory where the data should be saved.",
    )
    args = parser.parse_args()

    # Set the global variables
    DATA_PATH = args.target_path

    # Load environment variables from .env file
    load_dotenv()
    YELP_CLIENT_ID = os.getenv("YELP_CLIENT_ID")
    YELP_API_KEY = os.getenv("YELP_API_KEY")

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    main()

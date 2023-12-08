import sys
import pandas as pd
import json
import fb_api
import logging

# Setup Logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
cfh = logging.FileHandler('common.log', encoding='utf-8')
cfh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
chandler.setFormatter(formatter)
cfh.setFormatter(formatter)
logger.addHandler(chandler)
logger.addHandler(cfh)


# Function to get search terms
def get_search_terms():
    if len(sys.argv) > 1:
        # Use the command line argument if provided
        search_string = sys.argv[1]
    else:
        # Prompt the user for input if no command line argument is provided
        search_string = input("Enter search terms separated by spaces: ")

    # Split the search string into terms
    return search_string.split()


def main(search_terms=None):
    # Load the CSV file
    fb_api.generate_bom_csv()
    df = pd.read_csv('bom.csv')

    # Get search terms from command line arguments or user input
    if search_terms is None:
        search_terms = get_search_terms()

    # Start with a mask that selects everything
    mask = pd.Series([True] * len(df))

    # Update the mask to select only rows that contain all search terms in the Description
    for term in search_terms:
        mask &= df['Description'].str.contains(term, case=False, na=False)

    # Apply the mask to the dataframe to filter the results
    filtered_df = df[mask]

    # Check if the DataFrame has data
    if not filtered_df.empty:
        pass
        # print("Filtered DataFrame is not empty. Proceeding to convert to JSON.")
    else:
        print("Filtered DataFrame is empty. Exiting.")
        return

    # Convert the filtered dataframe to a dictionary
    parts_dict = filtered_df.to_dict(orient='index')

    # Convert the dictionary to a JSON string and print
    print(json.dumps(parts_dict, indent=4))

    return parts_dict


if __name__ == '__main__':
    main()

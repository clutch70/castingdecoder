import sys
import pandas as pd


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


def main():
    # Load the CSV file
    # Ensure to replace 'path_to_csv.csv' with the actual path to your CSV file
    df = pd.read_csv('bom.csv')

    # Get search terms from command line arguments or user input
    search_terms = get_search_terms()

    # Start with a mask that selects everything
    mask = pd.Series([True] * len(df))

    # Update the mask to select only rows that contain all search terms in the Description
    for term in search_terms:
        mask &= df['Description'].str.contains(term, case=False, na=False)

    # Apply the mask to the dataframe to filter the results
    filtered_df = df[mask]

    # Convert the filtered dataframe to a dictionary
    parts_dict = filtered_df.set_index('PartNumber').T.to_dict('dict')

    # Display the dictionary
    for part_number, details in parts_dict.items():
        print(f"Part Number: {part_number}")
        for key, value in details.items():
            print(f"  {key}: {value}")
        print()  # Add a new line for readability between parts


if __name__ == '__main__':
    main()
import pandas as pd
import argparse

def load_data(file_path):
    """ Load the CSV data into a DataFrame. """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def is_match(column_value, input_value):
    """ Check if the input_value matches any of the comma-separated values in column_value or if the column_value is blank. """
    # Treat blank or NA column_value as a match (regardless of input_value)
    if pd.isna(column_value) or column_value == '':
        return True

    # Convert column_value to string and check for a partial match
    column_value = str(column_value)
    return any(input_value in item for item in column_value.split(','))

def highlight_matched_input(input_value, column_value):
    """ Highlight the matched part in the column value and return if a match was found. """
    if not input_value or pd.isna(column_value) or column_value == '':
        return column_value, False
    if input_value in column_value:
        return column_value.replace(input_value, f'*{input_value}*'), True
    return column_value, False

def get_data_or_default(value):
    """ Return the value or 'NO DATA' if the value is blank or NaN. """
    return value if not pd.isna(value) and value != '' else 'NO DATA'

def find_engine(data, block, right_head, left_head, crank, hollander):
    """ Search for the engine based on casting numbers allowing for partial matches. """
    matches = data.apply(lambda row: is_match(row['BlockCasting'], block) and
                                     is_match(row['RightHeadCasting'], right_head) and
                                     is_match(row['LeftHeadCasting'], left_head) and
                                     is_match(row['CrankCasting'], crank) and
                                     is_match(row['Hollander'], hollander), axis=1)
    return data[matches]

def get_user_input(input_field):
    return input(f"Enter {input_field} (part or full, leave blank if unknown): ")

def main():
    parser = argparse.ArgumentParser(description='Engine Identifier')
    parser.add_argument('--block', help='Block Casting number (part or full)', default='')
    parser.add_argument('--right_head', help='Right Head Casting number (part or full)', default='')
    parser.add_argument('--left_head', help='Left Head Casting number (part or full)', default='')
    parser.add_argument('--crank', help='Crank Casting number (part or full)', default='')
    parser.add_argument('--hollander', help='Hollander Interchange number (part or full)', default='')
    args = parser.parse_args()

    if not any(vars(args).values()):
        args.block = get_user_input("Block Casting number")
        args.right_head = get_user_input("Right Head Casting number")
        args.left_head = get_user_input("Left Head Casting number")
        args.crank = get_user_input("Crank Casting number")
        args.hollander = get_user_input("Hollander Interchange number, suffix only")
    data_file = 'bom.csv'  # Replace with your CSV file path
    data = load_data(data_file)

    if data is not None:
        matching_engines = find_engine(data, args.block, args.right_head, args.left_head, args.crank, args.hollander)
        if not matching_engines.empty:
            for index, row in matching_engines.iterrows():
                block_cast, block_match = highlight_matched_input(args.block, row['BlockCasting'])
                right_head_cast, right_head_match = highlight_matched_input(args.right_head, row['RightHeadCasting'])
                left_head_cast, left_head_match = highlight_matched_input(args.left_head, row['LeftHeadCasting'])
                crank_cast, crank_match = highlight_matched_input(args.crank, row['CrankCasting'])
                hollander_num, hollander_match = highlight_matched_input(args.hollander, row['Hollander'])

                if any([block_match, right_head_match, left_head_match, crank_match, hollander_match]):
                    print(f"Manufacturer: {get_data_or_default(row['Make'])}")
                    print(f"Years: {get_data_or_default(row['Years'])}")
                    print(f"Engine Type: {get_data_or_default(row['Engine'])}")
                    print(f"Block Casting: {get_data_or_default(block_cast)}")
                    print(f"Right Head Casting: {get_data_or_default(right_head_cast)}")
                    print(f"Left Head Casting: {get_data_or_default(left_head_cast)}")
                    print(f"Crank Casting: {get_data_or_default(crank_cast)}")
                    print(f"Hollander: {get_data_or_default(hollander_num)}")
                    print(f"Notes: {get_data_or_default(row['Notes'])}")
                    print("-----------")
        else:
            print("No matching engine found.")
    else:
        print("Failed to load data.")

if __name__ == "__main__":
    main()

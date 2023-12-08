import sys
import json
import fb_api

def main():
    # Check if the correct number of command-line arguments were provided
    if len(sys.argv) != 3:
        print("Usage: python add_po_item.py <po_number> <new_items_dict>")
        return

    # Extract the command-line arguments
    po_number = sys.argv[1]
    new_items_dict = json.loads(sys.argv[2])  # Convert the new items dictionary from a JSON string to a Python dictionary

    # Call the create_po_item function
    fb_api.create_po_item(po_number, new_items_dict)

if __name__ == '__main__':
    main()
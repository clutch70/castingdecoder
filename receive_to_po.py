import sys
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

def main():
    # Check if the correct number of command-line arguments were provided
    if len(sys.argv) != 3:
        logging.debug("Usage: python receive_to_po.py <po_number> <cart_data_dict>")
        return

    # Extract the command-line arguments
    po_number = sys.argv[1]
    cart_data_dict = json.loads(sys.argv[2])  # Convert the cart data dictionary from a JSON string to a Python dictionary

    # Call the create_po_item function in fb_api.py
    fb_api.create_po_item(po_number, cart_data_dict)

if __name__ == '__main__':
    main()
from pprint import pprint

import fb_api
import requests
import keys as k
import json

po_uri = 'api/purchase-orders'

data_query_uri = 'api/data-query'

data = 'SELECT id from po where num = 10'


def create_po_item(po_number, new_items_dict=None, token=None):
    # logger.debug(f"create_part got {part_dict}")
    own_login = False
    if not token:
        token = fb_api.fb_login()
        own_login = True

    if token:
        pass
    else:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    post_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{k.fb_url}/{po_uri}/{po_number}", headers=headers)
        # print(f"FB part creation response is {response.content}")
        # pprint(response.content)
        response_content = response.content.decode()
        po = json.loads(response_content)
        po = construct_po_items(po, new_items_dict)
        pprint(po)
        response = requests.post(f"{k.fb_url}/{po_uri}/{po_number}", headers=post_headers, data=json.dumps(po))

        if own_login:
            fb_api.fb_logout(token)
        response.raise_for_status()

        return response.content
    except Exception as e:
        print(e)


def construct_po_items(json_obj, part_quantity_dict):
    # Extract the existing poItems list from the JSON object
    existing_po_items = json_obj.get('poItems', [])

    po_items = []
    next_line_number = len(existing_po_items) + 1 if existing_po_items else 1
    for part, quantity in part_quantity_dict.items():
        # Create a new poItem with the same keys as the provided JSON, but with all values set to an empty string or
        # an appropriate empty value
        po_item = {
            "class": {"id": "", "name": ""},
            "customFields": [],
            "dateLastFulfilled": "",
            "dateScheduled": "",
            "id": "",
            "lineNumber": next_line_number,
            "mcTotalCost": "",
            "mcTotalTax": "",
            "note": "",
            "part": {"name": part},
            "quantity": str(quantity),
            "quantityFulfilled": "",
            "quantityPicked": "",
            "revision": "",
            "status": "",
            "totalCost": "",
            "totalTax": "",
            "type": {"id": "", "name": ""},
            "unitCost": "",
            "uom": {"abbreviation": "", "id": "", "name": ""},
            "vendorPartNumber": ""
        }
        next_line_number += 1
        po_items.append(po_item)

    # Add the new poItems to the existing poItems list in the JSON object
    json_obj['poItems'] = existing_po_items + po_items

    return json_obj


new_items = {
    'FD-0A-100-AA': 3
}

# pprint(construct_po_items(po_data))
pprint(create_po_item(1, new_items_dict=new_items))

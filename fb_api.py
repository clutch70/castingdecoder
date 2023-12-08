import requests
import keys as k
import logging
import time
from requests.exceptions import HTTPError
import json

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

login_url = 'api/login'
logout_url = 'api/logout'
part_search_url = 'api/parts/?number='
part_create_uri = 'api/import/Part'
po_add_item_uri = 'api/purchaseorder/additem'
po_uri = 'api/purchase-orders'
data_query_uri = 'api/data-query'

login_exceeded_message = 'The login limit'

part_body = [
        "PartNumber",
        "PartDescription",
        "PartDetails",
        "UOM",
        "PartType",
        "ConsumptionRate",
        "POItemType"
]



def fb_login():
    for _ in range(3):  # Loop for 3 attempts
        try:
            response = requests.post(f"{k.fb_url}/{login_url}", json=k.fb_login_params)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
            return response.json()['token']
        except Exception as e:
            logger.error(f"Attempt to login to FB failed with error: {e}")
            time.sleep(30)
    return None


def fb_logout(token):
    for _ in range(3):
        try:
            fb_logout_params = {
                "Authorization": f"Bearer {token}"
            }

            response = requests.post(f"{k.fb_url}/{logout_url}", headers=fb_logout_params)
            return response
        except Exception as e:
            logger.error(f"Attempt to logout from FB failed with error: {e}")
            time.sleep(30)
    return None


def check_part_exists(token, part_number):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{k.fb_url}/{part_search_url}{part_number}", headers=headers)
    logger.debug(f"Check part exists response is {response.content}")
    logger.debug(f"Check part exists vars"
                 f"FB URL {k.fb_url}"
                 f"Part search URL {part_search_url}"
                 f"Part Number {part_number}"
                 f"headers are {headers}")
    #json = response.json()
    #print(json)
    #print(json['totalCount'])
    try:
        if response.json()['totalCount'] > 0:
            return response.json()
        else:
            return False
    except:
        return False

def check_for_part(partNumber, products, create_token=None):
    own_login = False  # Initialize own_login
    if not create_token:
        create_token = fb_login()
        logger.debug(f"FB Login token {create_token} created")
        own_login = True
    if create_token:
        #current_dict = {partNumber: {
        #    'Manufacturer': products[partNumber]['Manufacturer']
        #}}
        #c.add_mfrid_to_parts_dict()

        # Make sure the arguments are in the correct order
        check = check_part_exists(create_token, partNumber)
        if own_login:
            logger.debug(f"Logging out {create_token}")
            fb_logout(create_token)
        return check
    else:
        if own_login:
            fb_logout(create_token)
            logger.debug(f"Logging out {create_token}")
        return False

def verify_part_dict(parts_dict):
    required_elements = ["Description", "Details", "UOM", "UPC", "PartType", "Active", "ABCCode", "Weight", "WeightUOM",
                         "Width", "Height", "Length", "SizeUOM", "ConsumptionRate", "PrimaryTracking", "AlertNote",
                         "PictureUrl", "Revision", "POItemType", "DefaultOutsourcedReturnItem", "Tracks-Lot Number",
                         "Next Value-Lot Number", "Tracks-Revision Level", "Next Value-Revision Level",
                         "Tracks-Expiration Date", "Next Value-Expiration Date", "Tracks-Serial Number",
                         "Next Value-Serial Number", "CF-Castings", "CF-OEM Part No", "CF-Core Return Group",
                         "CF-Block Casting", "CF-Right Head Casting", "CF-Left Head Casting", "CF-Crankshaft Casting",
                         "CF-Application", "Manufacturer", "CF-Engine Family"]

    for part, info in parts_dict.items():
        existing_keys = list(info.keys())

        for element in required_elements:
            # Skip if the element is 'partnumber'
            if element.lower() == 'partnumber':
                continue
            found = False
            for key in existing_keys:
                if key.lower() == element.lower():
                    found = True
                    if key != element:
                        # If the key is mis-capitalized, correct it
                        info[element] = info.pop(key)
                    break
            if not found:
                # If the key does not exist at all, add it
                logger.debug(f"Fixing {element} for {part}")
                info[element] = ''

    return parts_dict

def create_part(part_dict, token=None):
    logger.debug(f"create_part got {part_dict}")
    if not token:
        token = fb_login()
        own_login = True

    if token:
        pass
    else:
        return False

    try:
        part = verify_part_dict(part_dict)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain"
        }


        for partNumber, part in part.items():
            logger.debug(f"CREATING FB PART {partNumber}")
            logger.debug(part)


            #data = f'''"PartNumber","PartDescription","PartDetails","UOM","UPC","PartType","Active","ABCCode","Weight","WeightUOM","Width","Height","Length","SizeUOM","ConsumptionRate","PrimaryTracking","AlertNote","PictureUrl","Revision","POItemType","DefaultOutsourcedReturnItem","Tracks-Lot Number","Next Value-Lot Number","Tracks-Revision Level","Next Value-Revision Level","Tracks-Expiration Date","Tracks-Serial Number","Next Value-Serial Number","CF-Castings","CF-OEM Part No","CF-Core Return Group","CF-Block Casting","CF-Right Head Casting","CF-Left Head Casting","CF-Crankshaft Casting","CF-Application","CF-Manufacturer","CF-Engine Family"
            #    "{partNumber.replace('"', '').replace(' ', '')}","{part.get('Description', '')}","{part.get('Details', '')}","{part.get('UOM', '')}","{part.get('UPC', '')}","{part.get('PartType', '')}","{part.get('Active', '')}","{part.get('ABCCode', '')}","{part.get('Weight', '')}","{part.get('WeightUOM', '')}","{part.get('Width', '')}","{part.get('Height', '')}","{part.get('Length', '')}","{part.get('SizeUOM', '')}","{part.get('ConsumptionRate', '')}","{part.get('PrimaryTracking', '')}","{part.get('AlertNote', '')}","{part.get('PictureUrl', '')}","{part.get('Revision', '')}","{part.get('POItemType', '')}","{part.get('DefaultOutsourcedReturnItem', '')}","{part.get('Tracks-Lot Number', '')}","{part.get('Next Value-Lot Number', '')}","{part.get('Tracks-Revision Level', '')}","{part.get('Next Value-Revision Level', '')}","{part.get('Tracks-Expiration Date', '')}","{part.get('Next Value-Expiration Date', '')}","{part.get('Tracks-Serial Number', '')}","{part.get('Next Value-Serial Number', '')}","{part.get('CF-Castings', '')}","{part.get('CF-OEM Part No', '')}","{part.get('CF-Core Return Group', '')}","{part.get('CF-Block Casting', '')}","{part.get('CF-Right Head Casting', '')}","{part.get('CF-Left Head Casting', '')}","{part.get('CF-Crankshaft Casting', '')}","{part.get('CF-Application', '')}","{part.get('CF-Manufacturer', '')}","{part.get('CF-Engine Family', '')}"'''

            #data = f'''"PartNumber","PartDescription","PartDetails","UOM","PartType","POItemType","CF-Application","CF-Manufacturer","CF-Engine Family"
            #        {partNumber.replace(' ', '')},'{part.get('Description', '')}','{part.get('Details', '')}',{part.get('UOM', '')},{part.get('PartType', 'Stock')},{part.get('POItemType', '')},'{part.get('CF-Application', '')}','{part.get('CF-Manufacturer', '')},'{part.get('CF-Engine Family', '')}'''

            partNumber = partNumber.replace(' ', '')  # Assuming partNumber is defined earlier
            partDescription = part.get('Description', '').replace('"', '""')  # Escaping double quotes within the field
            partDetails = part.get('Details', '').replace('"', '""')  # Escaping double quotes within the field
            #uom = part.get('UOM', 'ea')
            #partType = part.get('PartType', 'Inventory')
            #poItemType = part.get('POItemType', 'Purchase')
            uom = part.get('UOM', '').strip() or 'ea'
            partType = part.get('PartType', '').strip() or 'Inventory'
            poItemType = part.get('POItemType', '').strip() or 'Purchase'

            cfApplication = part.get('CF-Application', '').replace('"', '""')  # Escaping double quotes within the field
            cfManufacturer = part.get('CF-Manufacturer', '').replace('"',
                                                                     '""')  # Escaping double quotes within the field
            cfEngineFamily = part.get('CF-Engine Family', '').replace('"',
                                                                      '""')  # Escaping double quotes within the field

            data = f'''"PartNumber","PartDescription","PartDetails","UOM","PartType","POItemType","CF-Application","CF-Manufacturer","CF-Engine Family"
            "{partNumber}","{partDescription}","{partDetails}","{uom}","{partType}","{poItemType}","{cfApplication}","{cfManufacturer}","{cfEngineFamily}"'''

            logger.debug(f"Creating FB part {data}")
            try:
                response = requests.post(f"{k.fb_url}/{part_create_uri}",headers=headers,data=data)
                logger.debug(f"FB part creation response is {response.content}")
                logger.debug(f"Logging out {token}")
                fb_logout(token)
                response.raise_for_status()

                return response
            except HTTPError as http_err:
                if response.status_code == 400:
                    logger.warning(f"HTTP client error occurred when creating FB part: {http_err} - {response.json()}")
                    logger.warning("HTTP 400 - Check syntax when posting this data to FB.")
                else:
                    logger.warning(f"An unexpected HTTP error occurred when creating FB part: {http_err}")
            except Exception as e:
                logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                logger.error(f"Failed to create part in Fishbowl {partNumber} for error {e}.")
                logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                if own_login:
                    logger.debug(f"Logging out {token}")
                    fb_logout(token)
        if own_login:
            fb_logout(token)
            logger.debug(f"Logging out {token}")
    except:
        if own_login:
            fb_logout(token)
            logger.debug(f"Logging out {token}")
    if own_login:
        fb_logout(token)
        logger.debug(f"Logging out {token}")


def get_po_id(po_number, token=None):
    if not token:
        token = fb_login()
        own_login = True

    if token:
        pass
    else:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }

    data = f'SELECT id from po where num = {po_number}'

    try:
        response = requests.get(f"{k.fb_url}/{data_query_uri}", headers=headers, data=data)
        response_content = response.content.decode()
        api_data = json.loads(response_content)
        id_value = api_data[0]['id']
        fb_logout(token)
        response.raise_for_status()

        return id_value

    except Exception as e:
        logger.error(f"Failed to get PO ID in Fishbowl {po_number} for error {e}.")


def create_po_item(po_number, new_items_dict=None, token=None):
    # logger.debug(f"create_part got {part_dict}")
    if not token:
        token = fb_login()
        own_login = True

    if token:
        pass
    else:
        return False

    po_id = query_fb(f"SELECT id from po where num = '{po_number}'", 'id', token=token)
    logger.debug(f"Got PO ID {po_id} for PO {po_number}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    post_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{k.fb_url}/{po_uri}/{po_id}", headers=headers)
        # print(f"FB part creation response is {response.content}")
        # pprint(response.content)
        response_content = response.content.decode()
        po = json.loads(response_content)
        po = construct_po_items(po, new_items_dict, token=token)
        logger.debug(po)
        response = requests.post(f"{k.fb_url}/{po_uri}/{po_id}", headers=post_headers, data=json.dumps(po))
        logger.debug(response.content)
        # id_value = api_data[0]['id']
        # print(id_value)
        # logger.debug(f"FB part creation response is {response.content}")
        # print(f"Logging out {token}")
        # logger.debug(f"Logging out {token}")
        fb_logout(token)
        response.raise_for_status()

        return response.content
    except Exception as e:
        logger.error(e)


def construct_po_items(json_obj, part_quantity_dict, token=None):
    # Extract the existing poItems list from the JSON object
    existing_po_items = json_obj.get('poItems', [])

    po_items = []
    next_line_number = len(existing_po_items) + 1 if existing_po_items else 1
    for part, quantity in part_quantity_dict.items():
        description = query_fb(f"SELECT description from part where num = '{part}'", 'description', token=token)
        logger.debug(f"construct_po_items got description {str(description)}")
        unit_cost = query_fb(f"SELECT stdCost from part where num = '{part}'", 'stdCost', token=token)
        unit_cost = int(float(unit_cost))
        total_cost = unit_cost * quantity
        logger.debug(f"construct_po_items got unit_cost {str(unit_cost)}")
        part_id = query_fb(f"SELECT id from part where num = '{part}'", 'id', token=token)
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
            "part": {"name": part, "id": part_id, "description": f"{description}"},
            "quantity": str(quantity),
            "quantityFulfilled": "",
            "quantityPicked": "",
            "revision": "",
            "status": "",
            "totalCost": total_cost,
            "totalTax": "",
            "type": {"id": 10, "name": "Purchase"},
            "unitCost": unit_cost,
            "uom": {"abbreviation": "ea", "id": 1, "name": "Each"},
            "vendorPartNumber": ""
        }
        next_line_number += 1
        po_items.append(po_item)

    # Add the new poItems to the existing poItems list in the JSON object
    json_obj['poItems'] = existing_po_items + po_items

    return json_obj

def query_fb(query, column, token=None):
    own_login = False
    if not token:
        token = fb_login()
        own_login = True

    if token:
        pass
    else:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }

    try:
        response = requests.get(f"{k.fb_url}/{data_query_uri}", headers=headers, data=query)
        logger.debug(response.content)
        response_content = response.content.decode()

        api_data = json.loads(response_content)
        reply = api_data[0][column]  # Access the first item in the list and the value of the column key
        if own_login:
            fb_logout(token)
        response.raise_for_status()
        logger.debug(f"query_fb returned {reply}")
        return reply

    except Exception as e:
        logger.error(f"Failed to query Fishbowl for with query {query} with error {e}.")

def get_part_description(part_number, token=None):
    if not token:
        token = fb_login()
        own_login = True

    if token:
        pass
    else:
        return False



    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }

    data = f'SELECT description from part where num = {part_number}'

    try:
        response = requests.get(f"{k.fb_url}/{data_query_uri}", headers=headers, data=data)
        response_content = response.content.decode()
        api_data = json.loads(response_content)
        reply = api_data[0]['num']
        if own_login:
            fb_logout(token)
        response.raise_for_status()

        return reply

    except Exception as e:
        logger.error(f"Failed to get description in Fishbowl for part {part_number} with error {e}.")

def main():
    #token = fb_login()
    if check_for_part('0518d4079AC'):
        print('Found')
    else:
        print('None')
    #print(token)
    #print(check_part_exists(token,'051d84079AC'))
    #logout = fb_logout(token)

if __name__ == '__main__':
    pass
    #main()
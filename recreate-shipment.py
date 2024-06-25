import os
import json
import easypost
from dotenv import load_dotenv
import webbrowser

load_dotenv()

test_key = os.getenv("TEST_KEY")
prod_key = os.getenv("PROD_KEY")

client = easypost.EasyPostClient(test_key)

properties = [
    "created_at",
    "messages",
    "status",
    "tracking_code",
    "updated_at",
    "batch_id",
    "batch_status",
    "batch_message",
    "id",
    "order_id",
    "postage_label",
    "tracker",
    "selected_rate",
    "scan_form",
    "usps_zone",
    "refund_status",
    "mode",
    "fees",
    "object",
    "rates",
    "insurance",
    "forms",
    "verifications"
]


with open("./EasyPost Python Scripts/misc.JSON") as data:
    ship = json.load(data)
    nest = [
        ship["to_address"],
        ship["from_address"],
        ship["return_address"],
        ship["buyer_address"],
        ship["parcel"],
    ]

    for item in properties:
        if item in ship:
            del ship[item]

    for obj in nest:
        for item in properties:
            if item in obj:
                del obj[item]

    if ship["customs_info"] != None:
        for item in properties:
            if item in ship["customs_info"]:
                del ship["customs_info"][item]
            for custItem in ship["customs_info"]["customs_items"]:
                for item in properties:
                    if item in custItem:
                        del custItem[item]
    
    if "print_custom" in ship["options"]:
        del ship["options"]["print_custom"]

    try:
        shipment = client.shipment.create(
            is_return=ship["is_return"],
            reference=ship["reference"],
            to_address=ship["to_address"],
            from_address=ship["from_address"],
            parcel=ship["parcel"],
            customs_info=ship["customs_info"],
            options=ship["options"],
            # carrier_accounts= [""],
            # service= "GroundAdvantage"
        )

        if(shipment["tracking_code"] == None):
            for rate_error in shipment["messages"]:
                carrier = rate_error["carrier"]
                message = rate_error["message"]
                print(f"{carrier}: {message}")

            print()
            for rate in shipment["rates"]:
                carrier = rate["carrier"]
                service = rate["service"]
                rate_id = rate["id"]
                rate = rate["rate"]
                print(f"{carrier}: {service}: {rate}")
                print(f"{rate_id}\n")
        
            response = input("Please enter the rate to purcahse, or press enter to quit: ")
            if("rate_" in response):
                bought_shipment = client.shipment.buy(shipment.id, rate={"id": response})
                #data
                webbrowser.open_new_tab(bought_shipment["postage_label"]["label_url"])
            else:
                #data
                quit
        else:
            #data
            webbrowser.open_new_tab(shipment["postage_label"]["label_url"])
    except easypost.errors.api.ApiError as error:
        print(error.code +": "+ error.message)
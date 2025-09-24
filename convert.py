from math import nan
import partridge as ptg
import pandas as pd
import os
import zipfile
import uuid


def convert_fares(input, output):
    generated_uuid = uuid.uuid4()

    # Unzip GTFS for us to work with it
    with zipfile.ZipFile(input, "r") as zip_ref:
        zip_ref.extractall(f"/tmp/gtfs/{generated_uuid}/in")

    # Import the feed
    feed = ptg.load_raw_feed(f"/tmp/gtfs/{generated_uuid}/in")

    # Read tables we need into memory
    fare_attributes = feed.fare_attributes
    fare_rules = feed.fare_rules
    stops = feed.stops
    agency = feed.agency
    routes = feed.routes

    # Create new tables
    fare_products = pd.DataFrame(
        columns=[
            "fare_product_id",
            "fare_product_name",
            "amount",
            "currency",
            "fare_media_id",
        ]
    )
    fare_media = pd.DataFrame(
        columns=["fare_media_id", "fare_media_name", "fare_media_type"]
    )
    fare_leg_rules = pd.DataFrame(
        columns=[
            "leg_group_id",
            "network_id",
            "fare_product_id",
            "from_area_id",
            "to_area_id",
            "is_symmetrical"
        ]
    )
    networks = pd.DataFrame(columns=["network_id", "network_name"])
    route_networks = pd.DataFrame(columns=["network_id", "route_id"])
    stop_areas = pd.DataFrame(columns=["stop_id", "area_id"])
    areas = pd.DataFrame(columns=["area_name", "area_id"])

    # Create static data
    fare_media.loc[len(fare_media)] = {
        "fare_media_id": 0,
        "fare_media_name": "Cash",
        "fare_media_type": 0,
    }

    # If adding rider category support, this is where it would happen.

    # Generate networks from agencies
    for a in agency.itertuples():
        networks.loc[len(networks)] = {
            "network_id": a.agency_id,
            "network_name": a.agency_name,
        }

    # Convert route-based fare rules
    if len(fare_rules) != 0:
        route_rules = fare_rules[fare_rules["route_id"].notna()]
        for rule in route_rules.itertuples():
            fare_products.loc[len(fare_products)] = {
                "fare_product_id": rule.fare_id,
                "fare_product_name": rule.fare_id,
                "amount": fare_attributes[fare_attributes["fare_id"] == rule.fare_id].iloc[0].price,
                "currency": fare_attributes[fare_attributes["fare_id"] == rule.fare_id].iloc[0].currency_type,
                "fare_media_id": 0,
            }
            route_networks.loc[len(route_networks)] = {
                "route_id": rule.route_id,
                "network_id": routes[routes["route_id"] == rule.route_id].iloc[0].agency_id,
            }
            fare_leg_rules.loc[len(fare_leg_rules)] = {
                "leg_group_id": uuid.uuid4(),
                "network_id": routes[routes["route_id"] == rule.route_id].iloc[0].agency_id,
                "fare_product_id": rule.fare_id,
                "from_area_id": "",
                "to_area_id": "",
                "is_symmetrical": ""
            }


    # Convert stop-based fare rules
    if len(fare_rules) != 0:
        stop_rules = fare_rules[fare_rules["origin_id"].notna()]
        for rule in stop_rules.itertuples():
            origin_stop_id = stops[stops["zone_id"] == rule.origin_id].iloc[0].stop_id
            dest_stop_id = stops[stops["zone_id"] == rule.destination_id].iloc[0].stop_id

            areas.loc[len(areas)] = {"area_id": origin_stop_id, "area_name": rule.origin_id}
            areas.loc[len(areas)] = {
                "area_id": dest_stop_id,
                "area_name": rule.destination_id,
            }

            stop_areas.loc[len(areas)] = {
                "area_id": origin_stop_id,
                "stop_id": origin_stop_id,
            }
            stop_areas.loc[len(areas)] = {"area_id": dest_stop_id, "stop_id": dest_stop_id}

            fare_products.loc[len(fare_products)] = {
                "fare_product_id": rule.fare_id,
                "fare_product_name": rule.fare_id,
                "amount": fare_attributes[fare_attributes["fare_id"] == rule.fare_id].iloc[0].price,
                "currency": fare_attributes[fare_attributes["fare_id"] == rule.fare_id].iloc[0].currency_type,
                "fare_media_id": 0,
            }
            fare_leg_rules.loc[len(fare_leg_rules)] = {
                "from_area_id": origin_stop_id,
                "to_area_id": dest_stop_id,
                "is_symmetrical": '0',
                "leg_group_id": uuid.uuid4(),
                # "network_id": fare_attributes[fare_attributes["fare_id"] == rule.fare_id].iloc[0].agency_id,
                "network_id": "",
                "fare_product_id": rule.fare_id,
            }

    # TODO: transfers
    #

    # TODO: agency-based fares (no fare rules file present)

    # Clean up duplicate data
    fare_leg_rules = fare_leg_rules.drop_duplicates().dropna()
    route_networks = route_networks.drop_duplicates().dropna()
    fare_products = fare_products.drop_duplicates().dropna()
    stop_areas = stop_areas.drop_duplicates().dropna()
    areas = areas.drop_duplicates().dropna()

    # Export
    output_dir = f"/tmp/gtfs/{generated_uuid}/in"

    # Add new files
    fare_media.to_csv(f"{output_dir}/fare_media.txt", index=False)
    if len(fare_products) != 0:
        fare_products.to_csv(f"{output_dir}/fare_products.txt", index=False)
    if len(fare_leg_rules) != 0:
        fare_leg_rules.to_csv(f"{output_dir}/fare_leg_rules.txt", index=False)
    if len(networks) != 0:
        networks.to_csv(f"{output_dir}/networks.txt", index=False)
    if len(route_networks) != 0:
        route_networks.to_csv(f"{output_dir}/route_networks.txt", index=False)
    if len(stop_areas) != 0:
        stop_areas.to_csv(f"{output_dir}/stop_areas.txt", index=False)
    if len(areas) != 0:
        areas.to_csv(f"{output_dir}/areas.txt", index=False)

    # Zip the output GTFS feed
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zf.write(file_path, arcname)

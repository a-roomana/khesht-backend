import json
from tqdm import tqdm

def parse_shab_detail_rooms():
    """Process room details, generate summaries, and create embeddings."""
    # Load the room details
    try:
        with open('shab_room_details.json', 'r', encoding='utf-8') as f:
            room_details = json.load(f)
    except Exception as e:
        print(f"Error loading room_details.json: {e}")
        return

    # Initialize the output structure
    processed_data = []

    # Process each item
    for idx, item in enumerate(tqdm(room_details, desc="Processing items")):
        item_parsed = {}
        item_parsed["site"] = "shab.ir"
        item_parsed["lodge_id"] = item["id"]
        item_parsed["description"] = item["about"]
        item_parsed["title"] = item["title"]
        item_parsed["type"] = item["type"]
        item_parsed["rating"] = item["rates"]["value"]
        item_parsed["rating_count"] = item["reviews_count"]
        item_parsed["comments"] = [review["comment"] for review in item["reviews"]]
        item_parsed["area"] = item["building_area"]
        item_parsed["city"] = item["location"]["city"]
        item_parsed["province"] = item["location"]["province"]
        item_parsed["lat"] = item["location"]["latitude"]
        item_parsed["lng"] = item["location"]["longitude"]
        item_parsed["min_price"] = item["pricing"]["records"][0]["workweek_days"]["amount"]
        item_parsed["max_price"] = item["pricing"]["records"][0]["weekend_days"]["amount"]
        item_parsed["extra_person_price"] = item["pricing"]["records"][0]["extra_person"]["amount"]
        item_parsed["images"] = [i["thumbnail_path"] for i in item["pictures"]["records"]]

        processed_data.append(item_parsed)
    
    # Save parsed_data
    with open("shab_room_details_parsed.json", "w", encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)


parse_shab_detail_rooms()
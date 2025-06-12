import requests
import json
import time

location_ids = ['مازندران', 'گیلان', 'گلستان']
all_room_details = []

for location_id in location_ids:
    print(f"Processing location ID {location_id}...")

    # Step 1: Find number of pages
    search_url = f"https://www.shab.ir/_next/data/vLSqXvG6ygrRzxhiGqwXK/search/province/{location_id}.json?routes=province&routes={location_id}&page=0"
    search_response = requests.get(search_url).json()
    pages_to_fetch = int(search_response.get('pageProps', {}).get('data', {}).get('pagination', {}).get('total', 0)/24)

    print(pages_to_fetch)

    for page in range(1, pages_to_fetch + 1):
        print(f"  Fetching page {page}...")

        # Step 1: Fetch search results
        search_url = f"https://www.shab.ir/_next/data/vLSqXvG6ygrRzxhiGqwXK/search/province/{location_id}.json?routes=province&routes={location_id}&page={page}"
        search_response = requests.get(search_url)

        if search_response.status_code != 200:
            print(f"Failed to fetch search results for page {page}: {search_response.status_code}")
            continue

        search_data = search_response.json()
        room_items = search_data.get('pageProps', {}).get('data', {}).get('list', [])

        if not room_items:
            print(f"    No rooms found on page {page}. Stopping early for this location.")
            break

        # Step 2: Fetch room details
        for room in room_items:
            room_id = room.get('id')
            if room_id:
                detail_url = f"https://www.shab.ir/_next/data/vLSqXvG6ygrRzxhiGqwXK/houses/show/{room_id}.json?id={room_id}"
                detail_response = requests.get(detail_url)

                if detail_response.status_code == 200:
                    room_data = detail_response.json().get('pageProps', {}).get('data', {})
                    room_data['location_id'] = location_id  # Tag with location
                    room_data['page'] = page                # Tag with page number
                    all_room_details.append(room_data)
                    print(f"    ✓ Fetched room ID {room_id}")
                else:
                    print(f"    ✗ Failed to fetch details for room ID {room_id}: {detail_response.status_code}")

                time.sleep(0.01)  # API friendly pause

# Step 3: Save all room details
with open("shab_room_details.json", "w", encoding='utf-8') as f:
    json.dump(all_room_details, f, ensure_ascii=False, indent=2)

print("✅ All room details saved to room_details.json")

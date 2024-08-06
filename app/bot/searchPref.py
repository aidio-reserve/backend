from geopy.geocoders import Nominatim
import pycountry


geolocator = Nominatim(user_agent="aidio_app")


# 緯度経度から住所情報を取得
def get_location_info_from_lat_lon(latitude, longitude, geolocator):
    try:
        location = geolocator.reverse((latitude, longitude), language="ja")
        if location and location.raw.get("address"):
            address = location.raw["address"]
            prefecture_code = address.get("ISO3166-2-lvl4")
            city = address.get("city") or address.get("town") or address.get("village")
            return prefecture_code, city
    except Exception as e:
        print(f"Error: {e}")
    return None, None


# 都道府県コードから都道府県名を取得
def get_subdivision_name(iso_code):
    subdivision = pycountry.subdivisions.get(code=iso_code)
    if subdivision:
        return subdivision.name
    return None


def get_prefecture_name_from_lat_lon(latitude, longitude, geolocator):
    prefecture_code, city = get_location_info_from_lat_lon(
        latitude, longitude, geolocator
    )
    if prefecture_code:
        return get_subdivision_name(prefecture_code), city
    return None

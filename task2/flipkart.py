
from pydantic import BaseModel,field_validator
import re
import json 

class Rating(BaseModel):
    value:float
    count:int
    review_count:int

class Price(BaseModel):
    price:float
    currency:str

class Provider(BaseModel):
    name:str
    product_rating:float
    service_rating:float
    experience:str

class Product(BaseModel):
    brand:str
    name:str
    description:str
    image:list
    rating:Rating
    price:Price
    provider:Provider
    highlights:dict
    policy:str
    manufacturer_info:str
    

json_file='flipkart_data.json'
with open(json_file,'r',encoding='utf-8') as f:
    data=json.load(f)

general_specs = {}

path_0 = data["multiWidgetState"]["widgetsData"]["slots"]

try:
    grid_data = []
    
    for slot in path_0:
        try:
            if "slotData" in slot and "widget" in slot["slotData"] and "data" in slot["slotData"]["widget"]:
                dlsData = slot["slotData"]["widget"]["data"]["dlsData"]
                
                if "product-details-grid_0" in dlsData:
                    grid_data = dlsData["product-details-grid_0"]["value"]["gridData_0"]["value"]
                    break
                
        except (Exception):
            print(f"Error processing slot: {slot.get('slotId', 'Unknown Slot')}")
            continue
    
    if grid_data:
        for item in grid_data:
            item_value = item["value"]
            
            if "label_0" in item_value and "label_1" in item_value:
                key = item_value["label_0"]["value"]["text"]
                value = item_value["label_1"]["value"]["text"]
                
                if len(value) > 0:
                    value = value[0]
                
                general_specs[key] = value
    
except Exception as e:
    print(f"Error extracting specifications: {e}")
    print("general_specs will be empty")


product_path=data['multiWidgetState']['pageDataResponse']['seoData']['schema']

products_data = []

for item in product_path:
    brand = item['brand']['name']
    name = item['name']
    description = item['description']
    image = item['image']
    rating_path = item['aggregateRating']
    
    rating_data = Rating(
         value=rating_path['ratingValue'],
         count=rating_path['ratingCount'],
         review_count=rating_path['reviewCount']
    ) 

    price_path = item['offers']
    price_data = Price(
         price=price_path['price'],
         currency=price_path['priceCurrency']
    )
    
    experience = "Not Available"
    service_rating = 0
    fulfilled_by = "Not Available"
    
    try:
        path_1 = None
        slots = data['multiWidgetState']['widgetsData']['slots']
        
        for slot in slots:
            try:
                if "slotData" in slot and "widget" in slot["slotData"] and "data" in slot["slotData"]["widget"]:
                    dlsData = slot["slotData"]["widget"]["data"]["dlsData"]
                    
                    if "default_fk_pp_delivery_widget_seller_2" in dlsData:
                        path_1 = dlsData
                        break
            except (Exception):
                continue
        
        if path_1 is None:
            raise Exception("Could not find seller details widget")
        
        path_2 = path_1['default_fk_pp_delivery_widget_seller_2']['value']
        fulfilled_by = path_2['label_0']['value']['text']
        
        service_rating = float(path_2['label_1']['value']['text'])
        
        experience = path_2['label_3']['value']['text']
        
    except Exception as e:
        print(f"Could not extract seller details: {e}")
        fulfilled_by = "Unknown Seller"
        experience = "Not Available"
        service_rating = 0
    
    highlights = {}
    highlights.update(general_specs)
    try:
        policy = item['offers']['hasMerchantReturnPolicy']['description']
    except (KeyError, TypeError):
        policy = "Policy not available"
    
    manufacturer_info = brand
    
    provider_data = Provider(
         name=fulfilled_by,
         product_rating=rating_data.value,
         service_rating=service_rating,
         experience=experience
    )
    
    product_dict = Product(
         brand=brand,
         name=name,
         description=description,
         image=image,
         rating=rating_data,
         price=price_data,
         provider=provider_data,
         highlights=highlights,
         policy=policy,
         manufacturer_info=manufacturer_info
    )
    products_data.append(product_dict)

  

with open("output_output.json", "w", encoding="utf-8") as f:
    json.dump([i.model_dump() for i in products_data], f, ensure_ascii=False, indent=4)





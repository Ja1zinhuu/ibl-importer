import pymongo

def get_db():
    """
    Connect to MongoDB and return the database object.
    """
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['3DLib']
    return client, db  # Return both the client and db objects

def hdriTypes(): # This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL HDRI TYPES
    """
    Get distinct HDRI types and close the connection.
    """
    client, db = get_db()  # Get both client and db
    try:
        collection = db['HDRIs']
        distinct_types = collection.distinct('type')
        return distinct_types
    finally:
        client.close()  # Close the connection

def lgtMapTypes(): #This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL LIGHTMAP TYPES
    """
    Get distinct Lightmap types and close the connection.
    """
    client, db = get_db()  # Get both client and db
    try:
        collection = db['Lightmaps']
        distinct_types = collection.distinct('type')
        return distinct_types
    finally:
        client.close()  # Close the connection

def lgtMaps_and_hdris_types(): #This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL LIGHTMAP AND HDRI TYPES
    """
    Get distinct types for both HDRIs and Lightmaps, and close the connection.
    """
    client, db = get_db()  # Get both client and db
    try:
        collection1 = db['HDRIs']
        collection2 = db['Lightmaps']
        collection1 = collection1.distinct('type')
        collection2 = collection2.distinct('type')
        all_types = []
        for i in collection1:
            type = f"HDRI {i}"
            all_types.append(type)
        for i in collection2:
            type = f"Lightmap {i}"
            all_types.append(type)
        return all_types
    finally:
        client.close()  # Close the connection

def get_items_from_type(type, col_to_query): #This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL ITEMS OF A CERTAIN TYPE


    if col_to_query == "HDRIs":
        collection = "HDRIs"
    elif col_to_query == "Lightmaps": 
        collection = "Lightmaps"
    elif col_to_query == "All":
        collection1 = "HDRIs"
        collection2 = "Lightmaps"
    client, db = get_db()  # Get both client and db
    
    try:
        if col_to_query == "All":
            typeParts = type.split(" ")
            print (typeParts)
            type = typeParts[1]
            collection1 = db[collection1]
            collection2 = db[collection2]
            items1 = collection1.find({'type': type})
            items2 = collection2.find({'type': type})
            items = []
            for i in items1:
                items.append(i['name'])
            for i in items2:
                items.append(i['name'])
            return items
        
        else:
            collection = db[collection]
            items = collection.find({'type': type})
            items_list = []
            for i in items:
                items_list.append(i['name'])
            return items_list
    finally:
        client.close()  # Close the connection

def get_item_info(item, col_to_query): #This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL INFO OF A CERTAIN ITEM
    """
    Get all information for a specific item.
    """
    if col_to_query == "HDRIs":
        collection = "HDRIs"
    elif col_to_query == "Lightmaps": 
        collection = "Lightmaps"
    elif col_to_query == "All":
        collection1 = "HDRIs"
        collection2 = "Lightmaps" 
        
    client, db = get_db()  # Get both client and db
    try:
        if col_to_query == "All":
            collection1 = db[collection1]
            collection2 = db[collection2]
            item1 = collection1.find_one({'name': item})
            item2 = collection2.find_one({'name': item})
            if item1:
                return item1
            else:
                return item2
        else:
            collection = db[collection]
            item = collection.find_one({'name': item})
            return item
    finally:
        client.close()  # Close the connection

def get_item_from_id(id, col_to_query): #This function is called from run_iblImporter_maya.py, QUERIES THE DATABASE FOR ALL INFO OF A CERTAIN ITEM
    """
    Get all information for a specific item.
    """
    if col_to_query == "HDRIs":
        collection = "HDRIs"
    elif col_to_query == "Lightmaps": 
        collection = "Lightmaps"
    elif col_to_query == "All":
        collection1 = "HDRIs"
        collection2 = "Lightmaps" 
        
    client, db = get_db()  # Get both client and db
    try:
        if col_to_query == "All":
            collection1 = db[collection1]
            collection2 = db[collection2]
            item1 = collection1.find_one({'_id': id})
            item2 = collection2.find_one({'_id': id})
            if item1:
                return item1
            else:
                return item2
        else:
            collection = db[collection]
            item = collection.find_one({'_id': id})
            return item
    finally:
        client.close()  # Close the connection
    

def get_items_from_name(name, col_to_query):
    """
    Get all information for a specific item.
    """
    if col_to_query == "HDRIs":
        collection = "HDRIs"
    elif col_to_query == "Lightmaps": 
        collection = "Lightmaps"
    elif col_to_query == "All":
        collection1 = "HDRIs"
        collection2 = "Lightmaps" 
        
    client, db = get_db()  # Get both client and db
    try:
        if col_to_query == "All":
            collection1 = db[collection1]
            collection2 = db[collection2]
            item1 = collection1.find_one({'name': name})
            item2 = collection2.find_one({'name': name})
            if item1:
                return item1
            else:
                return item2
        else:
            collection = db[collection]
            item = collection.find_one({'name': name})
            return item
    finally:
        client.close()  # Close the connection
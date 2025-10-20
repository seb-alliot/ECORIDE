def increment_vue(db, trajet_id):
    vue_collection = db["vue"]
    compteur_vue = vue_collection.find_one({"_id": trajet_id})
    if compteur_vue:
        vue_collection.update_one({"_id": trajet_id}, {"$inc": {"compteur": 1}})
    else:
        vue_collection.insert_one({"_id": trajet_id, "compteur": 1})
    return vue_collection.find_one({"_id": trajet_id})["compteur"]

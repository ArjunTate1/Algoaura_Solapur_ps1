from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017")
db = client["smart_road_db"]
collection = db["pothole_reports"]


def save_pothole_report(result):
    inserted = collection.insert_one(result)
    result["_id"] = str(inserted.inserted_id)
    return result


def get_all_potholes():
    potholes = list(collection.find({}))
    for p in potholes:
        p["_id"] = str(p["_id"])
        # Ensure these fields always exist
        p["latitude"]  = p.get("latitude")
        p["longitude"] = p.get("longitude")
    return potholes



def get_user(username, password):
    user = db["users"].find_one({"username": username, "password": password})
    if user:
        user["_id"] = str(user["_id"])
        return user
    return None

def create_user(username, password, role):
    existing = db["users"].find_one({"username": username})
    if existing:
        return None
    result = db["users"].insert_one({
        "username": username,
        "password": password,
        "role": role
    })
    return str(result.inserted_id)



def assign_to_contractor(pothole_id, contractor):
    collection.update_one(
        {"_id": ObjectId(pothole_id)},
        {"$set": {"assigned_to": contractor, "status": "review"}}
    )
    return {"message": "Assigned successfully"}

def get_users_by_role(role):
    users = list(db["users"].find({"role": role}))
    for u in users:
        u["_id"] = str(u["_id"])
    return users


def get_assigned_potholes(contractor):
    potholes = list(collection.find({"assigned_to": contractor}))
    for p in potholes:
        p["_id"] = str(p["_id"])
    return potholes

def mark_resolved(pothole_id):
    collection.update_one(
        {"_id": ObjectId(pothole_id)},
        {"$set": {"status": "resolved"}}
    )
    return {"message": "Marked as resolved"}




def get_forum_posts():
    posts = list(db["forum_posts"].find({}).sort("pinned", -1))
    for p in posts:
        p["_id"] = str(p["_id"])
    return posts

def create_forum_post(username, title, body):
    result = db["forum_posts"].insert_one({
        "username": username,
        "title": title,
        "body": body,
        "upvotes": 0,
        "upvoted_by": [],
        "pinned": False,
        "deleted": False,
        "comments": [],
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })
    return str(result.inserted_id)

def add_comment(post_id, username, comment):
    db["forum_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": {
            "id": str(__import__('uuid').uuid4()),
            "username": username,
            "comment": comment,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }}}
    )
    return {"message": "Comment added"}

def upvote_post(post_id, username):
    post = db["forum_posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        return {"error": "Post not found"}
    if username in post.get("upvoted_by", []):
        db["forum_posts"].update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"upvotes": -1}, "$pull": {"upvoted_by": username}}
        )
        return {"message": "Upvote removed"}
    db["forum_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"upvotes": 1}, "$push": {"upvoted_by": username}}
    )
    return {"message": "Upvoted"}

def pin_post(post_id, pinned):
    db["forum_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"pinned": pinned}}
    )
    return {"message": "Updated"}

def delete_post(post_id):
    db["forum_posts"].update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"deleted": True}}
    )
    return {"message": "Deleted"}



def get_potholes_with_priority():
    potholes = list(collection.find({}))
    for p in potholes:
        p["_id"] = str(p["_id"])

    # Get max values for normalization
    max_count        = max((p.get("pothole_count", 0)  for p in potholes), default=1)
    max_area         = max(
        (p["potholes"][0].get("area_m2", 0) for p in potholes if p.get("potholes")),
        default=1
    )
    max_report_count = max((p.get("report_count", 1)   for p in potholes), default=1)

    for p in potholes:
        count        = p.get("pothole_count", 0)
        area         = p["potholes"][0].get("area_m2", 0) if p.get("potholes") else 0
        report_count = p.get("report_count", 1)

        # Normalize each factor 0→1
        norm_count        = count        / max_count        if max_count        else 0
        norm_area         = area         / max_area         if max_area         else 0
        norm_report_count = report_count / max_report_count if max_report_count else 0

        # Z-score: 30% pothole count + 40% area/dimension + 30% report frequency
        z_score = round(
            0.30 * norm_count +
            0.40 * norm_area  +
            0.30 * norm_report_count,
            4
        )
        p["z_score"]      = z_score
        p["report_count"] = report_count

        if   z_score >= 0.7: p["priority"] = "critical"
        elif z_score >= 0.4: p["priority"] = "high"
        elif z_score >= 0.2: p["priority"] = "medium"
        else:                p["priority"] = "low"

    potholes.sort(key=lambda p: p["z_score"], reverse=True)
    return potholes



def save_pothole_report(result):
    lat = result.get("latitude")
    lng = result.get("longitude")

    # Check if report already exists at same location (within ~50m)
    if lat and lng:
        lat_f = float(lat)
        lng_f = float(lng)

        # Search within small coordinate range (~50 metres)
        delta = 0.0005
        existing = collection.find_one({
            "latitude":  {"$gte": str(lat_f - delta), "$lte": str(lat_f + delta)},
            "longitude": {"$gte": str(lng_f - delta), "$lte": str(lng_f + delta)}
        })

        if existing:
            # Merge — increment report_count and update pothole data
            new_count    = existing.get("pothole_count", 0) + result.get("pothole_count", 0)
            report_count = existing.get("report_count", 1) + 1

            # Keep highest area pothole
            existing_area = existing["potholes"][0].get("area_m2", 0) if existing.get("potholes") else 0
            new_area      = result["potholes"][0].get("area_m2", 0)   if result.get("potholes")   else 0
            best_potholes = result["potholes"] if new_area > existing_area else existing["potholes"]

            collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "pothole_count":  new_count,
                    "report_count":   report_count,
                    "potholes":       best_potholes,
                    "timestamp":      result.get("time", existing.get("timestamp")),
                    "original_img":   result.get("original_img")  or existing.get("original_img"),
                    "processed_img":  result.get("processed_img") or existing.get("processed_img"),
                }}
            )
            existing["_id"] = str(existing["_id"])
            return existing

    # No duplicate — insert new
    result["report_count"] = 1
    inserted = collection.insert_one(result)
    result["_id"] = str(inserted.inserted_id)
    return result


def get_all_potholes():
    potholes = list(collection.find({}))
    for p in potholes:
        p["_id"] = str(p["_id"])
    return potholes
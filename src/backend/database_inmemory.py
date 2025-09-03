"""
In-memory database simulation for development and testing purposes.
This replaces MongoDB with simple dictionaries to avoid database setup complexity.
"""

from argon2 import PasswordHasher

# In-memory storage
activities_data = {}
teachers_data = {}

class MockCollection:
    def __init__(self, data_store):
        self.data_store = data_store
    
    def find(self, query=None):
        """Return all items as MongoDB would, with _id as key"""
        if not query:
            for key, value in self.data_store.items():
                yield {"_id": key, **value}
        else:
            # Simple query support for the filters we need
            for key, value in self.data_store.items():
                if self._matches_query({"_id": key, **value}, query):
                    yield {"_id": key, **value}
    
    def find_one(self, query):
        """Find single document"""
        if isinstance(query, dict) and "_id" in query:
            key = query["_id"]
            if key in self.data_store:
                return {"_id": key, **self.data_store[key]}
        return None
    
    def count_documents(self, query):
        """Count matching documents"""
        return len(list(self.find(query)))
    
    def insert_one(self, doc):
        """Insert a document"""
        doc_id = doc.pop("_id")
        self.data_store[doc_id] = doc
        return type('InsertResult', (), {'inserted_id': doc_id})()
    
    def update_one(self, query, update):
        """Update a document"""
        if isinstance(query, dict) and "_id" in query:
            key = query["_id"]
            if key in self.data_store:
                if "$push" in update:
                    for field, value in update["$push"].items():
                        if field in self.data_store[key]:
                            self.data_store[key][field].append(value)
                        else:
                            self.data_store[key][field] = [value]
                if "$pull" in update:
                    for field, value in update["$pull"].items():
                        if field in self.data_store[key]:
                            if value in self.data_store[key][field]:
                                self.data_store[key][field].remove(value)
                return type('UpdateResult', (), {'modified_count': 1})()
        return type('UpdateResult', (), {'modified_count': 0})()
    
    def aggregate(self, pipeline):
        """Simple aggregation for getting unique days"""
        # This is a simplified implementation for the specific aggregation used
        if len(pipeline) >= 2 and "$unwind" in pipeline[0] and "$group" in pipeline[1]:
            days = set()
            for key, value in self.data_store.items():
                if "schedule_details" in value and "days" in value["schedule_details"]:
                    for day in value["schedule_details"]["days"]:
                        days.add(day)
            return [{"_id": day} for day in sorted(days)]
        return []
    
    def _matches_query(self, doc, query):
        """Simple query matching for basic filters"""
        for key, condition in query.items():
            if key == "schedule_details.days" and isinstance(condition, dict) and "$in" in condition:
                if "schedule_details" not in doc or "days" not in doc["schedule_details"]:
                    return False
                if not any(day in doc["schedule_details"]["days"] for day in condition["$in"]):
                    return False
            elif key == "schedule_details.start_time" and isinstance(condition, dict):
                if "schedule_details" not in doc or "start_time" not in doc["schedule_details"]:
                    return False
                if "$gte" in condition:
                    if doc["schedule_details"]["start_time"] < condition["$gte"]:
                        return False
            elif key == "schedule_details.end_time" and isinstance(condition, dict):
                if "schedule_details" not in doc or "end_time" not in doc["schedule_details"]:
                    return False
                if "$lte" in condition:
                    if doc["schedule_details"]["end_time"] > condition["$lte"]:
                        return False
            elif key == "difficulty" and isinstance(condition, dict):
                if "$exists" in condition:
                    has_difficulty = "difficulty" in doc
                    if condition["$exists"] != has_difficulty:
                        return False
                elif condition == doc.get("difficulty"):
                    continue
                elif doc.get("difficulty") != condition:
                    return False
            elif key in doc:
                if doc[key] != condition:
                    return False
            else:
                return False
        return True

# Create mock collections
activities_collection = MockCollection(activities_data)
teachers_collection = MockCollection(teachers_data)

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""
    
    # Initialize activities if empty
    if len(activities_data) == 0:
        for name, details in initial_activities.items():
            activities_data[name] = details
            
    # Initialize teacher accounts if empty
    if len(teachers_data) == 0:
        for teacher in initial_teachers:
            teachers_data[teacher["username"]] = {k: v for k, v in teacher.items() if k != "username"}

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "difficulty": "Beginner",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "difficulty": "Intermediate",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "difficulty": "Advanced",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "difficulty": "Beginner",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "difficulty": "Intermediate",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "difficulty": "Advanced",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "difficulty": "Advanced",
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "difficulty": "Intermediate",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "difficulty": "Advanced",
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Join fellow otaku to explore the captivating universe of Japanese manga! From epic shounen adventures to heartwarming slice-of-life stories, discover amazing characters, share your favorite series, and dive deep into the art of storytelling.",
        "schedule": "Tuesdays at 7:00 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:00"
        },
        "max_participants": 15,
        "participants": []
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]
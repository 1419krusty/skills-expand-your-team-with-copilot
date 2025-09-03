"""
Mock database implementation for testing without MongoDB
"""

from argon2 import PasswordHasher

# Mock MongoDB collections as dictionaries
activities_data = {}
teachers_data = {}

class MockCollection:
    def __init__(self, data_dict):
        self.data = data_dict
    
    def count_documents(self, query):
        return len(self.data)
    
    def insert_one(self, document):
        _id = document.get('_id')
        self.data[_id] = document
    
    def find_one(self, query):
        if '_id' in query:
            return self.data.get(query['_id'])
        return None
    
    def find(self, query=None):
        if not query:
            return [{'_id': key, **value} for key, value in self.data.items()]
        
        # Handle day filter
        if 'schedule_details.days' in query:
            target_days = query['schedule_details.days'].get('$in', [])
            result = []
            for key, doc in self.data.items():
                if 'schedule_details' in doc:
                    doc_days = doc['schedule_details'].get('days', [])
                    if any(day in doc_days for day in target_days):
                        result.append({'_id': key, **doc})
            return result
        
        # Handle time filters
        result = []
        for key, doc in self.data.items():
            include = True
            
            if 'schedule_details.start_time' in query:
                start_filter = query['schedule_details.start_time'].get('$gte')
                if start_filter and 'schedule_details' in doc:
                    doc_start = doc['schedule_details'].get('start_time', '')
                    if doc_start < start_filter:
                        include = False
            
            if 'schedule_details.end_time' in query:
                end_filter = query['schedule_details.end_time'].get('$lte')
                if end_filter and 'schedule_details' in doc:
                    doc_end = doc['schedule_details'].get('end_time', '')
                    if doc_end > end_filter:
                        include = False
            
            if include:
                result.append({'_id': key, **doc})
        
        return result
    
    def update_one(self, query, update):
        if '_id' in query:
            doc_id = query['_id']
            if doc_id in self.data:
                if '$push' in update:
                    for field, value in update['$push'].items():
                        if field not in self.data[doc_id]:
                            self.data[doc_id][field] = []
                        self.data[doc_id][field].append(value)
                if '$pull' in update:
                    for field, value in update['$pull'].items():
                        if field in self.data[doc_id] and isinstance(self.data[doc_id][field], list):
                            if value in self.data[doc_id][field]:
                                self.data[doc_id][field].remove(value)
                return type('Result', (), {'modified_count': 1})()
        return type('Result', (), {'modified_count': 0})()
    
    def aggregate(self, pipeline):
        # Mock aggregation for days
        days = set()
        for doc in self.data.values():
            if 'schedule_details' in doc and 'days' in doc['schedule_details']:
                days.update(doc['schedule_details']['days'])
        
        return [{'_id': day} for day in sorted(days)]

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
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

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
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Explore the fantastic stories of the most interesting characters from Japanese Manga (graphic novels).",
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
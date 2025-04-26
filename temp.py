import json

# Example JSON array
data = [
    {
        "text": "You are developing a new application on a VM that is on your corporate network. The application will use Java Database Connectivity (JDBC) to connect to Cloud SQL for PostgreSQL. Your Cloud SQL instance is configured with IP address 192.168.3.48, and SSL is disabled. You want to ensure that your application can access your database instance without requiring configuration changes to your database. What should you do?",
        "examId": "professional-cloud-architect",
        "id": "",
        "options": [
            {
                "id": "A",
                "isCorrect": False,
                "text": "Define a connection string using your Google username and password to point to the external (public) IP address of your Cloud SQL instance."
            },
            {
                "id": "B",
                "isCorrect": False,
                "text": "Define a connection string using a database username and password to point to the internal (private) IP address of your Cloud SQL instance."
            },
            {
                "id": "C",
                "isCorrect": True,
                "text": "Define a connection string using Cloud SQL Auth proxy configured with a service account to point to the internal (private) IP address of your Cloud SQL instance."
            },
            {
                "id": "D",
                "isCorrect": False,
                "text": "Define a connection string using Cloud SQL Auth proxy configured with a service account to point to the external (public) IP address of your Cloud SQL instance."
            }
        ],
        "explanation": ""
    }
]

# Updating the examId
for item in data:
    if item.get("examId") == "professional-cloud-architect":
        item["examId"] = "professional-cloud-database-engineer"

# Pretty-print the updated JSON
print(json.dumps(data, indent=4))

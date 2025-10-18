"""
Test script for Resume Analyzer API
Run this after starting the backend server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if API is running"""
    print("\n=== Testing API Health ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_create_user():
    """Test user creation"""
    print("\n=== Testing User Creation ===")
    user_data = {
        "username": "test_user",
        "email": "test@example.com"
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        user = response.json()
        print(f"Created user: {json.dumps(user, indent=2)}")
        return user['id']
    elif response.status_code == 400:
        print("User already exists, fetching existing user...")
        # Get existing user
        response = requests.get(f"{BASE_URL}/users/")
        users = response.json()
        for user in users:
            if user['email'] == user_data['email']:
                return user['id']
    return None

def test_upload_resume(user_id):
    """Test resume upload"""
    print("\n=== Testing Resume Upload ===")
    resume_text = """
John Doe
Software Engineer
Email: john@example.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Software engineer with experience in web development.

WORK EXPERIENCE
Software Developer - ABC Company
Jan 2020 - Present
- Worked on various projects
- Fixed bugs
- Attended meetings

Junior Developer - XYZ Corp
Jun 2018 - Dec 2019
- Helped with coding tasks
- Learned new technologies

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2018

SKILLS
Python, JavaScript, HTML, CSS
    """
   
    params = {"user_id": user_id}
    data = {"text": resume_text}
   
    response = requests.post(
        f"{BASE_URL}/resumes/upload",
        params=params,
        json=data
    )
   
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        resume = response.json()
        print(f"Uploaded resume ID: {resume['id']}")
        print(f"Original text length: {len(resume['original_text'])} characters")
        return resume['id']
    else:
        print(f"Error: {response.text}")
    return None

def test_improve_resume(resume_id):
    """Test resume improvement"""
    print("\n=== Testing Resume Improvement ===")
    print("This may take 30-60 seconds as the LLM processes the resume...")
   
    improvement_data = {
        "improvement_focus": "technical",
        "job_description": """
We are seeking a Python Developer with experience in FastAPI and modern web development.
The ideal candidate should have:
- 2+ years of Python development experience
- Experience with FastAPI or similar frameworks
- Knowledge of PostgreSQL and database design
- Understanding of RESTful API design
- Experience with Git and version control
        """
    }
   
    response = requests.post(
        f"{BASE_URL}/resumes/{resume_id}/improve",
        json=improvement_data,
        timeout=120
    )
   
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nImprovement complete!")
        print(f"\n=== IMPROVED RESUME ===")
        print(result['improved_text'][:500] + "..." if len(result['improved_text']) > 500 else result['improved_text'])
        print(f"\nFull length: {len(result['improved_text'])} characters")
    else:
        print(f"Error: {response.text}")

def test_get_resume(resume_id):
    """Test getting resume"""
    print("\n=== Testing Get Resume ===")
    response = requests.get(f"{BASE_URL}/resumes/{resume_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        resume = response.json()
        print(f"Resume ID: {resume['id']}")
        print(f"Has improved text: {resume['improved_text'] is not None}")
    else:
        print(f"Error: {response.text}")

def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("RESUME ANALYZER API TESTS")
    print("=" * 60)
   
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not running! Please start the backend server.")
        return
   
    # Test 2: Create user
    user_id = test_create_user()
    if not user_id:
        print("\n❌ Failed to create user")
        return
   
    # Test 3: Upload resume
    resume_id = test_upload_resume(user_id)
    if not resume_id:
        print("\n❌ Failed to upload resume")
        return
   
    # Test 4: Improve resume
    test_improve_resume(resume_id)
   
    # Test 5: Get resume
    test_get_resume(resume_id)
   
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    print(f"\nYou can view the full API documentation at: {BASE_URL}/docs")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to the API!")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
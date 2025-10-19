Testing Django REST API with Postman
This guide provides step-by-step instructions for testing the Django REST API endpoints using Postman. The API includes user registration, login, logout, profile management, password change, and token refresh functionalities. Each endpoint will be tested with appropriate HTTP methods, headers, and request bodies.
Prerequisites

Postman: Ensure Postman is installed (download from Postman).
API Server: The Django server must be running locally (e.g., http://127.0.0.1:8000) or on a hosted environment.
Base URL: Replace http://127.0.0.1:8000/api/ with your actual API base URL if different.
Environment Setup: Create a Postman environment with variables:
base_url: http://127.0.0.1:8000/api/
access_token: (to store the JWT access token)
refresh_token: (to store the JWT refresh token)



EndPOINTS Overview
The API has the following endpoints:

POST /register/: Register a new user.
POST /login/: Authenticate and log in a user.
POST /logout/: Log out a user by blacklisting the refresh token.
GET /profile/: Retrieve the authenticated user's profile.
PUT /profile/: Update the authenticated user's profile.
PUT /change-password/: Change the authenticated user's password.
POST /token/refresh/: Refresh the JWT access token.

Testing Each Endpoint
1. Register a New User
Endpoint: POST {{base_url}}register/Description: Creates a new user account.Request:

Method: POST
URL: {{base_url}}register/
Headers:
Content-Type: application/json


Body (raw, JSON):{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "TestPassword123!",
  "password_confirm": "TestPassword123!",
  "first_name": "Test",
  "last_name": "User"
}



Expected Response:

Status: 201 Created
Body:{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com",
    "first_name": "Test",
    "last_name": "User",
    "full_name": "Test User",
    "avatar": null,
    "bio": "",
    "created_at": "2025-10-07T17:43:00Z",
    "updated_at": "2025-10-07T17:43:00Z",
    "posts_count": 0,
    "comments_count": 0
  },
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "message": "User registered successfully"
}



Postman Script (in Tests tab):
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});
pm.test("Response contains user and tokens", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('user');
    pm.expect(jsonData).to.have.property('refresh');
    pm.expect(jsonData).to.have.property('access');
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
});

Notes:

Save the access_token and refresh_token to Postman environment variables for later use.
If the email already exists, expect a 400 Bad Request with an error message.

2. Login
Endpoint: POST {{base_url}}login/Description: Authenticates a user and returns JWT tokens.Request:

Method: POST
URL: {{base_url}}login/
Headers:
Content-Type: application/json


Body (raw, JSON):{
  "email": "testuser@example.com",
  "password": "TestPassword123!"
}



Expected Response:

Status: 200 OK
Body:{
  "user": {
    "email": "testuser@example.com",
    "password": "<hidden>"
  },
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "message": "User registered successfully"
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains user and tokens", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('user');
    pm.expect(jsonData).to.have.property('refresh');
    pm.expect(jsonData).to.have.property('access');
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
});

Notes:

Update the access_token and refresh_token in the Postman environment.
If credentials are incorrect, expect a 400 Bad Request with an error message like "User not found." or "Account is banned.".

3. Logout
Endpoint: POST {{base_url}}logout/Description: Logs out the user by blacklisting the refresh token.Request:

Method: POST
URL: {{base_url}}logout/
Headers:
Content-Type: application/json
Authorization: Bearer {{access_token}}


Body (raw, JSON):{
  "refresh_token": "{{refresh_token}}"
}



Expected Response:

Status: 200 OK
Body:{
  "message": "Logout successful"
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains success message", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Logout successful");
});

Notes:

Requires a valid access_token for authentication.
If the refresh token is invalid, expect a 400 Bad Request with an error message.

4. Get User Profile
Endpoint: GET {{base_url}}profile/Description: Retrieves the authenticated user's profile details.Request:

Method: GET
URL: {{base_url}}profile/
Headers:
Authorization: Bearer {{access_token}}Expected Response:


Status: 200 OK
Body:{
  "id": 1,
  "username": "testuser",
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "full_name": "Test User",
  "avatar": null,
  "bio": "",
  "created_at": "2025-10-07T17:43:00Z",
  "updated_at": "2025-10-07T17:43:00Z",
  "posts_count": 0,
  "comments_count": 0
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains user profile", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('email');
    pm.expect(jsonData).to.have.property('full_name');
});

Notes:

Requires a valid access_token.
If unauthorized, expect a 401 Unauthorized response.

5. Update User Profile
Endpoint: PUT {{base_url}}profile/Description: Updates the authenticated user's profile details.Request:

Method: PUT
URL: {{base_url}}profile/
Headers:
Content-Type: application/json
Authorization: Bearer {{access_token}}


Body (raw, JSON):{
  "first_name": "Updated",
  "last_name": "User",
  "bio": "This is an updated bio."
}



Expected Response:

Status: 200 OK
Body:{
  "first_name": "Updated",
  "last_name": "User",
  "avatar": null,
  "bio": "This is an updated bio."
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains updated fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.first_name).to.eql("Updated");
    pm.expect(jsonData.bio).to.eql("This is an updated bio.");
});

Notes:

Requires a valid access_token.
The avatar field can be updated if a file upload is supported (configure Postman to send multipart/form-data if needed).
If unauthorized, expect a 401 Unauthorized response.

6. Change Password
Endpoint: PUT {{base_url}}change-password/Description: Changes the authenticated user's password.Request:

Method: PUT
URL: {{base_url}}change-password/
Headers:
Content-Type: application/json
Authorization: Bearer {{access_token}}


Body (raw, JSON):{
  "old_password": "TestPassword123!",
  "new_password": "NewPassword123!",
  "new_password_confirm": "NewPassword123!"
}



Expected Response:

Status: 200 OK
Body:{
  "message": "Password changed successfully"
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains success message", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Password changed successfully");
});

Notes:

Requires a valid access_token.
If the old password is incorrect or new passwords don't match, expect a 400 Bad Request with an error message.
After changing the password, the user must log in again to obtain new tokens.

7. Refresh Token
Endpoint: POST {{base_url}}token/refresh/Description: Refreshes the JWT access token using the refresh token.Request:

Method: POST
URL: {{base_url}}token/refresh/
Headers:
Content-Type: application/json


Body (raw, JSON):{
  "refresh": "{{refresh_token}}"
}



Expected Response:

Status: 200 OK
Body:{
  "access": "<new_access_token>",
  "refresh": "<new_refresh_token>"
}



Postman Script (in Tests tab):
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
pm.test("Response contains new access token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.environment.set("access_token", jsonData.access);
});

Notes:

Use the refresh_token saved from login or registration.
Update the access_token in the Postman environment.
If the refresh token is invalid, expect a 401 Unauthorized or 400 Bad Request.

Testing Workflow

Register a user: Send a POST request to /register/ to create a user and obtain initial tokens.
Login: Test login with the same credentials to verify authentication and token generation.
Get Profile: Use the access_token to retrieve the user's profile.
Update Profile: Update profile details using a PUT request.
Change Password: Change the user's password and verify by logging in with the new password.
Refresh Token: Use the refresh token to obtain a new access token.
Logout: Blacklist the refresh token to log out the user.
Error Cases: Test edge cases, such as:
Registering with an existing email (expect 400 Bad Request).
Logging in with incorrect credentials (expect 400 Bad Request).
Accessing protected endpoints without a token (expect 401 Unauthorized).



Tips for Efficient Testing

Collection: Create a Postman collection to organize all requests.
Environment Variables: Use access_token and refresh_token variables to avoid manual token copying.
Tests: Add test scripts to automate response validation and token storage.
Pre-request Scripts: Automate setting the Authorization header:pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer {{access_token}}'
});


File Uploads: For the avatar field, configure Postman to send multipart/form-data if testing file uploads.

Troubleshooting

401 Unauthorized: Ensure the access_token is valid and included in the Authorization header.
400 Bad Request: Check the request body for missing or incorrect fields.
500 Internal Server Error: Verify the Django server is running and the database is migrated (python manage.py migrate).
Token Issues: Ensure the rest_framework_simplejwt package is installed and configured correctly in Django settings.








{
  "info": {
    "name": "Main App API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Categories",
      "item": [
        {
          "name": "Get All Categories",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/categories/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "categories", ""]
            }
          },
          "response": []
        },
        {
          "name": "Create Category (Authenticated)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"name\": \"Test Category\", \"description\": \"Test category description\"}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/categories/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "categories", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get Category by Slug",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/categories/test-category/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "categories", "test-category", ""]
            }
          },
          "response": []
        },
        {
          "name": "Update Category (Authenticated)",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"name\": \"Updated Category\", \"description\": \"Updated description\"}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/categories/test-category/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "categories", "test-category", ""]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Posts",
      "item": [
        {
          "name": "Get All Posts",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", ""]
            }
          },
          "response": []
        },
        {
          "name": "Create Post (Authenticated)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"title\": \"Test Post\", \"content\": \"This is a test post content\", \"category\": 1, \"status\": \"published\"}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get Post by Slug",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/test-post/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "test-post", ""]
            }
          },
          "response": []
        },
        {
          "name": "Update Post (Author Only)",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\"title\": \"Updated Post\", \"content\": \"Updated content\", \"category\": 1, \"status\": \"published\"}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/test-post/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "test-post", ""]
            }
          },
          "response": []
        },
        {
          "name": "Delete Post (Author Only)",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/test-post/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "test-post", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get My Posts (Authenticated)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/my-posts/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "my-posts", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get Popular Posts",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/popular/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "popular", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get Recent Posts",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/recent/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "recent", ""]
            }
          },
          "response": []
        },
        {
          "name": "Get Posts by Category",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/v1/posts/categories/test-category/posts/",
              "host": ["{{baseUrl}}"],
              "path": ["api", "v1", "posts", "categories", "test-category", "posts", ""]
            }
          },
          "response": []
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    },
    {
      "key": "access_token",
      "value": "your_jwt_token_here"
    }
  ]
}
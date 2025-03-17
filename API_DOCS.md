### User Management APIs
```
GET /api/v1/users - Get all users
GET /api/v1/users/{user_id} - Get user details
PUT /api/v1/users/{user_id} - Update user information
DELETE /api/v1/users/{user_id} - Delete user
GET /api/v1/users/me - Get current logged-in user information
PUT /api/v1/users/me - Update current user information
PUT /api/v1/users/{user_id}/status - Enable/disable user
```

### Permission Management APIs
```
GET /api/v1/rbac/users/{user_id}/permissions - Get all permissions for a user
GET /api/v1/rbac/users/{user_id}/roles - Get all roles for a user
```

### System Management APIs
```
GET /api/v1/system/logs - Get system logs
```

### Authentication APIs
```
POST /api/v1/auth/login - User login
POST /api/v1/auth/register - User registration
POST /api/v1/auth/test-token - Test token validity
POST /api/v1/auth/refresh-token - Refresh access token
```

### Role Management APIs
```
GET /api/v1/rbac/roles - Get all roles
GET /api/v1/rbac/roles/{role_id} - Get role details
POST /api/v1/rbac/roles - Create new role
PUT /api/v1/rbac/roles/{role_id} - Update role
DELETE /api/v1/rbac/roles/{role_id} - Delete role
POST /api/v1/rbac/roles/{role_id}/permissions - Assign permissions to role
DELETE /api/v1/rbac/roles/{role_id}/permissions/{permission_id} - Remove permission from role
``` 
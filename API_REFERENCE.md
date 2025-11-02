# API Reference Guide

## Base URL

http://localhost:5000/api

---

## Student Endpoints

### Get All Students

**GET** `/students`

Response:

```json
{
  "success": true,
  "message": "Found 20 students",
  "data": [...]
}
```

### Get Single Student

**GET** `/students/{id}`

Response includes full profile with skills, traits, and availability.

### Create Student

**POST** `/students`

Body:

```json
{
  "student_number": "2021-12345",
  "first_name": "Juan",
  "last_name": "Dela Cruz",
  "email": "juan@tip.edu.ph",
  "gwa": 1.75,
  "year_level": 4
}
```

### Update Student

**PUT** `/students/{id}`

Body (partial update allowed):

```json
{
  "gwa": 1.5,
  "year_level": 4
}
```

### Delete Student

**DELETE** `/students/{id}`

### Add Skills to Student

**POST** `/students/{id}/skills`

Body:

```json
{
  "skills": [
    {
      "skill_name": "Python",
      "proficiency_level": "Advanced",
      "years_experience": 2.5
    }
  ]
}
```

---

## Group Endpoints

### Get All Groups

**GET** `/groups`

Returns all groups with their members.

### Get Single Group

**GET** `/groups/{id}`

Returns group details including members and tasks.

### Form Groups (Trigger Matcher Agent)

**POST** `/groups/form`

Body:

```json
{
  "target_group_size": 4,
  "algorithm": "ga",
  "clear_existing": true
}
```

Options:

- `algorithm`: "simple" or "ga"
- `clear_existing`: true/false (clear old groups first)

---

## Task Endpoints

### Get All Tasks

**GET** `/tasks?group_id=1&status=Pending`

Query parameters (optional):

- `group_id`: Filter by group
- `status`: Filter by status (Pending, In Progress, Completed, Overdue)

### Create Task

**POST** `/tasks`

Body:

```json
{
  "group_id": 1,
  "task_name": "Database Design",
  "description": "Design the database schema",
  "required_skills": "MySQL, Database Design",
  "complexity_level": "High",
  "estimated_hours": 20,
  "deadline": "2025-12-31"
}
```

### Update Task Status

**PUT** `/tasks/{id}/status`

Body:

```json
{
  "status": "Completed",
  "completion_percentage": 100
}
```

### Allocate Tasks (Trigger Coordinator Agent)

**POST** `/groups/{id}/allocate-tasks`

Runs the Coordinator Agent to assign tasks to group members.

---

## Dashboard Endpoints

### Faculty Dashboard

**GET** `/dashboard/faculty`

Returns:

- Total students, groups, tasks
- Average group compatibility
- Task distribution by status
- At-risk groups

### Student Dashboard

**GET** `/dashboard/student/{id}`

Returns:

- Student's group info
- Assigned tasks
- Group members
- Total workload hours

---

## Utility Endpoints

### Health Check

**GET** `/health`

Check if API is running.

### Root

**GET** `/`

API information and available endpoints.

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

---

## Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request
- **404** - Not Found
- **409** - Conflict (duplicate)
- **500** - Server Error

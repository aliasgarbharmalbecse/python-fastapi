User Module

database tables to be created
- users
  - id: uuid
  - firstname
  - lastname
  - email
  - phone
  - department [fk to department id]
  - role
  - is_active
  - hashed_password
  - created_at
- departments
  - id: uuid
  - department_name
  - department_head: ref users:id
  - users: relationship with users
- roles
  - admin
  - manager
  - employee
- user_roles
  - id
  - user_id
  - role_id
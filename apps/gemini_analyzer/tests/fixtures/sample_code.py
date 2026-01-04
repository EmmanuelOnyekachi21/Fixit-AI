"""Sample code snippets for testing."""

# Sample vulnerable code with SQL injection
VULNERABLE_SQL_CODE = '''
def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
'''

# Sample vulnerable code with XSS
VULNERABLE_XSS_CODE = '''
def render_comment(comment):
    return f"<div>{comment}</div>"
'''

# Sample safe code
SAFE_CODE = '''
def get_user(username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone()
'''

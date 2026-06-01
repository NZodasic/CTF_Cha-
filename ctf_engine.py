import os
import sqlite3
import json
import time

DB_PATH = "ctf_state.db"

# -------------------------------------------------------------
# 1. DATABASE & SESSION ENGINE
# -------------------------------------------------------------

def init_db():
    """Initializes the database and creates user progress table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER PRIMARY KEY,
            stage INTEGER DEFAULT 0,
            last_updated INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user_stage(user_id: int) -> int:
    """Returns the current stage level of the user. Defaults to 0."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT stage FROM user_progress WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0

def set_user_stage(user_id: int, stage: int):
    """Updates the user progress to a specific stage."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_progress (user_id, stage, last_updated)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            stage = excluded.stage,
            last_updated = excluded.last_updated
    """, (user_id, stage, int(time.time())))
    conn.commit()
    conn.close()

def reset_user(user_id: int):
    """Resets the user's progress back to stage 0."""
    set_user_stage(user_id, 0)

# -------------------------------------------------------------
# 2. STAGE 3 FILE SYSTEM MOCK
# -------------------------------------------------------------

MOCK_FILES = {
    "sys_config.bak": """[Admin]
# Administrative tokens for local API health checks
X-Admin-Auth = admin_super_secret_token_2026
system_env = production
debug_mode = true
""",
    "admin_notes.txt": """SYSTEM MAINTENANCE LOG - 2024-08-12
----------------------------------
- Standard legacy system has been deprecated.
- Core credentials migrated to a separate offline legacy channel.
- Wait, the legacy portal is still accessible using the access code.
- I hid the access code inside the system environment variables or inside the bot avatar's EXIF metadata.
- Yes, check the bot avatar JPEG metadata ('ImageDescription') inside 'avatar_source.jpg' for 'portal_key'!
- The ancient authentication command is '/legacy_portal_auth'.
""",
    "user_database.db.encrypted": """[DATABASE BACKUP - ENCRYPTED STATE]
Table: users
======================================================
id  | username   | password_hash
------------------------------------------------------
1   | root       | $2b$12$K382Akskdjf91jKASJD... (ENCRYPTED)
2   | operator   | $2b$12$92Akdjas910KjasdkL8... (ENCRYPTED)
======================================================
* Note: System Admin credentials are secure. Web endpoints are restricted to local loopback (127.0.0.1) only.
"""
}

def inspect_mock_file(filename: str):
    """
    Returns the string contents of a mock file, or a status indicator
    if it is a special binary file like the avatar.
    """
    filename = filename.strip().lower()
    if filename in ["avatar_source.jpg", "avatar_source.png", "avatar"]:
        # Indication that bot needs to send file attachment
        return {"status": "file", "path": "assets/avatar_source.jpg"}
    
    # Try finding exact or partial matches
    for k, v in MOCK_FILES.items():
        if k.lower() == filename:
            return {"status": "text", "content": v}
            
    return {"status": "error", "message": f"File '{filename}' not found in the backup catalog."}

# -------------------------------------------------------------
# 3. STAGE 4 OTP SEQUENCE MATH
# -------------------------------------------------------------

def get_otp_value(n: int = 7) -> int:
    """
    Computes T(n) = T(n-1) * 3 - T(n-2) for T(0)=2, T(1)=5.
    Expected: T(7) = 1597
    """
    if n == 0:
        return 2
    if n == 1:
        return 5
    
    a, b = 2, 5
    for _ in range(2, n + 1):
        a, b = b, b * 3 - a
    return b

# -------------------------------------------------------------
# 4. STAGE 5 MOCK SSRF ENGINE
# -------------------------------------------------------------

def mock_curl_request(url: str, headers_str: str = None) -> str:
    """
    Simulates a loopback (127.0.0.1) HTTP client inside the bot system.
    This allows players to perform Mock SSRF requests to port 8080.
    """
    url = url.strip()
    # Normalize address
    if not (url.startswith("http://127.0.0.1:8080") or url.startswith("http://localhost:8080")):
        return "[CONNECTION ERROR] Failed to connect to server: Outer internet connections are blocked for safety. Only loopback connections (http://127.0.0.1:8080) are permitted."

    path = url.replace("http://127.0.0.1:8080", "").replace("http://localhost:8080", "").strip()
    if not path or path == "/":
        return json.dumps({
            "status": "online",
            "version": "1.0.4-legacy",
            "server": "BaseHTTP/0.6 (Python 3.14)",
            "message": "Welcome to Core Control Panel API Node. Only administrative tools are allowed.",
            "endpoints": {
                "/": "Index listing",
                "/health": "Database and connection health check",
                "/debug_console": "Administrative debug console (Requires authentication token in X-Admin-Auth header)"
            }
        }, indent=4)
        
    elif path == "/health":
        return json.dumps({
            "status": "UP",
            "database": "CONNECTED",
            "uptime": "981240s",
            "load_average": "[0.02, 0.05, 0.01]"
        }, indent=4)
        
    elif path == "/debug_console":
        # Parse headers
        if not headers_str:
            return "[HTTP/1.1 401 Unauthorized]\nContent-Type: text/plain\n\nError: Unauthorized. Administrative header 'X-Admin-Auth' is missing or invalid."
            
        try:
            headers = json.loads(headers_str)
        except Exception:
            return "[HTTP/1.1 400 Bad Request]\nContent-Type: text/plain\n\nError: Invalid JSON format in headers parameter. Example: {\"X-Admin-Auth\": \"your_token_here\"}"

        # Case-insensitive header check
        admin_auth_val = None
        for k, v in headers.items():
            if k.strip().lower() == "x-admin-auth":
                admin_auth_val = v
                break
                
        if admin_auth_val == "admin_super_secret_token_2026":
            return "[HTTP/1.1 200 OK]\nContent-Type: text/plain\n\n[SUCCESS] Authorized. Operator Session Restored.\nSystem Flag Decryption Key (Base64 Encoded): Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY="
        else:
            return f"[HTTP/1.1 401 Unauthorized]\nContent-Type: text/plain\n\nError: Unauthorized. Administrative token '{admin_auth_val}' does not match key database."
            
    else:
        return f"[HTTP/1.1 404 Not Found]\nContent-Type: text/plain\n\nError: Route '{path}' not found on core API."

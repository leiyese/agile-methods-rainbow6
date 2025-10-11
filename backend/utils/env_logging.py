import os

def log_env_vars():
    
    keys = [
        "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
        "DATABASE_URL", "FRONTEND_URL", "FLASK_ENV", "RENDER",
        "EMBEDDING_MODEL", "GENERATION_MODEL", "GEMINI_API_KEY"
    ]

    print("\n=== ENVIRONMENT VARIABLES AT STARTUP (Render Debug) ===")
    for key in keys:
        value = os.environ.get(key)

        if key in ["DB_PASSWORD", "GEMINI_API_KEY"]:
            if value:
                print(f"{key}: [SET] (hidden for security)")
            else:
                print(f"{key}: [MISSING ❌]")
        elif key == "DATABASE_URL" and value:
            
            redacted = value.split("@")[-1]
            print(f"{key}: postgresql://***@{redacted}")
        else:
            print(f"{key}: {value or '[MISSING ❌]'}")
    print("==========================================================\n")



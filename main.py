import os
import psycopg

def main():
    # Read connection info from your .env
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "social")
    db_user = os.getenv("DB_USER", "admin")
    db_password = os.getenv("DB_PASSWORD", "password")

    try:
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
        )
        cur = conn.cursor()

        # Check if table "post" exists in the public schema
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'post'
            );
        """)
        exists = cur.fetchone()[0]

        if not exists:
            print("Table 'post' does not exist.")
        else:
            cur.execute("SELECT COUNT(*) FROM public.post;")
            count = cur.fetchone()[0]
            print(f"Table 'post' exists and contains {count} entries.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error connecting to database or querying table: {e}")

if __name__ == "__main__":
    main()

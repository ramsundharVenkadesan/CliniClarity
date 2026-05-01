import firebase_admin
from firebase_admin import auth

def purge_all_users():
    try:
        app = firebase_admin.initialize_app() # Initialize using Application Default Credentials (ADC)
    except ValueError: pass # Already initialized in the environment

    try:
        page = auth.list_users() # Fetch up to 1000 users
        uids = [user.uid for user in page.users]

        if not uids:
            print("No users to purge.")
            return

        print(f"Found {len(uids)} users. Initializing Purge...")

        delete_users = auth.delete_users(uids) # Bulk delete the users

        if delete_users.failure_count > 0:
            print(f"Failed to delete {delete_users.failure_count} users!")


    except Exception as ex:
        print(f"Error purging users: {ex}")

if __name__ == "__main__":
    purge_all_users()
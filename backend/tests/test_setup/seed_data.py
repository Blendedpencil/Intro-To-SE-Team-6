from tests.factories import seed_basic_users, seed_listings


def run_seed():
    print("Seeding database...")

    admins, buyers, sellers = seed_basic_users()
    listings = seed_listings()

    print(f"Created {len(admins)} admins")
    print(f"Created {len(buyers)} buyers")
    print(f"Created {len(sellers)} sellers")
    print(f"Created {len(listings)} listings")

    print("Seeding complete.")
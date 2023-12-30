import requests
from tqdm import tqdm

# Function to get a list of all domains
def get_domain_list(api_key, email):
    base_url = 'https://api.cloudflare.com/client/v4'
    url = f'{base_url}/zones'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        domains = response.json().get('result', [])
        return domains
    else:
        print(f'Failed to fetch domain list. Status code: {response.status_code}')
        print(response.json())
        return None

# Function to display the total number of DNS records for a selected domain
def get_total_dns_records(api_key, zone_id, email, domains):
    base_url = 'https://api.cloudflare.com/client/v4'
    url = f'{base_url}/zones/{zone_id}/dns_records'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        records = response.json().get('result', [])
        total_records = len(records)
        domain_name = next((domain['name'] for domain in domains if domain['id'] == zone_id), None)
        print(f'Domain Name: {domain_name} | Domain ID: {zone_id} | Total DNS Records: {total_records}')
    else:
        print(f'Failed to fetch DNS records. Status code: {response.status_code}')
        print(response.json())

# Function to delete all DNS records for a selected domain
def delete_all_dns_records(api_key, zone_id, email):
    base_url = 'https://api.cloudflare.com/client/v4'
    url = f'{base_url}/zones/{zone_id}/dns_records'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json',
    }

    # Fetch all DNS records, handling pagination
    all_records = []
    page = 1
    while True:
        params = {'page': page, 'per_page': 100}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            records_page = response.json().get('result', [])
            all_records.extend(records_page)

            if len(records_page) < 100:
                break  # Reached the last page
            else:
                page += 1
        else:
            print(f'\nFailed to fetch DNS records. Status code: {response.status_code}')
            print(response.json())
            return

    print(f'\nTotal DNS Records for the selected domain (ID: {zone_id}) is : {len(all_records)}')

    if not all_records:
        print("So Please choose a Domain ID with Bulk DNS.")
        return

    # Display a progress bar for deletion
    user_confirmation = input(f"\nAre you sure you want to delete all DNS records? (yes/no): ").lower()
    if user_confirmation != 'yes':
        print("DNS Records deletion canceled.")
        return

    for record in tqdm(all_records, desc="Deleting DNS Records", unit="record"):
        record_id = record['id']
        delete_url = f'{base_url}/zones/{zone_id}/dns_records/{record_id}'
        delete_response = requests.delete(delete_url, headers=headers)

    print("\nAll DNS Records Deleted Successfully.")

# Function to validate Cloudflare API key
def validate_api_key(api_key, email):
    base_url = 'https://api.cloudflare.com/client/v4/user'
    url = f'{base_url}'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        print(f'Invalid API key or Email. Please check your credentials.')
        return False

# Function to validate email format
def validate_email(email):
    # You can add more sophisticated email validation if needed
    if "@" in email and "." in email:
        return True
    else:
        print(f'Invalid email format. Please enter a valid email address.')
        return False

# Main function
def main():
    api_key = input("Enter your Global API Key: ")
    email = input("Enter your Cloudflare email: ")

    # Validate API key and email
    while not (validate_api_key(api_key, email) and validate_email(email)):
        api_key = input("Enter your Global API Key: ")
        email = input("Enter your Cloudflare email: ")

    print("CF Global API key and Cloudflare Mail Validated Successfully. Proceeding with the script...")

    while True:
        # Get a list of all domains
        domains = get_domain_list(api_key, email)

        if domains:
            print('\nList of domains:')
            for domain in domains:
                get_total_dns_records(api_key, domain['id'], email, domains)  # Display total DNS records for each domain

            selected_domain_id = input('\nEnter the ID of the domain to delete all DNS records (q to quit): ')

            if selected_domain_id.lower() == 'q':
                break

            # Delete all DNS records for the selected domain
            delete_all_dns_records(api_key, selected_domain_id, email)

if __name__ == "__main__":
    main()
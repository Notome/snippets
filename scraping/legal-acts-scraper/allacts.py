import requests

base_url = "https://api.ord.vk.com/"
headers = {
    "Host": "api.ord.vk.com",
    "Authorization": "Bearer 567985380b4f4de4b7dc8bc141d60163"
}

def get_contracts(headers):
    url = base_url + "v1/contract"
    params = {"limit": 10000}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['external_ids']

def get_invoices(headers):
    url = base_url + "v1/invoice?limit=10000"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['external_ids']

def get_invoice_data(headers, invoice_id):
    url = base_url + f"v3/invoice/{invoice_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

contracts = get_contracts(headers)
invoices = get_invoices(headers)

contracts_set = set()
contracts_with_invoices = set()

for x in contracts: contracts_set.add(x)
print('В сет договоров добавили')
for x in invoices: contracts_with_invoices.add(get_invoice_data(headers, x)['contract_external_id'])
print('В сет актов добавили')
while contracts_with_invoices: contracts_set.remove(contracts_with_invoices.pop())

print(contracts_set)

# def get_contract_info(headers, external_id):
#     url = base_url + f"v1/contract/{external_id}"
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     return response.json()

# all_contracts = get_contracts(headers)['external_ids']

# all_invoices = get_invoices(headers)['external_ids']
# contracts_with_invoices = set()

# for invoice_id in all_invoices:
#     invoice_data = get_invoice_data(headers, invoice_id)
#     contract_id = invoice_data.get('contract_external_id')
#     if contract_id:
#         contracts_with_invoices.add(contract_id)


# contracts_without_invoices = [cid for cid in all_contracts if cid not in contracts_with_invoices]

# for contract_id in contracts_without_invoices:
#     contract_info = get_contract_info(headers, contract_id)
#     print(contract_info)
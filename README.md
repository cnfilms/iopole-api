![img](https://www.iopole.com/assets/logo.svg)

# iopole-api

### How to use 🔧
    
    from iopoleapi.client import IopoleAPI
    
    api = IopoleAPI(client_id='YOUR_CLIENT_ID',
                    client_secret='YOUR_CLIENT_SECRET',
                    base_url='IOPOLE_BASE_URL',
                    auth_url='IOPOLE_AUTH_URL')
    api.auth()

    # Send invoices
    invoice_id = api.send_invoice('path/to/invoice.pdf')

    # Get invoices original file
    invoice = api.get_invoice(valid_invoice_id)

    # Get invoice metadata
    metadata = api.get_invoice_metadata(valid_invoice_id)

    # Get Iopole enrollment link
    url = api.get_enrollment_link(company_siren)

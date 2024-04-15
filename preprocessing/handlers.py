def le_cert(cert_name):
    return f"""
ssl_certificate "/etc/letsencrypt/live/{cert_name}/fullchain.pem";
ssl_certificate_key "/etc/letsencrypt/live/{cert_name}/privkey.pem";
"""
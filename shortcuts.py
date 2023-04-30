import socket
import os
import sys
from jinja2 import Template

def get_input(prompt, required=True):
    """
    Prompt user for input and return value. If required=True, keep prompting
    until non-empty input is received. If user presses Ctrl-C, exit the script.
    """
    while True:
        try:
            value = input(f"{prompt} \n")
            if required and not value:
                print('Input is required')
            else:
                return value
        except KeyboardInterrupt:
            print('\nExiting...')
            sys.exit()


def render_template(template_path, context):
    """
    Render Jinja2 template using the provided context dictionary.
    """
    with open(template_path, 'r') as f:
        template = Template(f.read())
    return template.render(context)


def create_systemd_service(template_path, service_name, context):
    """
    Render template and create systemd service file in /etc/systemd/system/.
    """
    unit_file = render_template(template_path, context)
    service_path = f'/etc/systemd/system/{service_name}'

    with open(service_path, 'w') as f:
        f.write(unit_file)

    os.chmod(service_path, 0o755)

    print(f'Systemd service created: {service_path}')
    return service_path


def create_nginx_config(domain_name, template_path, context):
    """
    This creates nginx config file for a domain or subdomain in /etc/nginx/sites-available
    and also creates a symbolic link in /etc/nginx/sites-enabled.
    """
    with open(f"/etc/nginx/sites-available/{domain_name}", 'w') as file:
                file.write(render_template(template_path, context))
                os.system(f"sudo ln -s /etc/nginx/sites-available/{domain_name} /etc/nginx/sites-enabled/")
                restart_systemd_service('nginx.service')
                os.system('systemctl restart nginx')
                clear_terminal()
                print(f"nginx config file created for {domain_name}")


def reload_systemd():
    """
    Reload systemd daemon.
    """
    os.system('sudo systemctl daemon-reload')


def enable_systemd_service(service_name):
    """
    Enable systemd service.
    """
    os.system(f'sudo systemctl enable {service_name}')
    print(f'Systemd service enabled: {service_name}')


def restart_systemd_service(service_name):
    """
    Restart systemd service.
    """
    os.system(f'sudo systemctl restart {service_name}')
    print(f'Systemd service restarted: {service_name}')


def find_free_port(port_range=(1024, 65535)):
    """
    Find a free http or tcp or udp port to bind your web appliication to.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        for port in range(port_range[0], port_range[1]+1):
            try:
                sock.bind(('localhost', port))
                return port
            except OSError:
                pass
    raise OSError("Could not find a free port")

def clear_terminal():
    os.system('clear')


"""
This module allows deploying a generic application for various programming languages.
"""
from shortcuts import *

is_static_website = False

app_port = find_free_port()

framework = get_input("""
What technology or  framework does your application run?
1. Django
2. HTML/CSS/Javascript (static webite)
""")
clear_terminal()

if framework == '1':
    global command
    web_server = get_input("""
    Choose how you want to deploy:
    1. Gunicorn + letsecrypt SSL
    2. Gunicorn + Nginx + letsencrypt SSL
    3. Gunicorn without SSL
    4. Django Development server without SSL
    5. Django Development server + Nginx + letsencrypt SSL
    """)
    clear_terminal()
    if web_server == '1':
        domain_name = get_input('Enter domain name or subdomain:')
        project_name = get_input('Enter project name:')
        command = f"gunicorn {project_name}.wsgi -b 0.0.0.0:{app_port} --workers 3 --certfile=/etc/letsencrypt/live/{domain_name}/fullchain.pem --keyfile=/etc/letsencrypt/live/{domain_name}/privkey.pem"
    elif web_server == '2':
        domain_name = get_input('Enter domain name or subdomain:')
        project_name = get_input('Enter project name:')
        command = f"gunicorn {project_name}.wsgi -b 0.0.0.0:{app_port} --workers 3"
    elif web_server == '3':
        domain_name = get_input('Enter domain name or subdomain:')
        project_name = get_input('Enter project name:')
        command = f"gunicorn {project_name}.wsgi -b 0.0.0.0:{app_port} --workers 3"
    elif web_server == '4':
        domain_name = get_input('Enter domain name or subdomain:')
        project_name = get_input('Enter project name:')
        command = f"python3 manage.py runserver 0.0.0.0:{app_port}"
    elif web_server == '5':
        domain_name = get_input('Enter domain name or subdomain:')
        project_name = get_input('Enter project name:')
        command = f"python3 manage.py runserver 0.0.0.0:{app_port}"
        

    context = {
                'service_name': get_input('Enter systemd service name:'),
                'description': get_input('Enter systemd service description:'),
                'user': get_input('Enter systemd service user: '),
                'group': get_input('Enter systemd service group: '),
                'work_dir': get_input('Enter project working directory: '),
                'runserver_command': command,
                'domain_name': domain_name, 'is_static_webite': False
                
            }

    # Render template and create systemd service file
    template_path = 'templates/generic_systemd.j2'
    create_systemd_service(template_path, context['service_name'], context)

    # Enable and restart systemd service
    enable_systemd_service(context['service_name'])
    reload_systemd()
    restart_systemd_service(context['service_name'])
    restart_systemd_service('nginx')
    if web_server == '1':
        clear_terminal()
        if app_port == '443':
            print(f"Congratulations! your application is deployed at https://{context['domain_name']}")
        print(f"Congratulations! your application is deployed at https://{context['domain_name']}:{app_port}")
        

    elif web_server == '2' or web_server == '5':
        template_path = 'templates/generic_nginx.j2'
        clear_terminal()
        https_port = get_input('Enter Nginx SSL port:')
        context['https_port'] = https_port
        with open(f"/etc/nginx/sites-available/{context['domain_name']}", 'w') as file:
                file.write(render_template(template_path, context))
                os.system(f"sudo ln -s /etc/nginx/sites-available/{context['domain_name']} /etc/nginx/sites-enabled/")
                restart_systemd_service('nginx.service')
                os.system('systemctl restart nginx')
                clear_terminal()
        if https_port == '443':
            print(f"Congratulations! Your website is deployed at https://{context['domain_name']}")
        print(f"Congratulations! Your website is deployed at https://{context['domain_name']}:{context['https_port']}")

    if web_server == '3' or web_server == '4':
        clear_terminal()
        if app_port == '80':
            print(f"Congratulations! your application is deployed at http://{context['domain_name']}")
        print(f"Congratulations! your application is deployed at http://{context['domain_name']}:{app_port}")
        



elif framework == '2':
        deploy_type = get_input("""
        Choose how you want to deploy:
        1. Static website with SSL
        """)
        domain_name = get_input('Enter domain name or sudomain:')
        template_path = 'templates/generic_nginx.j2'
        web_root = get_input('Enter absolute path to your website document root: ')
        if deploy_type == '1':
            context = {
                'domain_name': domain_name,
                'https_port': get_input('Enter nginx ssl port: '),
                'is_static_website': True,
                'static_website_root': web_root,
            }
            with open(f"/etc/nginx/sites-available/{domain_name}", 'w') as file:
                file.write(render_template(template_path, context))
                os.system(f"sudo ln -s /etc/nginx/sites-available/{domain_name} /etc/nginx/sites-enabled/")
                restart_systemd_service('nginx.service')
                clear_terminal()
            if app_port == '443':
                print(f"Congratulations! Your website is deployed at https://{domain_name}")
            print(f"Congratulations! Your website is deployed at https://{domain_name}:{context['https_port']}")

        



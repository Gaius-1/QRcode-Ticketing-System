from config import *
from webserver import *
import sys

guests = [{"first_name": "Frederick", "last_name": "Agbo", "phone_number": "0558478823"},
          {"first_name": "John", "last_name": "Smith", "phone_number": "0245397251"}
         ]

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'

    if command == 'generate_ticket_link':
        agree = input('This will create a new file. Are you sure? (y/n) ')
        if agree == 'y':
            from excel_handler import generate_ticket_link
            generate_ticket_link(INPUT_FILE_PATH, OUTPUT_FILE_PATH, DOMAIN_NAME)
            from webserver import get_nginx_config
            get_nginx_config()

    elif command == 'run_webserver':
        # from webserver import run_server
        run_server()

    elif command == 'add_ticket_id':
        from excel_handler import add_new_guest_from_excel
        add_new_guest_from_excel(OUTPUT_FILE_PATH, guests, DOMAIN_NAME)

    elif command == 'help':
        print('Available commands:')
        print('\tadd_ticket_id')
        print('\trun_webserver')
        print('\thelp')

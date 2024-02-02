import mechanicalsoup
import argparse

def custom_auth_dvwa(user_provided_url):
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    dvwa_setup_page = user_provided_url + "/dvwa/setup.php"
    browser.open(dvwa_setup_page)
    print(browser.page)
    browser.select_form(selector='form[action="#"]')
    browser.submit_selected()

    dvwa_login_page = user_provided_url + "/dvwa"
    browser.open_relative(dvwa_login_page)  # We've made it to the login page
    browser.select_form(selector='form[action="login.php"]')
    browser.form.input({"username": "admin"})
    browser.form.input({"password": "password"})
    browser.submit_selected()

    # Now navigate to security setting page http://127.0.0.1/dvwa/security.php
    dvwa_security_page = user_provided_url + "/dvwa/security.php"
    browser.open_relative(dvwa_security_page)
    browser.select_form(selector='form[action="#"]')
    browser["security"] = "low"
    browser.submit_selected()

    # Now go to home page and print
    dvwa_home_page = user_provided_url + "/dvwa/"
    browser.open_relative(dvwa_home_page)
    print(browser.page)

def cli(args = None):
    print("[discover | test] url OPTIONS\n\n"
          "COMMANDS:\n"
          "\tdiscover  Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.\n"
          "\ttest Under construction\n\n"
          "OPTIONS:\n"
          "\tOptions can be given in any order.\n\n"
          "\t--custom-auth=dvwa  Signal that the fuzzer should use hard-coded authentication for Damn Vulnerable Web Application.\n\n"
          "MORE TO COME IN LATER EDITIONS!")
    # if the user is running main.py on their own (Not the CI)
    if args is None:
        cli_input = input()
        cli_input_list = cli_input.split()
        if cli_input_list[2] == '--custom-auth=dvwa':
            custom_auth_dvwa(cli_input_list[1])
    else:
        print(args)
        custom_auth_dvwa(args)




def main():
    parser = argparse.ArgumentParser(description='Fuzz me harder')
    parser.add_argument('deliverable0', type=str, help='hardcoded deliverable 0')
    args = parser.parse_args()
    cli(args.deliverable0)



main()

# to test on my own machine: discover http://127.0.0.1 --custom-auth=dvwa
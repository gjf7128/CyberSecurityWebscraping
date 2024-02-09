import mechanicalsoup
import argparse

from mechanicalsoup import LinkNotFoundError


def custom_auth_dvwa(user_provided_url):
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    dvwa_setup_page = user_provided_url + "/dvwa/setup.php"
    print(dvwa_setup_page)
    browser.open(dvwa_setup_page)
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


def cli(args=None):
    # if the user is running main.py without trying to pass args... Might scrap this
    if args is None:
        cli_input = input()
        cli_input_list = cli_input.split()
        if cli_input_list[2] == '--custom-auth=dvwa':
            custom_auth_dvwa(cli_input_list[1])
    else:
        if args.discovertest is not None and args.url is not None:
            url = args.url
            if args.custom_auth == "dvwa":
                custom_auth_dvwa(url)
            if args.discovertest == "discover":
                if args.common_words is None:
                    print("common words argument is required.  Try using --common-words=mywords.txt")
                else:
                    page_discovery(args)


def page_discovery(args):
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup', raise_on_404=True)
    pages_found = page_guessing(args, browser)
    print(str(len(pages_found)) + " pages guessed and found\n")
    pages_found.append(args.url)
    for pages in pages_found:
        print(pages)
        # LEFT OFF HERE


def page_guessing(args, browser):
    pages_found = []

    #extracting a list of words from text file
    f = open(args.common_words, "r")
    words_to_guess = f.readline().split()
    f.close()

    #extracting a list of extensions
    f = open(args.extensions, "r")
    extensions_to_guess = f.readline().split()
    f.close()
    
    print("Now Guessing Pages...\n")
    for word in words_to_guess:
        page_name = args.url + "/" + word
        for extension in extensions_to_guess:
            guessed_url = page_name + "." + extension
            try:
                browser.open(guessed_url)
                pages_found.append(guessed_url)
            except LinkNotFoundError:
                print("guess: " + guessed_url + " failed")

    return pages_found



def main():
    print("[discover | test] url OPTIONS\n\n"
          "COMMANDS:\n"
          "\tdiscover  Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.\n"
          "\ttest Under construction\n\n"
          "OPTIONS:\n"
          "\tOptions can be given in any order.\n\n"
          "\t--custom-auth=dvwa  Signal that the fuzzer should use hard-coded authentication for Damn Vulnerable Web Application.\n\n"
          "Discover options:\n"
          "\t--common-words=file  file of common words to be used for page guessing. Try --common-words=mywords.txt\n"
          "\t--extensions=file    file of path extensions to be used with page guessing.  Try --extensions=extensions.txt\n\n"
          "MORE TO COME IN LATER EDITIONS!")
    parser = argparse.ArgumentParser(description='Fuzz me harder')
    parser.add_argument("discovertest", help="Expects either: discover or test")
    parser.add_argument("url", help="The url we are discovering or testing")
    parser.add_argument("--custom-auth", help="hardcoded deliverable 0")
    parser.add_argument("--common-words", help="try using --common-words=mywords.txt. REQUIRED")
    parser.add_argument("--extensions", help="try using --extensions=extensions.txt")
    args = parser.parse_args()
    cli(args)



main()

# python main.py discover http://localhost --custom-auth=dvwa
# or
# python main.py test http://localhost --custom-auth=dvwa       will accomplish old part 0

#fuzz part1 page guessing
# python main.py discover http://localhost --common-words=mywords.txt --extension=extensions.txt
# python main.py discover http://localhost/fuzzer-tests --common-words=mywords.txt --extension=extensions.txt



import mechanicalsoup
import argparse
import time

from mechanicalsoup import LinkNotFoundError


def custom_auth_dvwa():
    user_provided_url = "http://127.0.0.1"

    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    dvwa_setup_page = user_provided_url + "/dvwa/setup.php"
    browser.open(dvwa_setup_page)
    browser.select_form(selector='form[action="#"]')
    browser.submit_selected()

    dvwa_login_page = user_provided_url + "/dvwa"
    browser.open_relative(dvwa_login_page)  # We've made it to the login page
    browser.select_form(selector='form[action="login.php"]')
    browser.form.input({"username": "admin"})
    browser.form.input({"password": "password"})
    browser.submit_selected()

    # Now navigate to security setting page http://localhost/dvwa/security.php
    dvwa_security_page = user_provided_url + "/dvwa/security.php"
    browser.open_relative(dvwa_security_page)
    browser.select_form(selector='form[action="#"]')
    browser["security"] = "low"
    browser.submit_selected()

    # Now go to home page and print
    dvwa_home_page = user_provided_url + "/dvwa/"
    browser.open_relative(dvwa_home_page)
    print(browser.page)
    print("custom auth dvwa succeeded\n\n")


def cli(args=None):
    # if the user is running main.py without trying to pass args... Might scrap this
    if args is None:
        cli_input = input()
        cli_input_list = cli_input.split()
        if cli_input_list[2] == '--custom-auth=dvwa':
            custom_auth_dvwa()
    else:
        if args.discovertest is not None and args.url is not None:
            if args.custom_auth == "dvwa":
                custom_auth_dvwa()
            if args.discovertest == "discover":
                if args.common_words is None:
                    print("common words argument is required.  Try using --common-words=mywords.txt")
                else:
                    page_discovery(args)
            if args.discovertest == "test" and args.vectors is not None:
                if args.custom_auth == "dvwa":
                    custom_auth_dvwa()
                if args.vectors == "vectors.txt":
                    try_vectors(args)
                else:
                    print("vectors argument is required.  Try using --vectors=vectors.txt")


def try_vectors(args):
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup', raise_on_404=True)

    # extracting a list of extensions
    f = open(args.vectors, "r")
    vectors_to_try = f.readline().split('\n')
    f.close()

    browser.open(args.url)
    # iterating over all vectors and appending to URL's
    for vector in vectors_to_try:
        appended_url = args.url + vector
        try:
            start = time.perf_counter() * 1000
            request = browser.open(appended_url)
            end = time.perf_counter() * 1000
            print("Vector SUCCESSFULLY appended to URL\n")
            if args.slow is not None and end - start > args.slow:
                print("Request went over " + str(args.slow) + " milliseconds")
            if args.response is not None:
                check_response_code(request)
            check_sanitized(args, browser.page, vector)
        except LinkNotFoundError:
            print("appended URL gave a LinkNotFoundError")


    #iterating over every form on the current page
    common_form_tag_names = ["username", "password", "ip", "password_new", "password_conf", "id", "name", "txtName", "mtxMessage"]
    browser.open(args.url)
    for vector in vectors_to_try:
        for tag_name in common_form_tag_names:
            try:
                browser.select_form()
                browser.form.set(tag_name, vector)
                start = time.perf_counter() * 1000
                request = browser.submit_selected()
                end = time.perf_counter() * 1000
                if args.slow is not None and end - start > args.slow:
                    print("Request went over " + str(args.slow) + " milliseconds")
                if args.response is not None:
                    check_response_code(request)
                print("Input Field " + tag_name + " with vector succeeded form submission")
                check_sanitized(args, browser.page, vector)
            except LinkNotFoundError:
                print("Input TextField did not exist or some other manner of error happened")


def check_sanitized(args, page, vector):
    if args.sanitized_chars == "sanitized.txt":
        f = open(args.sanitized_chars, "r")
        san_chars = f.readline().split('\n')
        f.close()

        chars_unsanitized = []
        for character in san_chars:
            if character in vector:
                chars_unsanitized.append(character)

        # if vector contained chars that should be sanitized and the whole vector remained unsanitized, print page
        if len(chars_unsanitized) >= 1:
            print("The following characters existed within our vector and may not have been sanitized:\n")
            print(chars_unsanitized)
            if vector in page:
                print("unsanitized vector detected!")
                print("Here is the page for reference: \n" + page + "\n\n")
            else:
                print("vector was either fully or partially sanitized\n\n")


# After googling how many error codes there were, I only coded the error code i've experienced because that's insane.
def check_response_code(response):
    if str(200) not in str(response):
        if str(403) in str(response):
            print("403 Error code: Forbidden - Client does not have access rights and has been denied.")
        elif str(200) not in str(response) and str(403) not in str(response):
            print(response)


def page_discovery(args):
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup', raise_on_404=True)
    pages_found = page_guessing(args, browser)
    print(str(len(pages_found)) + " pages guessed and found :\n")
    pages_found.insert(0, args.url)
    links_confirmed = []
    for page in pages_found:
        print(page)
        links_confirmed_inner = link_crawling(page, browser)
        links_confirmed.append(links_confirmed_inner)
        print("\n")


def link_crawling(page, browser):
    # Holds list of url's/pages confirmed to exist.
    pages_crawled_to = []

    browser.open(page)
    browser.list_links()

    # I spent waaaaaaay too long trying to teach myself RegEx to avoid going off site when link crawling
    # spent nearly 2 hours on this.  You have to be a 4D chess master to learn RegEx.  My brain is fried.
    # Alas, despite my efforts I have failed to construct a RegEx that avoids going off site.
    # I should have just bit the bullet on this part and not wasted so much time.
    links_on_page = browser.links(url_regex="^(?:htt(?:ps|p)://www.)*.")
    print(links_on_page)

    for link in links_on_page:
        try:
            browser.follow_link(link)
            pages_crawled_to.append(link)
        except LinkNotFoundError:
            print("attempted to visit link but link not found")

    return pages_crawled_to




def page_guessing(args, browser):
    pages_found = []

    #extracting a list of words from text file
    f = open(args.common_words, "r")
    words_to_guess = f.readline().split()
    f.close()

    if args.extensions is not None:
        # extracting a list of extensions
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
    else:
        print("Now Guessing Pages...\n")
        for word in words_to_guess:
            page_name = args.url + "/" + word
            guessed_url = page_name + ".php"
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
          "\t--extensions=file    file of path extensions to be used with page guessing.  Try --extensions=extensions.txt\n"
          "\t--vectors=file       file containing attack vectors.  try --vectors=vectors.txt\n"
          "\t--sanitized-chars=file    file containing characters that should be sanitized.  try --sanitized-chars=sanitized.txt\n"
          "\t--slow               how fast a response should at least be in ms.  try --slow=100\n"
          "\t--response           whether to check for response codes.  try --response=<AnyString>\n")
    parser = argparse.ArgumentParser(description='Fuzz me harder')
    parser.add_argument("discovertest", help="Expects either: discover or test")
    parser.add_argument("url", help="The url we are discovering or testing")
    parser.add_argument("--custom-auth", help="hardcoded deliverable 0")
    parser.add_argument("--common-words", help="try using --common-words=mywords.txt. REQUIRED")
    parser.add_argument("--extensions", help="try using --extensions=extensions.txt")
    parser.add_argument("--vectors", help="try using --vectors=vectors.txt")
    parser.add_argument("--sanitized-chars", help="try using --sanitized-chars=sanitized.txt")
    parser.add_argument("--sensitive", help="try using --sensitive=sensitive.txt")
    parser.add_argument("--slow", type=int, help="number of milliseconds considered to be a slow response. try --slow=100")
    parser.add_argument("--response", help="flag to check for response codes if not 200. try --response=<any string>")

    args = parser.parse_args()
    cli(args)



main()

# python main.py discover http://localhost --custom-auth=dvwa
# or
# python main.py test http://localhost --custom-auth=dvwa       will accomplish old part 0

#fuzz part1 page guessing
# python main.py discover http://localhost --common-words=mywords.txt --extension=extensions.txt
# python main.py discover http://localhost/fuzzer-tests --common-words=mywords.txt --extension=extensions.txt

#fuzz part2 test
# python main.py test http://127.0.0.1/dvwa/vulnerabilities/brute/ --custom-auth=dvwa --vectors=vectors.txt --sanitized-chars=sanitized.txt --slow=100 --response=yes
# this page has username and password TextFields

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/exec/ --custom-auth=dvwa --vectors=vectors.txt
# this page has ip TextField

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/csrf/ --custom-auth=dvwa --vectors=vectors.txt
# this page has password_new and password_conf TextFields

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/sqli/ --custom-auth=dvwa --vectors=vectors.txt
# this page has id TextField

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/sqli_blind/ --custom-auth=dvwa --vectors=vectors.txt
# this page has id TextField

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/xss_r/ --custom-auth=dvwa --vectors=vectors.txt
# this page has a name TextField

# python main.py test http://127.0.0.1/dvwa/vulnerabilities/xss_r/ --custom-auth=dvwa --vectors=vectors.txt
# this page has a txtName and mtxMessage TextField








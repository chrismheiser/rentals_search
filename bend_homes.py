import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from craigslist import CraigslistHousing

# Enter your query restrictions
max_price = 1400
location = "bend"

# Track what was found and what was matched
appfolio_found = 0
appfolio_matched = 0
craigslist_found = 0
craigslist_matched = 0
dpm_found = 0
dpm_matched = 0


# List addresses that are on the top of your list
favorites = [
]

# List addresses you're on the fence about
maybe = [
]

# List the addresses of properties you don't like or that slipped past the requirements
bad_list = [
]

# List the names of the appfolio accounts to search
companies = [
    "villageprop",
    "bend",
    "pluspmllc",
    "asuperior",
    "mountainviewpm",
    "alpine",
    "austinpmor",
    "highdesertpm",
    "colm",
    "foxmgmtservices2",
    "mtbachpm",
    "atlast",
    "thepennbrookco",
    "myluckhouse"
]


def get_deschutespm():
    global favorites, bad_list, dpm_found, dpm_matched, location, max_price

    print("\n")
    print("RENTINGOREGON.COM")
    print("================================")
    company_url = "https://rentingoregon.com/listings/?orderby=price&order=asc"
    r = requests.get(company_url, headers={'user-agent': 'Paw/3.1.5 (Macintosh; OS X/10.13.6) GCDHTTPRequest',
                                           'content-type': "application/json"})
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.prettify())
    listings = soup.findAll("div", {"class": "property"})
    for i in listings:
        dpm_found += 1
        listing_labels = {}
        bad = False
        price_match = True
        pets = True
        location_match = True
        favorite = False
        try:
            listing_price = int(i.find("span", {"class": "listing-price-value"}).string.replace(",", ""))
            listing_address = i.find("h2", {"class": "entry-title"}).a.string
            listing_location = i.find("span", {"class", "listing-details-location"}).find("a", {"class", "listing-term"}).string
            listing_link = i.find("h2", {"class": "entry-title"}).a.get("href")
            labels = i.findAll("span", {"class", "listing-details-detail"})
            for e in labels:
                detail = e.find("span", {"class": "listing-details-label"}).string
                value = e.find("span", {"class": "listing-details-value"}).string
                if detail:
                    if "location" not in detail.lower():
                        if "pets" in detail.lower():
                            if "no" in value.lower():
                                pets = False
                        if detail not in listing_labels:
                            listing_labels[detail] = value

            # Have I already looked at this property and said no? Check the "bad" list
            if listing_address in bad_list:
                bad = True
            if listing_address in favorites:
                favorite = True
            if location != listing_location.lower():
                location_match = False
            if listing_price > max_price:
                price_match = False
            if price_match and pets and location_match and not bad:
                print("\n")
                if favorite:
                    print("******** FAVORITE *************")
                dpm_matched += 1
                print(listing_link)
                print(listing_address)
                print("Rent: {}".format(listing_price))
                for k, v in listing_labels.items():
                    print(k, v)
                print("\n")
                print("__________________________________")

        except Exception as e:
            print("oops: error: {}".format(e))

    print("Listings Found: {}".format(dpm_found))
    print("Listings Matched: {}".format(dpm_matched))


def get_craigslist():
    global craigslist_found, craigslist_matched

    print("\n")
    print("CRAIGSLIST RESULTS")
    print("================================")

    cl_h = CraigslistHousing(site='bend', category='apa',
                             filters={'max_price': max_price})
    for result in cl_h.get_results(sort_by='newest', geotagged=True, limit=15):
        # print(result)
        craigslist_found += 1
        show = True
        if "where" in result:
            for loc in ["prineville", "la pine", "redmond", "john day", "chemult", "crescent lake"]:
                try:
                    if loc in result["where"].lower():
                        show = False
                        break
                except Exception:
                    pass
        if "name" in result:
            for loc in ["prineville", "la pine", "redmond", "john day", "chemult", "crescent lake"]:
                try:
                    if loc in result["name"].lower():
                        show = False
                        break
                except Exception:
                    pass

        if show:
            craigslist_matched += 1
            keys = ["datetime", "price", "name", "where", "bedrooms", "area", "url"]
            for key in keys:
                if key in result:
                    print("{}: {}".format(key.upper(), result[key]))

        print("\n")
        print("__________________________________")

    print("Listings Found: {}".format(craigslist_found))
    print("Listings Matched: {}".format(craigslist_matched))


def listing_desc(desc):
    try:
        for br in desc.findAll('br'):
            next_s = br.nextSibling
            if not (next_s and isinstance(next_s, NavigableString)):
                continue
            next2_s = next_s.nextSibling
            if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                text = str(next_s).strip()
                if text:
                    print(next_s)
    except Exception:
        print("No description error")


def no_pets_desc(desc):
    try:
        for br in desc.findAll('br'):
            next_s = br.nextSibling
            if not (next_s and isinstance(next_s, NavigableString)):
                continue
            next2_s = next_s.nextSibling
            if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                text = str(next_s).strip()
                if text:
                    if "no pets" in text.lower():
                        return True
    except Exception:
        print("No description error")
    return False


def get_appfolio():
    global appfolio_matched, appfolio_found, location, max_price, bad_list, favorites

    print("\n")
    print("APPFOLIO RESULTS")
    print("================================")

    for name in companies:
        company_url = "https://" + name + ".appfolio.com"
        r = requests.get(company_url + "/listings")
        soup = BeautifulSoup(r.text, 'html.parser')
        # print(soup.prettify())
        listings = soup.findAll("div", {"class": "listing-item__body"})
        for i in listings:
            appfolio_found += 1
            price = 0
            bad = False
            price_match = True
            pets = True
            location_match = True
            favorite = False

            listing_link = ""
            listing_title = ""
            listing_address = ""
            listing_labels = []
            listing_pets = i.find("span", {"class": "js-listing-pet-policy"}).string
            if listing_pets:
                if "not allowed" in listing_pets.lower():
                    pets = False
                listing_pets = listing_pets.replace("Pet Policy: ", "")

            else:
                listing_pets = "NO PET INFO"
            try:
                listing_link = "{}{}".format(company_url, i.h2.a.get("href"))
            except AttributeError:
                # print("No URL link")
                pass
            try:
                listing_title = i.h2.a.string
            except AttributeError:
                # print("No title")
                pass
            try:
                listing_address = i.p.span.string
            except AttributeError:
                # print("No address")
                pass
            labels = i.findAll("dl", {"class": "detail-box__item"})
            for j in labels:
                if j.dd.string:
                    if "$" in j.dd.string:
                        price = int(j.dd.string.replace("$", "").replace(",", ""))
                listing_labels.append("{} : {}".format(j.dt.string, j.dd.string))

            desc1 = i.find("p", {"class": "listing-detail__description"})
            desc2 = i.find("p", {"class": "js-listing-description"})

            if desc1:
                desc = desc1
            elif desc2:
                desc = desc2
            else:
                desc = "No description"

            # Look for a "no pets" string inside the description box
            if no_pets_desc(desc):
                pets = False

            # Have I already looked at this property and said no? Check the "bad" list
            if listing_address.string in bad_list:
                bad = True
            if listing_address in favorites:
                favorite = True

            if location not in listing_address.lower():
                location_match = False
            #     print("WRONG CITY: {}".format(listing_address))
            if price > max_price:
                price_match = False
            #     print("TOO EXPENSIVE: {}".format(price))
            # if not pets:
            #     print("PET RESTRICTIONS: {}".format(listing_pets))
            if price_match and pets and location_match and not bad:
                print("\n")
                if favorite:
                    print("******** FAVORITE *************")
                appfolio_matched += 1
                print(listing_pets)
                print(listing_link)
                print(listing_title)
                print(listing_address)
                [print(i) for i in listing_labels]
                print(listing_desc(desc))
                print("\n")
                print("__________________________________")
    print("Listings Found: {}".format(appfolio_found))
    print("Listings Matched: {}".format(appfolio_matched))


get_deschutespm()
get_appfolio()
# get_craigslist()

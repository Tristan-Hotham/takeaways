"""Name-based cuisine classifier for UK food business names.

The Food Standards Agency data give a business type (takeaway, restaurant, pub, mobile caterer)
but not what food is sold. This module guesses the cuisine from the trading name alone, using
transparent keyword rules: chains first, then strong words ("fish bar", "kebab", "tandoori"),
then weaker hints ("dragon", "spice", "golden"). Anything else is left unclassified ("other").

classify(name) returns (category, rule) where rule says which pattern fired, so every decision
can be audited. Categories are listed in CATS in display order.
"""
import re

CATS = [
    ("fish_chips", "Fish and chips"),
    ("indian", "Indian and curry"),
    ("chinese", "Chinese"),
    ("pizza", "Pizza"),
    ("kebab", "Kebab and Turkish"),
    ("chicken", "Chicken shop"),
    ("burger", "Burger"),
    ("thai", "Thai"),
    ("japanese", "Japanese and sushi"),
    ("asian_other", "Other East and South East Asian"),
    ("italian", "Italian"),
    ("caribbean", "Caribbean and African"),
    ("mexican", "Mexican"),
    ("greek_med", "Greek and Middle Eastern"),
    ("sandwich", "Sandwich, bakery and deli"),
    ("cafe", "Cafe, coffee and sweet things"),
    ("other", "Not classified"),
]
LABEL = dict(CATS)

# chains and well-known brands: (regex, category)
CHAINS = [
    (r"\bkfc\b|kentucky fried|popeyes|\bmorley'?s\b|chicken cottage|\bdixy\b|sam'?s chicken|\bnando'?s\b|wingstop|\bpfc\b|favorite chicken|\bfavourite chicken|hfc\b|chick ?king|chicken ?king|perfect fried chicken|southern fried|\bchooks\b|\btfc\b|\bmfc\b|\bjfc\b|\bafc\b chicken|german doner kebab", None),
    (r"domino'?s|pizza hut|papa ?john'?s|\bpapa johns|pizza express|\bfranco manca|\bpizzaexpress|\bpieminister", None),
    (r"mcdonald'?s|burger king|five guys|\bwimpy\b|byron\b|honest burgers?|\bgbk\b|gourmet burger|shake shack|\bfatburger", "burger"),
    (r"\bsubway\b|\bgreggs\b|\bpret\b|pret a manger|\bleon\b|\bitsu\b|\bbirds bakery|\bpercy ingle|cooplands|\bwenzel'?s|\bpoundbakery|\bmilligans|\bbakers oven|\bwarrens bakery|\bmartins bakery|\bthree cooks", "sandwich"),
    (r"\bcosta\b|starbucks|caff[eè] nero|\bnero\b|\bbooths cafe|\bblack sheep coffee|\bharris \+ hoole|\bcoffee#1|\bcoffee 1\b", "cafe"),
    (r"wagamama|yo! ?sushi|\byo sushi|\byo to go\b|wasabi\b|\bsushimania|\bmisato|\bkokoro\b|\bsamurai\b", "japanese"),
    (r"\bpanku\b|\bsambal\b|\bchopstix\b|\btiger tiger\b", "asian_other"),
    (r"fireaway|caprinos?\b|\bgodfather pizza", "pizza"),
    (r"krispy kreme|auntie anne|millie'?s cookies|\bamorino\b|bubbleology|\bmr pretzels?|\bcinnabon|\bkaspa'?s\b|\bcreams\b|\bh?eavenly desserts|\bsweet ?treats?\b", "cafe"),
    (r"\bchicking\b|\broosters?\b|\bchesters\b|\bmorleys\b", "chicken"),
    (r"zizzi|ask italian|prezzo|bella italia|carluccio|\bfrankie (and|&) benny|\bvapiano", "italian"),
    (r"harry ramsden|\bthe codfather", "fish_chips"),
    (r"german doner|\bdoner haus\b|\bkebabish", "kebab"),
    (r"chiquito|taco bell|tortilla\b|wahaca|barburrito|\bchipotle\b|\btaco\b|\btacos\b|\bburrito", "mexican"),
    (r"\bturtle bay|\bcaribbean|\bjerk\b|\bjamaica|\bnigerian|\bafrican|\bghana|\bethiopian|\beritrean|\bsomali|\bsuya\b|\bjollof", "caribbean"),
]
CHAIN_RE = []
for pat, cat in CHAINS:
    CHAIN_RE.append((re.compile(pat), cat))

STRONG = [
    ("fish_chips", r"fish ?(and|&|n'?|'n'?) ?chips?|\bfish ?bar\b|\bfish ?shop\b|\bchip ?shop\b|\bchippy\b|\bchippie\b|\bchipper\b|\bfisheries\b|\bfish ?(&|and) ?chicken|\bfish ?(&|and) ?grill|\bfrying ?(pan|tonight)\b|\bchip ?(inn|bar|stop)\b|\bfish ?inn\b|\bfish ?kitchen\b|\bfishbar\b|\bchips\b|\bfish restaurant\b|\bthe fryer\b|\bfryery\b|\bfriery\b|\bfish ?(&|and) ?chip\b|\bfish & ?pizza|\bchip\b|\bfrydays?\b|\bfridays\b|\bcatch\b|\bsupper\b|\bsalt (and|&|n) vinegar\b|\bseafare\b|\bgalley\b|\bfish\b"),
    ("kebab", r"\bkebabs?\b|\bdoner\b|\bdöner\b|\bshawarma\b|\bshwarma\b|\bgyros?\b|\bkebab ?house\b|\bocakbasi\b|\bmangal\b|\bturkish\b|\bistanbul\b|\banatolia|\bantalya\b|\bbodrum\b|\bmarmaris\b|\bankara\b|\bkapadokya|\bcappadocia\b|\bkervan|\bkeba?b\b|\bcharcoal\b|\bocakbaşı\b|\bmeze ?grill\b"),
    ("pizza", r"\bpizz?as?\b|\bpizzeria\b|\bpizzaria\b|\bpizzas\b|\bcalzone\b|\bpizza\w*"),
    ("chicken", r"fried chicken|\bchicken\b|\bperi[- ]?peri\b|\bpiri[- ]?piri\b|\bwings?\b|\bchick\b|\bpollo\b"),
    ("burger", r"\bburgers?\b|\bburgr\b|\bsmash\b"),
    ("indian", r"\btandoori?\b|\bcurry\b|\bcurries\b|\bbalti\b|\bmasala\b|\bindian\b|\bbiryani\b|\bbiriyani\b|\bkarahi\b|\bkorma\b|\btikka\b|\bdosa\b|\bnaan\b|\bnan\b|\bbhaji\b|\bpakora\b|\bbangla|\bbengal|\bnepal|\bnepalese\b|\bgurkha\b|\bgorkha\b|\bhimalaya|\bkathmandu\b|\bpunjab|\bdelhi\b|\bbombay\b|\bmumbai\b|\bmadras\b|\bkashmir|\bsylhet|\bdhaka\b|\bgoa\b|\bkerala\b|\bmoghul|\bmughal|\bmogul\b|\bnawab\b|\bmaharaja|\bmaharani|\bshahi\b|\bshahee|\bbhaji|\bpakistani\b|\blahore\b|\bkarachi\b|\bsri lanka|\btiffin\b|\bthali\b|\bchaat\b|\bsamosa|\bdesi\b|\bghandi\b|\bgandhi\b|\bjalsa\b|\bmasaledar|\bindia\b|\bpaneer|\bvindaloo|\bdhal\b|\bdal\b"),
    ("chinese", r"\bchinese\b|\bchina\b|\bcantones|\bcanton\b|\bpeking\b|\bbeijing\b|\bhong kong\b|\bkowloon\b|\bszechuan\b|\bsichuan\b|\bshanghai\b|\bhunan\b|\bdim sum\b|\bchop ?suey\b|\bsuey\b|\bfried rice\b|\bwok\w*\b|\bchow mein\b"),
    ("thai", r"\bthai\b|\bthailand\b|\bbangkok\b|\bsiam\b|\bphuket\b|\bchiang\b|\bpad thai\b|\btuk ?tuk\b|\bbaan\b|\bban thai\b"),
    ("japanese", r"\bsushi\b|\bjapanese\b|\bjapan\b|\bramen\b|\bteriyaki\b|\bbento\b|\bkatsu\b|\btokyo\b|\bosaka\b|\bizakaya\b|\bteppanyaki\b|\bsamurai\b|\byakitori\b|\budon\b"),
    ("asian_other", r"\bvietnam|\bpho\b|\bbanh ?mi\b|\bkorean\b|\bkorea\b|\bseoul\b|\bmalaysia|\bsingapore|\bindonesia|\bfilipino|\bphilippine|\bburmese|\bpoke\b|\bbao\b|\basian\b|\bpan ?asian\b|\bbubble tea\b"),
    ("italian", r"\bitalian\b|\bitalia\b|\btrattoria\b|\bristorante\b|\bosteria\b|\bpasta\b|\bnapoli\b|\bnapoletana\b|\bsicilia|\btoscana\b|\broma\b|\bvenezia\b|\bmilano\b|\bgelato\b|\bgelateria\b|\bpiccolo\b|\bbella\b|\bmamma\b|\bla dolce\b|\bpronto\b"),
    ("greek_med", r"\bgreek\b|\bgreece\b|\bsouvlaki\b|\bfalafel\b|\blebanese\b|\blebanon\b|\bbeirut\b|\bsyrian\b|\bpersian\b|\biranian\b|\bkurdish\b|\bmeze\b|\bmezze\b|\bmediterranean\b|\bmed\b grill|\bcyprus\b|\bcypriot\b|\bmoroccan\b|\bmorocco\b|\bafghan\b|\barabic\b|\bmanakeesh\b|\bhalloumi\b"),
    ("mexican", r"\bmexican\b|\bmexico\b|\bcantina\b|\btaqueria\b|\bnachos?\b|\bquesadilla"),
    ("sandwich", r"\bsandwich|\bsarnie|\bbutty\b|\bbutties\b|\bbaguette|\bbap\b|\bbaps\b|\bdeli\b|\bdelicatessen\b|\bbakery\b|\bbakers?\b|\bbakehouse\b|\bpatisserie\b|\bboulangerie\b|\bcrust\b|\bbagels?\b|\bwraps?\b|\bpasties\b|\bpasty\b|\bpie shop\b|\bpies\b|\bsnack ?bar\b|\bfood to go\b|\bpanini\b|\bfilling station\b|\broll\b|\brolls\b|\bbakes?\b|\bspuds?\b|\bjacket potato|\bbuns\b|\bsub\b|\bsubs\b"),
    ("cafe", r"\bcaf[eé]s?\b|\bcoffee\b|\bcafeteria\b|\bespresso\b|\btea ?rooms?\b|\btearooms?\b|\btea ?shop\b|\bbrunch\b|\bcafè\b|\bcaffe\b|\bcaff\b|\bdiner\b|\bbrew\b|\broastery\b|\bdonuts?\b|\bdoughnuts?\b|\bwaffles?\b|\bcrepes?\b|\bpancakes?\b|\bdesserts?\b|\bice cream\b|\bmilkshakes?\b|\bjuice\b|\bsmoothie|\bcookies?\b|\bscoops?\b|\bboba\b|\bbubble\b|\bchai\b|\bcakes?\b|\bcupcakes?\b|\bsweets?\b|\btreats?\b|\bpretzels?\b|\bshakes?\b|\bsugar\b|\bgelato\b|\bchurros?\b|\bcrumbs\b"),
]
STRONG_RE = [(c, re.compile(p)) for c, p in STRONG]

# Weak hints: words common in the names of one kind of takeaway but not proof of it (a "Golden Dragon"
# or "Jade Garden" is nearly always Chinese, a "Spice Lounge" nearly always Indian). They are used only
# when no strong word fires, so "Orient Chicken & Pizza" is a chicken and pizza shop, not Chinese.
WEAK = [
    ("chinese", r"\bchinese\b|\bchina\b|\bcantones|\bcanton\b|\bpeking\b|\bbeijing\b|\bhong kong\b|\bkowloon\b|\bszechuan\b|\bsichuan\b|\bshanghai\b|\bhunan\b|\bdim sum\b|\bchow\b|\bwok\b|\bwoks\b|\bmandarin\b|\bpanda\b|\bdragon\b|\bjade\b|\bbamboo\b|\blotus\b|\bfortune\b|\bfu\b|\bwah\b|\bwing\b|\bwong\b|\bwang\b|\bchan\b|\bchen\b|\blee'?s\b|\byip\b|\bling\b|\bming\b|\btang\b|\bdynasty\b|\boriental\b|\bnoodles?\b|\bkung fu\b|\bhappy garden\b|\bnew garden\b|\bgolden (city|house|dragon|palace|garden|bowl|wok|star|jade|lotus|china|rice|bamboo|dynasty|harvest|river|sea|sun|moon|panda|phoenix|chopsticks|ocean|world|inn|valley|gate|pearl|crown|east|bay)\b|\bchopsticks?\b|\bphoenix\b|\bpearl\b|\bjasmine\b|\blucky\b|\bhappy (house|valley|family|garden|inn)\b|\bsun ?sun\b|\bfook\b|\bfat ?boy?s? ?chinese\b|\bkwok\b|\bkam\b|\bchung\b|\bcheung\b|\bwai\b|\bwu\b|\bhing\b|\bhoi\b|\bmay ?wah\b|\bsiu\b|\bloon\b|\bkin\b|\bgreat wall\b|\bmayflower\b|\blee garden\b|\bchop ?suey\b|\bsuey\b|\bnoble house\b|\borient\b|\bred lantern\b|\b(kings?|royal|tasty|new|lucky|jade|peking|lotus|bamboo|oriental|china|summer|rose|garden) garden\b|\bnew century\b|\bgood luck\b|\bnew diamond\b|\brainbow house\b|\bevergreen\b|\bsilver star\b|\bming'?s\b|\bwong'?s\b|\bmr rice\b|\bfried rice\b|\bgolden (kitchen|bridge|hill|bird|garden|wall|lion|fortune|bell|cup|chef|house|palace)\b|\bkam'?s\b|\bfortune cookie\b|\bhappy (chef|wok)\b|\bwok\w*\b"),
    ("indian", r"\bspice\b|\bspices\b|\bspicy\b|\bsaffron\b|\bcardamom\b|\bchutney|\bmahal\b|\braj\b|\btaj\b|\beverest\b|\bmasala\b"),
]
WEAK_RE = [(c, re.compile(p)) for c, p in WEAK]

# Precedence when several strong families fire. Hybrids such as "Pizza and Kebab House" or
# "Fish Bar and Chinese" are common; the first family in this order wins, and the second is kept.
ORDER = ["fish_chips", "indian", "thai", "japanese", "chinese", "kebab", "pizza", "chicken", "burger",
         "asian_other", "caribbean", "mexican", "greek_med", "italian", "sandwich", "cafe"]

# words that are strong evidence only in specific forms; e.g. "golden fry" is a chip shop
FISH_HINT = re.compile(r"\bfry\b|\bfryer\b|\bcod\b|\bhaddock\b|\bplaice\b|\bbatter\b|\bcodfather\b|\bfins?\b|\bseafood\b|\bsea ?food\b")


def norm(name):
    s = (name or "").lower()
    s = s.replace("’", "'").replace("`", "'")
    s = re.sub(r"[^a-z0-9&'äöüçéèàë+ ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def families(n):
    """All strong families that fire for a normalised name, in ORDER."""
    hit = {c for c, rx in STRONG_RE if rx.search(n)}
    return [c for c in ORDER if c in hit]


def classify(name):
    n = norm(name)
    if not n:
        return "other", "empty"
    for rx, cat in CHAIN_RE:
        m = rx.search(n)
        if m:
            if cat is None:  # chicken or pizza chains, decide by the matched text
                t = m.group(0)
                cat = "pizza" if re.search(r"pizza|domino|papa|franco|pieminister", t) else ("kebab" if "doner" in t else "chicken")
                if "pieminister" in t:
                    cat = "sandwich"
            return cat, "chain:" + m.group(0)
    fam = families(n)
    # pizza places that also sell kebabs: name order decides between the two
    if "pizza" in fam and "kebab" in fam:
        pk = n.find("pizz"); kk = min([i for i in (n.find("kebab"), n.find("doner"), n.find("turkish")) if i >= 0] or [99])
        first = "pizza" if pk < kk else "kebab"
        return first, "strong:pizza+kebab"
    if fam:
        return fam[0], "strong:" + "+".join(fam)
    for c, rx in WEAK_RE:
        if rx.search(n):
            return c, "weak:" + c
    if FISH_HINT.search(n):
        return "fish_chips", "hint:fish"
    return "other", "none"


# OpenStreetMap cuisine tags to the same families (first matching value wins)
OSM_MAP = {
    "fish_and_chips": "fish_chips", "fish": "fish_chips", "seafood": "fish_chips", "chips": "fish_chips",
    "indian": "indian", "curry": "indian", "bangladeshi": "indian", "nepalese": "indian", "pakistani": "indian", "sri_lankan": "indian", "punjabi": "indian", "balti": "indian", "south_indian": "indian", "tandoori": "indian",
    "chinese": "chinese", "cantonese": "chinese", "sichuan": "chinese", "dim_sum": "chinese", "oriental": "chinese",
    "pizza": "pizza",
    "kebab": "kebab", "turkish": "kebab", "doner": "kebab", "shawarma": "kebab", "kurdish": "kebab",
    "chicken": "chicken", "fried_chicken": "chicken", "wings": "chicken", "portuguese": "chicken", "peri_peri": "chicken",
    "burger": "burger", "american": "burger",
    "thai": "thai",
    "japanese": "japanese", "sushi": "japanese", "ramen": "japanese",
    "vietnamese": "asian_other", "korean": "asian_other", "asian": "asian_other", "malaysian": "asian_other", "noodle": "asian_other", "bubble_tea": "asian_other", "poke": "asian_other",
    "italian": "italian", "pasta": "italian",
    "caribbean": "caribbean", "jamaican": "caribbean", "african": "caribbean", "nigerian": "caribbean", "ethiopian": "caribbean",
    "mexican": "mexican", "tex-mex": "mexican", "burrito": "mexican", "tacos": "mexican",
    "greek": "greek_med", "lebanese": "greek_med", "mediterranean": "greek_med", "middle_eastern": "greek_med", "persian": "greek_med", "falafel": "greek_med", "syrian": "greek_med", "moroccan": "greek_med", "afghan": "greek_med",
    "sandwich": "sandwich", "bakery": "sandwich", "deli": "sandwich", "bagel": "sandwich", "pie": "sandwich", "pasty": "sandwich",
    "coffee_shop": "cafe", "cafe": "cafe", "breakfast": "cafe", "ice_cream": "cafe", "donut": "cafe", "dessert": "cafe", "tea": "cafe", "crepe": "cafe", "juice": "cafe",
}


def osm_family(cuisine):
    if not cuisine:
        return None
    for v in re.split(r"[;,]", cuisine.lower()):
        v = v.strip().replace(" ", "_")
        if v in OSM_MAP:
            return OSM_MAP[v]
    return "unmapped"


if __name__ == "__main__":
    for t in ["Golden Fry", "Bombay Spice", "Pizza & Kebab House", "Domino's Pizza", "Fish Bar and Chinese", "The Red Lion",
              "Happy Garden", "Chicken Cottage", "Greggs", "Taj Mahal", "Nando's", "Kebabish Original", "Costa Coffee"]:
        print(t, classify(t))


# ---------------------------- Identifier Prefixes --------------------------- #
HOST_PREFIX = "H"
ROUTER_PREFIX = "R"
LINK_PREFIX = "L"


# ----------------------------- Helper Functions ----------------------------- #
def is_host(identifier):
    return identifier.find(HOST_PREFIX) == 0


def is_router(identifier):
    return identifier.find(ROUTER_PREFIX) == 0


def is_link(identifier):
    return identifier.find(LINK_PREFIX) == 0

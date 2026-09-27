"""What one sitting of 334 asks for: products of one colour that are in stock, with their size
read out of JSON.

A third of the products have no size, so the NULL a missing key gives is on every seed."""

COLORS = ["red", "green", "blue", "black"]
ADJECTIVES = ["plain", "striped", "woollen", "linen", "padded", "light"]
NOUNS = ["shirt", "scarf", "jacket", "sock", "cap", "glove"]
SIZES = ["S", "M", "L", "XL"]


def brief(r):
    return {"color": r.choice(COLORS)}


def rows(r, b):
    products = []
    for i in range(1, 41):
        attrs = {"color": r.choice(COLORS), "stock": r.randint(0, 20)}
        if r.random() < 0.7:
            attrs["size"] = r.choice(SIZES)
        products.append(
            {
                "id": i,
                "name": f"{r.choice(ADJECTIVES)} {r.choice(NOUNS)} {i}",
                "price": f"{r.randrange(500, 9000) / 100:.2f}",
                "attrs": attrs,
            }
        )
    return {"products": products}

# Usability improvements

Four improvements, two on the front end and two in the agent/backend. Each one was chosen
after finding an actual problem in the running app, not from a list of good ideas — the
evidence for each is recorded below.

---

## Front end

### 1. Size availability on every product card, and an "available in my size" filter

**The problem.** The shop's whole pitch is that it tells you the truth about stock — the
About page says so in as many words. But the products grid showed no availability at all.
145 of the 612 inventory rows are zero, so a shopper could scroll the catalogue, pick
something, click through, and only then find out their size was gone. Every sold-out
discovery cost a page load.

**What I planned, and why I changed it.** I first intended a "Sold out" badge plus an
"In stock only" filter. Then I checked the data: **no product is sold out in every size**,
so that filter would have filtered nothing and the badge would never have appeared. What is
actually true is that **77 of 102 products have at least one size gone**. The useful
question is not "is this in stock" but "is this in stock *in my size*".

**What I built instead.** `GET /api/products` now returns per-product availability, and
each card shows a strip of six size pips — XS through XXL — with unavailable sizes greyed
and struck through. A **size filter** in the toolbar narrows the grid to products available
in one size. (The "Sold out" badge is still implemented for the all-gone case; it simply
does not fire against today's data, and will if stock drops.)

**Why it helps.** A shopper wearing an XL can see at a glance which of the 102 items they
can actually buy, without opening a single product page — and the filter cuts the grid to
the 77 that have it. For the business, it is the same honesty the chat agent practises,
applied to the part of the site most people actually use, and it steers shoppers toward
stock that can be sold.

**Verified:** the grid renders 612 pips, exactly matching the 612 inventory rows, with
exactly 145 struck through — the number of zero-quantity rows. Filtering by each size gives
75 / 78 / 80 / 78 / 77 / 79 products for XS–XXL, which matches
`SELECT size, COUNT(*) FROM inventory WHERE quantity > 0 GROUP BY size` exactly.

### 2. A phone-sized layout

**The problem.** At 375px the site was unusable in a specific way: the nav wrapped onto two
rows and ate about 230px before any content, the product grid dropped to one column with an
image nearly a full screen tall, and the floating chat button sat on top of the first card.
Getting to the second product took two full scrolls.

**What I added.** A set of breakpoints at 820px and 560px that:

- shrink the nav to a single compact row and tighten the wordmark
- put the product grid into two columns on a phone instead of one giant one
- let the chat panel fill the screen properly instead of being a fixed 370px box
- reduce heading sizes and page padding so content starts above the fold

**Why it helps.** Campus retail traffic is overwhelmingly phones — someone standing outside
the Broadway store, or in a dorm room. The old layout made browsing a hundred products on a
phone genuinely tedious; two columns and a compact header roughly triple the number of items
visible per screen.

---

## Agent and backend

### 3. Search that can filter on price and stock, and that reports how many it found

**The problem.** Asked *"What do you have for under $40?"*, the agent answered: *"These are
the items I found under $40"* and listed six. There are **25**. The phrasing implied it had
shown everything, because the tool gave it no way to know otherwise: `search_catalogue` had
no price filter and no notion of a total, so the agent matched on words, got its six, and
reported them as the answer. It was also free to return sold-out items as suggestions.

**What I added.** `search_catalogue` gained `max_price`, `min_price` and `in_stock_only`
arguments, and now returns a `SearchResults` object with counts alongside the capped list.
The prompt tells the agent to use the filters for budget questions and to say how many
matched when it is showing only some of them.

**A second bug this surfaced.** With one count, the agent answered *"13 in-stock items below
your budget"* — still wrong. It had searched the word "apparel", which matched 13; the count
reflected its own search words, not the price range. One number could not express both. So
`SearchResults` now returns two: `total_matches` (your words **and** the filters) and
`total_in_filters` (the filters alone). The agent is told to quote the second for a pure
budget question. It now answers **"There are 25 in-stock items in that price range. Here are
six"** — and 25 is what SQL says.

**Why it helps.** The shopper gets an accurate picture of what their budget buys rather than
a silent truncation that reads like a complete answer — the difference between believing
there are six options and knowing there are 25. Budget and stock filtering also happen in
SQL instead of by the model eyeballing a list, which is both more accurate and cheaper:
fewer wasted results in the context window, and no second search when the first one came
back full of things the shopper cannot buy.

### 4. The reply is checked before the shopper sees it

**The problem.** Two honesty holes. A `product_id` the agent invented was silently dropped
by `cards_for()`, so the shopper could read "we have these three hoodies" with only two
cards underneath and no explanation. And `unverified_prices()` — the check for dollar
figures that match no catalogue price — only wrote to the server log. Nothing stopped a
wrong number reaching the screen.

**What I added.** A PydanticAI `@agent.output_validator` that inspects every reply before it
is returned and raises `ModelRetry` when either check fails:

- a `product_id` that is not in the catalogue
- a dollar figure in the prose that matches no price in the catalogue

The agent is told what was wrong and gets to correct itself, with retries capped so a stuck
model cannot loop.

**Why it helps.** The honesty rules in the prompt are instructions, and instructions can be
drifted away from. This turns the two that matter most into something the system enforces
rather than requests. For the shopper, a price on screen is a price in the database. For the
business, the gap between "the agent said" and "the shop charges" closes.

**Verified:** driving the agent with a stub model that returned a made-up product — *"We
have the Velvet Bulldog Cape for $14"* — the validator rejected it, handed the model the
reason, and the corrected second answer cited a real product at a real price. Asked for 20%
off a $32 tee, and for the total on two $68 hoodies, the agent declined both rather than
produce a number the catalogue cannot back.

**Tradeoff, stated plainly.** The price check works on exact matches against known catalogue
prices, so if the agent ever adds two items into a total the validator will not recognise the
sum and will make it retry. That is the right way round — a false retry costs a moment, a
false price costs a customer — but it is a real constraint, and it is why the agent is told
not to do arithmetic on prices.

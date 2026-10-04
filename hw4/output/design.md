# Design

What changed to make the site feel like a real Campus Customs storefront, and why each
change should help someone stay and buy.

## Type

**EB Garamond** for headings, product names, prices and the wordmark; **Inter** for
everything you read quickly. A serif on the garment name and the price makes a $68 hoodie
read like a catalogue entry rather than a database row — which is the difference between
browsing a shop and querying a table. Headings jumped from 34px to 42px (56px in the hero)
so a page has an obvious first thing to look at.

## Colour

The old palette was two blues. It is now a six-step ladder — midnight, navy-deep, navy,
blue, blue-400, sky — plus a pale wash, so depth comes from the blues themselves instead of
from grey. Added **brass** (`#bd9b60`) as the one non-blue: the hairline under the nav, the
rule above a section heading, Dan's collar tag. Navy and brass is the colour pair of a
crest, and it signals "licensed, official" without anyone writing the word.

## Hierarchy

Eyebrow labels ("Officially licensed Yale apparel") are small brass caps; section headings
sit under a short brass rule. The hero has an italic turn — *the way you **actually**
dress* — which gives the sentence a voice. The effect is that each screen tells you where
to look first.

## Product presentation

Cards lift and the garment itself zooms slightly on hover, so the product responds to being
considered. The grid fades in staggered rather than snapping into place. On the item page the
image sits in a padded frame with a soft blue wash, the way clothing is shown on a wall
rather than in a spreadsheet. **Why it sells:** movement on hover is what makes a grid feel
browsable instead of listy, and the frame makes a $98 jacket look like it costs $98.

## Handsome Dan

The chat is no longer "the assistant" — it is **Handsome Dan**, the shop dog, drawn entirely
in HTML and CSS (no image file, so he is crisp at any size and costs nothing to load). He
appears in the wordmark, on the chat button, in the panel header, and beside every reply.
He blinks on a slow loop and his tongue appears while he is thinking; the loading indicator
is three bouncing paws rather than three dots.

His voice changed with his face: a shop dog who has watched twenty years of students come
through the door — warm, dry, unhurried. The prompt caps the dog at an occasional aside and
bans puns outright, and says plainly that **if the personality and the honesty rules ever
disagree, honesty wins**. A mascot that talks you into a sold-out size is worse than no
mascot.

**Why it sells:** a named character with a face is something people say hello to. It turns
"open the support widget" into "ask Dan", which is a much lower bar — and the questions he
answers (what does it cost, is my size there) are exactly the ones that otherwise end a
visit.

## Motion, with a brake

Hover lifts, image zoom, staggered grid, message pop-in, blinking. All of it is wrapped in
`@media (prefers-reduced-motion: reduce)`, which switches the lot off for anyone who has
asked their system for less animation.

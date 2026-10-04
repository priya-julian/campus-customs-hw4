import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <p className="eyebrow">Officially licensed Yale apparel</p>
          <h1>Wear the blue, the way you <em>actually</em> dress.</h1>
          <p>
            Campus Customs has outfitted New Haven since long before you got here. Crewnecks
            that survive a hundred wash cycles, hoodies built for a February walk down
            Prospect, and tees that look right whether you are headed to section or to the
            Bowl. No costume-shop spirit wear — just good blue clothes.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn">Shop the collection</Link>
            <Link to="/about" className="btn btn-outline">Who we are</Link>
          </div>
        </div>
      </section>

      <div className="page">
        <h2 className="rule-head">Why shop with us</h2>
        <p className="lede" style={{ marginBottom: 28 }}>
          We are a licensed Yale retailer on Broadway, which means every graphic on these
          garments is one the University actually approved.
        </p>
        <div className="features">
          <div className="feature">
            <h3>Straight answers on stock</h3>
            <p>
              Sizes run out, and we would rather say so. Every product page shows exactly what
              is left in each size, pulled live from the stockroom.
            </p>
          </div>
          <div className="feature">
            <h3>Licensed, not knocked off</h3>
            <p>
              Residential college crests, school marks, and team wordmarks are reproduced under
              license, so the details are correct down to the shield.
            </p>
          </div>
          <div className="feature">
            <h3>Ask before you buy</h3>
            <p>
              Not sure whether the crewneck or the quarter-zip is warmer? Open the chat in the
              corner and ask. It knows the catalogue, not a sales script.
            </p>
          </div>
        </div>
      </div>
    </>
  )
}

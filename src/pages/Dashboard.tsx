// import React from "react";
// import "./Dashboard.css";
// import { ExternalLink, Heart } from "lucide-react";
// import { useState } from "react";


// interface CompanyOffer {
//   id: string;
//   companyName: string;
//   companyLogo: string;
//   price: number;
//   originalPrice?: number;
//   rating: number;
//   reviewCount: number;
//   productUrl: string;
//   inStock: boolean;
// }

// const companies: CompanyOffer[] = [
//   {
//     id: "1",
//     companyName: "Amazon",
//     companyLogo: "https://logo.clearbit.com/amazon.com",
//     price: 199,
//     originalPrice: 299,
//     rating: 4.8,
//     reviewCount: 2456,
//     productUrl: "https://amazon.com",
//     inStock: true,
//   },
//   {
//     id: "2",
//     companyName: "Best Buy",
//     companyLogo: "https://logo.clearbit.com/bestbuy.com",
//     price: 209,
//     originalPrice: 299,
//     rating: 4.6,
//     reviewCount: 1823,
//     productUrl: "https://bestbuy.com",
//     inStock: true,
//   },
//   {
//     id: "3",
//     companyName: "Walmart",
//     companyLogo: "https://logo.clearbit.com/walmart.com",
//     price: 189,
//     originalPrice: 299,
//     rating: 4.7,
//     reviewCount: 3102,
//     productUrl: "https://walmart.com",
//     inStock: true,
//   },
//   {
//     id: "4",
//     companyName: "Target",
//     companyLogo: "https://logo.clearbit.com/target.com",
//     price: 219,
//     originalPrice: 299,
//     rating: 4.5,
//     reviewCount: 987,
//     productUrl: "https://target.com",
//     inStock: false,
//   },
// ];

// const defaultProduct = {
//   image: "src/assets/car.jpg",
//   name: "Sample Product",
//   category: "Electronics",
//   description:
//     "A short description of the sample product used for the dashboard preview.",
//   details: ["High quality materials", "2-year warranty", "Energy efficient"],
//   analytics: {
//     averagePrice: 199.99,
//     priceRange: { min: 149.99, max: 249.99 },
//     bestDeal: "$149.99 at Example Store",
//     priceChange: -4.5,
//   },
//   reviewVideo: "dQw4w9WgXcQ",
// } as const;

// export default function Dashboard() {
// const [liked, setLiked] = useState<Record<string, boolean>>({});
//   return (
//     <div className="dashboard-container">
//       {/* LEFT SIDE (UNCHANGED) */}
//       <div className="left-box">
//         <div className="product-image">
//           <img src={defaultProduct.image} />
//         </div>

//         <span className="category-badge">{defaultProduct.category}</span>
//         <h2 className="product-title">{defaultProduct.name}</h2>
//         <p className="product-desc">{defaultProduct.description}</p>

//         <hr className="divider" />

//         <h3 className="section-title">Product Details</h3>
//         <ul className="details-list">
//           {defaultProduct.details.map((item, i) => (
//             <li key={i}>
//               <span className="checkmark">✓</span> {item}
//             </li>
//           ))}
//         </ul>

//         <hr className="divider" />

//         <h3 className="section-title">Price Analytics</h3>
//         <div className="analytics-item">
//           <span>Average Price</span>
//           <span>${defaultProduct.analytics.averagePrice}</span>
//         </div>
//         <div className="analytics-item">
//           <span>Price Range</span>
//           <span>
//             ${defaultProduct.analytics.priceRange.min} - $
//             {defaultProduct.analytics.priceRange.max}
//           </span>
//         </div>
//         <div className="analytics-item">
//           <span>Best Deal</span>
//           <span className="best-deal">
//             {defaultProduct.analytics.bestDeal}
//           </span>
//         </div>
//         <div className="analytics-item">
//           <span>Price Trend</span>
//           <span className="trend">
//             {defaultProduct.analytics.priceChange}%
//           </span>
//         </div>

//         <hr className="divider" />

//         <h3 className="section-title">Product Review</h3>
//         <div className="video-frame">
//           <iframe
//             src={`https://www.youtube.com/embed/${defaultProduct.reviewVideo}`}
//             allowFullScreen
//           ></iframe>
//         </div>
//       </div>

//       {/* RIGHT SIDE (COMPARE PRICES) */}
//       <div className="compare-box">
//         <h1 className="compare-heading">Compare Prices</h1>
//         <p className="compare-subtext">
//           Find the best deal from {companies.length} retailers
//         </p>

//         {companies.map((c) => (
//           <div className="compare-card" key={c.id}>
//             <div className="compare-left">
//               <img src={c.companyLogo} className="compare-logo" />
//               <div>
//                 <div className="compare-name">{c.companyName}</div>
//                 {!c.inStock && (
//                   <span className="compare-out">Out of Stock</span>
//                 )}
//               </div>
//             </div>

//             <div className="compare-price">
//               <div className="price-main">${c.price}</div>
//               <div className="price-old">${c.originalPrice}</div>
//               <div className="price-off">
//                 {Math.round(
//                   ((c.originalPrice! - c.price) / c.originalPrice!) * 100
//                 )}
//                 % off
//               </div>
//             </div>

//             <div className="compare-rating">
//               ⭐⭐⭐⭐☆
//               <span>
//                 {c.rating} ({c.reviewCount} reviews)
//               </span>
//             </div>

//            <div className="compare-actions">
//   <button className="compare-btn">Add to Cart</button>

//   <button className="icon-btn">
//     <ExternalLink size={18} />
//   </button>

//  <button
//   className={`icon-btn ${liked[c.id] ? "liked" : ""}`}
//   onClick={() =>
//     setLiked((prev) => ({ ...prev, [c.id]: !prev[c.id] }))
//   }
// >
//   <Heart
//     size={18}
//     fill={liked[c.id] ? "#ef4444" : "none"}
//   />
// </button>
// </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }
import React, { useState } from "react";
import "./Dashboard.css";
import { ExternalLink, Heart, Star , MessageSquare  } from "lucide-react";




interface CompanyOffer {
  id: string;
  companyName: string;
  companyLogo: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviewCount: number;
  productUrl: string;
  inStock: boolean;
}

interface Review {
  id: string;
  userName: string;
  userAvatar?: string;
  rating: number;
  comment: string;
  date: string;
  source: string;
  verified: boolean;
}


const companies: CompanyOffer[] = [
  {
    id: "1",
    companyName: "Amazon",
    companyLogo: "https://logo.clearbit.com/amazon.com",
    price: 199,
    originalPrice: 299,
    rating: 4.8,
    reviewCount: 2456,
    productUrl: "https://amazon.com",
    inStock: true,
  },
  {
    id: "2",
    companyName: "Best Buy",
    companyLogo: "https://logo.clearbit.com/bestbuy.com",
    price: 209,
    originalPrice: 299,
    rating: 4.6,
    reviewCount: 1823,
    productUrl: "https://bestbuy.com",
    inStock: true,
  },
  {
    id: "3",
    companyName: "Walmart",
    companyLogo: "https://logo.clearbit.com/walmart.com",
    price: 189,
    originalPrice: 299,
    rating: 4.7,
    reviewCount: 3102,
    productUrl: "https://walmart.com",
    inStock: true,
  },
  {
    id: "4",
    companyName: "Target",
    companyLogo: "https://logo.clearbit.com/target.com",
    price: 219,
    originalPrice: 299,
    rating: 4.5,
    reviewCount: 987,
    productUrl: "https://target.com",
    inStock: false,
  },
];

const reviews: Review[] = [
  {
    id: "1",
    userName: "John Smith",
    userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
    rating: 5,
    comment:
      "Absolutely amazing headphones! The noise cancellation is top-notch and battery life exceeds expectations. Worth every penny.",
    date: "January 15, 2024",
    source: "Amazon",
    verified: true,
  },
  {
    id: "2",
    userName: "Sarah Johnson",
    userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
    rating: 4,
    comment:
      "Great sound quality and comfortable for long listening sessions. Only minor issue is the case could be more compact.",
    date: "January 10, 2024",
    source: "Best Buy",
    verified: true,
  },
  {
    id: "3",
    userName: "Michael Chen",
    userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Michael",
    rating: 5,
    comment:
      "Best headphones I've owned. The audio is crystal clear and the ANC blocks out everything.",
    date: "January 8, 2024",
    source: "Walmart",
    verified: true,
  },
   {
      id: "4",
      userName: "Emily Rodriguez",
      userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Emily",
      rating: 4,
      comment: "Excellent build quality and sound. The companion app is intuitive. Would give 5 stars but they're a bit tight on larger heads.",
      date: "2024-01-05",
      source: "Target",
      verified: false
    },
    {
      id: "5",
      userName: "David Park",
      userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=David",
      rating: 5,
      comment: "Professional grade headphones at a consumer price. Using them daily for music production and they're phenomenal.",
      date: "2024-01-02",
      source: "Amazon",
      verified: true
    },
];

const defaultProduct = {
  image: "src/assets/car.jpg",
  name: "Sample Product",
  category: "Electronics",
  description:
    "A short description of the sample product used for the dashboard preview.",
  details: ["High quality materials", "2-year warranty", "Energy efficient"],
  analytics: {
    averagePrice: 199.99,
    priceRange: { min: 149.99, max: 249.99 },
    bestDeal: "$149.99 at Example Store",
    priceChange: -4.5,
  },
  reviewVideo: "dQw4w9WgXcQ",
} as const;

export default function Dashboard() {
  const [liked, setLiked] = useState<Record<string, boolean>>({});

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        size={14}
        className={
          i < Math.round(rating)
            ? "star-filled"
            : "star-empty"
        }
      />
    ));
  };

  return (
    <div className="dashboard-container">
      {/* LEFT SIDE */}
      <div className="left-box">
        <div className="product-image">
          <img src={defaultProduct.image} />
        </div>

        <span className="category-badge">{defaultProduct.category}</span>
        <h2 className="product-title">{defaultProduct.name}</h2>
        <p className="product-desc">{defaultProduct.description}</p>

        <hr className="divider" />

        <h3 className="section-title">Product Details</h3>
        <ul className="details-list">
          {defaultProduct.details.map((item, i) => (
            <li key={i}>
              <span className="checkmark">✓</span> {item}
            </li>
          ))}
        </ul>

        <hr className="divider" />

        <h3 className="section-title">Price Analytics</h3>
        <div className="analytics-item">
          <span>Average Price</span>
          <span>${defaultProduct.analytics.averagePrice}</span>
        </div>
        <div className="analytics-item">
          <span>Price Range</span>
          <span>
            ${defaultProduct.analytics.priceRange.min} - $
            {defaultProduct.analytics.priceRange.max}
          </span>
        </div>
        <div className="analytics-item">
          <span>Best Deal</span>
          <span className="best-deal">
            {defaultProduct.analytics.bestDeal}
          </span>
        </div>
        <div className="analytics-item">
          <span>Price Trend</span>
          <span className="trend">
            {defaultProduct.analytics.priceChange}%
          </span>
        </div>

        <hr className="divider" />

        <h3 className="section-title">Product Review</h3>
        <div className="video-frame">
          <iframe
            src={`https://www.youtube.com/embed/${defaultProduct.reviewVideo}`}
            allowFullScreen
          ></iframe>
        </div>
      </div>

      {/* RIGHT SIDE */}
      <div className="compare-box">
        <h1 className="compare-heading">Compare Prices</h1>
        <p className="compare-subtext">
          Find the best deal from {companies.length} retailers
        </p>

        {companies.map((c) => (
          <div className="compare-card" key={c.id}>
            <div className="compare-left">
              <img src={c.companyLogo} className="compare-logo" />
              <div>
                <div className="compare-name">{c.companyName}</div>
                {!c.inStock && (
                  <span className="compare-out">Out of Stock</span>
                )}
              </div>
            </div>

            <div className="compare-price">
              <div className="price-main">${c.price}</div>
              <div className="price-old">${c.originalPrice}</div>
              <div className="price-off">
                {Math.round(
                  ((c.originalPrice! - c.price) / c.originalPrice!) * 100
                )}
                % off
              </div>
            </div>

            <div className="compare-rating">
              <div className="stars">{renderStars(c.rating)}</div>
              <span>
                {c.rating} ({c.reviewCount} reviews)
              </span>
            </div>

            <div className="compare-actions">
              <button className="compare-btn">Add to Cart</button>

              <button
                className="icon-btn"
                onClick={() => window.open(c.productUrl, "_blank")}
              >
                <ExternalLink size={18} />
              </button>

              <button
                className={`icon-btn ${liked[c.id] ? "liked" : ""}`}
                onClick={() =>
                  setLiked((prev) => ({
                    ...prev,
                    [c.id]: !prev[c.id],
                  }))
                }
              >
                <Heart
                  size={18}
                  fill={liked[c.id] ? "#ef4444" : "none"}
                />
              </button>
            </div>
          </div>
        ))}

       {/* CUSTOMER REVIEWS */}
<div className="reviews-section">
  <h2 className="reviews-heading">Customer Reviews</h2>
  <p className="reviews-subtext">
    Read what customers are saying from different retailers
  </p>

  {reviews.map((r) => (
    <div className="review-card" key={r.id}>
      <div className="review-header">
        <img src={r.userAvatar} className="review-avatar" />

        <div className="review-meta">
          <div className="review-name-row">
            <span className="review-name">{r.userName}</span>
            {r.verified && (
              <span className="review-verified">Verified Purchase</span>
            )}
          </div>

          <div className="review-rating-row">
            <div className="review-stars">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  size={14}
                  className={
                    i < r.rating ? "star-filled" : "star-empty"
                  }
                />
              ))}
            </div>

            <span className="review-dot">•</span>
            <span className="review-date">{r.date}</span>
            <span className="review-dot">•</span>
            <span className="review-source">{r.source}</span>
          </div>
        </div>
      </div>

      <p className="review-text">{r.comment}</p>
    </div>
  ))}
</div>

      </div>
    </div>
  );
}

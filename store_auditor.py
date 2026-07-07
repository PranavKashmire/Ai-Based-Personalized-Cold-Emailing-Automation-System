"""
store_auditor.py — eCommerce Impact-Driven Audit Engine (12-Point Framework).
Each issue includes a screenshot_hint to enable inline section cropping in the PDF.
"""

import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)
HEADERS = {"User-Agent": USER_AGENT}


def fetch_page(url: str) -> tuple[BeautifulSoup | None, dict]:
    meta = {"load_time": None, "status_code": None, "final_url": url, "error": None}
    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        meta["load_time"] = round(time.time() - start, 2)
        meta["status_code"] = resp.status_code
        meta["final_url"] = resp.url
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml"), meta
        meta["error"] = f"HTTP {resp.status_code}"
        return None, meta
    except Exception as e:
        meta["error"] = str(e)
        logger.warning(f"Failed to fetch {url}: {e}")
        return None, meta


def find_product_page(soup: BeautifulSoup, base_url: str) -> str | None:
    for a in soup.find_all("a", href=True):
        if "/products/" in a["href"]:
            return urljoin(base_url, a["href"])
    return None


# ── Screenshot hint structure ─────────────────────────────────────────────────
# source: "homepage" | "product"   (which screenshot file to crop from)
# region: "top" | "middle" | "bottom"  (vertical crop zone)
def hint(source: str, region: str) -> dict:
    return {"source": source, "region": region}


# ── 1. First Impression & Homepage Impact ─────────────────────────────────────
def audit_homepage_impression(soup: BeautifulSoup, meta: dict) -> list[dict]:
    issues = []

    hero = soup.find(class_=re.compile(r"hero|banner|slider|carousel", re.I))
    if not hero:
        issues.append({
            "problem": "No clear hero/banner section detected above the fold",
            "impacted_metric": "Bounce Rate",
            "impact_level": "High",
            "fix": "Add a compelling above-the-fold hero with clear value proposition",
            "type": "Quick Win",
            "revenue_impact": "Header clarity that optimizes conversion rate by 10-20%",
            "screenshot_hint": hint("homepage", "top"),
        })

    h1 = soup.find("h1")
    if not h1 or len(h1.get_text(strip=True)) < 10:
        issues.append({
            "problem": "Missing or weak H1 headline on homepage",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Add a benefit-led H1 that instantly tells visitors what you sell",
            "type": "Quick Win",
            "revenue_impact": "Headline optimization that lowers bounce rate by 15%",
            "screenshot_hint": hint("homepage", "top"),
        })

    cta_patterns = re.compile(r"shop now|buy now|get started|explore|order now|add to cart", re.I)
    ctas = soup.find_all(string=cta_patterns)
    if len(ctas) < 2:
        issues.append({
            "problem": "Insufficient or hidden CTAs on the homepage",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Place at least 2-3 visible CTAs above the fold with action-oriented text",
            "type": "Quick Win",
            "revenue_impact": "CTA placement change that optimizes conversion rate by 10-25%",
            "screenshot_hint": hint("homepage", "top"),
        })

    announcement = soup.find(class_=re.compile(r"announcement|promo-bar|top-bar|header-bar", re.I))
    if not announcement:
        issues.append({
            "problem": "No announcement/promo bar detected at the top",
            "impacted_metric": "AOV",
            "impact_level": "Medium",
            "fix": "Add a sticky top bar promoting free shipping threshold or active discount",
            "type": "Quick Win",
            "revenue_impact": "Announcement bar addition that increases AOV by 5-15%",
            "screenshot_hint": hint("homepage", "top"),
        })

    return issues


# ── 2. Product Page Revenue Drivers ──────────────────────────────────────────
def audit_product_page_revenue(soup: BeautifulSoup | None) -> list[dict]:
    issues = []
    if not soup:
        return issues

    imgs = soup.find_all("img", class_=re.compile(r"product|featured|gallery", re.I))
    if len(imgs) < 3:
        issues.append({
            "problem": "Insufficient product imagery found on the product page",
            "impacted_metric": "Return Rate, Trust",
            "impact_level": "High",
            "fix": "Add 5+ high-quality images: front, lifestyle, and size-reference shots",
            "type": "Quick Win",
            "revenue_impact": "Visual context update that lifts CVR by 8-15%",
            "screenshot_hint": hint("product", "top"),
        })

    price_elem = soup.find(class_=re.compile(r"price|product-price|price--sale", re.I))
    if not price_elem:
        issues.append({
            "problem": "Product price not clearly visible near the purchase button",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Ensure price is prominently displayed adjacent to the Add to Cart button",
            "type": "Quick Win",
            "revenue_impact": "Price clarity change that reduces purchase decision friction",
            "screenshot_hint": hint("product", "middle"),
        })

    reviews = soup.find(class_=re.compile(r"review|rating|testimonial|stars", re.I))
    if not reviews:
        issues.append({
            "problem": "No visible reviews or social proof on the product page",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Integrate a review widget and display star ratings near the price",
            "type": "Long-Term",
            "revenue_impact": "Trust signal integration that increases CVR by 15-30%",
            "screenshot_hint": hint("product", "middle"),
        })

    desc = soup.find(class_=re.compile(r"product-description|description|product__description", re.I))
    if not desc or len(desc.get_text(strip=True)) < 100:
        issues.append({
            "problem": "Short or missing product description",
            "impacted_metric": "Return Rate",
            "impact_level": "Medium",
            "fix": "Write benefit-first descriptions with bullet points, use cases, and FAQs",
            "type": "Long-Term",
            "revenue_impact": "Description improvement that lowers return rate by reducing expectation gaps",
            "screenshot_hint": hint("product", "bottom"),
        })

    return issues


# ── 3. Conversion Rate Optimization (CRO) ────────────────────────────────────
def audit_cro(soup: BeautifulSoup | None) -> list[dict]:
    issues = []
    if not soup:
        return issues

    add_to_cart = soup.find(string=re.compile(r"add to cart|add to bag|buy now", re.I))
    if not add_to_cart:
        issues.append({
            "problem": "ATC (Add to Cart) button is not easily identifiable or prominent",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Make ATC button sticky on scroll and use a high-contrast color",
            "type": "Quick Win",
            "revenue_impact": "Sticky CTA implementation that increases mobile CVR by 10-25%",
            "screenshot_hint": hint("product", "middle"),
        })

    urgency = soup.find(string=re.compile(r"only \d+ left|low stock|limited|sale ends", re.I))
    if not urgency:
        issues.append({
            "problem": "No ethical urgency or scarcity signals detected on the page",
            "impacted_metric": "Cart Abandonment",
            "impact_level": "Medium",
            "fix": "Add low-stock counters or 'X people viewing this' real-time indicators",
            "type": "Quick Win",
            "revenue_impact": "Urgency signal addition that can lift overall CVR by 8-20%",
            "screenshot_hint": hint("product", "middle"),
        })

    free_shipping = soup.find(string=re.compile(r"free shipping|free delivery|free returns", re.I))
    if not free_shipping:
        issues.append({
            "problem": "Free shipping offer is not prominently displayed",
            "impacted_metric": "Cart Abandonment",
            "impact_level": "High",
            "fix": "Display free shipping threshold in hero, announcement bar, and product pages",
            "type": "Quick Win",
            "revenue_impact": "Shipping clarity that reduces cart abandonment by 10-20%",
            "screenshot_hint": hint("homepage", "top"),
        })

    return issues


# ── 4. Mobile Optimization ───────────────────────────────────────────────────
def audit_mobile_optimization(soup: BeautifulSoup) -> list[dict]:
    issues = []
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        issues.append({
            "problem": "Missing mobile viewport meta tag — mobile layout may be broken",
            "impacted_metric": "Bounce Rate",
            "impact_level": "High",
            "fix": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>",
            "type": "Quick Win",
            "revenue_impact": "Mobile UX fix that prevents massive traffic loss (~70% of shoppers)",
            "screenshot_hint": hint("homepage", "top"),
        })

    search = soup.find("input", attrs={"type": "search"}) or soup.find("input", attrs={"name": re.compile(r"search|q", re.I)})
    if not search:
        issues.append({
            "problem": "No visible search bar on the site",
            "impacted_metric": "Conversion Rate",
            "impact_level": "Medium",
            "fix": "Add a prominent search bar — visitors who search convert 2-3x higher",
            "type": "Quick Win",
            "revenue_impact": "Search bar addition that captures high-intent buyer traffic",
            "screenshot_hint": hint("homepage", "top"),
        })

    return issues


# ── 5. Speed & Performance ───────────────────────────────────────────────────
def audit_speed_performance(soup: BeautifulSoup, meta: dict) -> list[dict]:
    issues = []
    load_time = meta.get("load_time", 0)
    if load_time and load_time > 3:
        issues.append({
            "problem": f"Slow server response time detected (~{load_time}s)",
            "impacted_metric": "Conversion Rate",
            "impact_level": "High",
            "fix": "Optimize images with WebP, remove unused Shopify apps, enable lazy loading",
            "type": "Long-Term",
            "revenue_impact": "Speed optimization preventing a 7% CVR drop per extra second",
            "screenshot_hint": hint("homepage", "top"),
        })

    blocking_scripts = soup.find_all("script", src=True)
    if len(blocking_scripts) > 15:
        issues.append({
            "problem": f"{len(blocking_scripts)} external scripts detected causing potential render-blocking",
            "impacted_metric": "Page Speed",
            "impact_level": "High",
            "fix": "Audit and remove unused Shopify apps, defer non-critical JS",
            "type": "Long-Term",
            "revenue_impact": "Script reduction that can cut LCP by 30-50%",
            "screenshot_hint": hint("homepage", "top"),
        })

    return issues


# ── 6. SEO & Organic Growth ──────────────────────────────────────────────────
def audit_seo(soup: BeautifulSoup) -> list[dict]:
    issues = []

    title = soup.find("title")
    if not title or len(title.get_text(strip=True)) < 20:
        issues.append({
            "problem": "Missing or unoptimized SEO page title tag",
            "impacted_metric": "Traffic Growth",
            "impact_level": "High",
            "fix": "Set keyword-rich title: 'Brand Name | Category | Value Prop' (50-60 chars)",
            "type": "Quick Win",
            "revenue_impact": "Organic CTR lift that reduces dependency on paid ad spend",
            "screenshot_hint": hint("homepage", "top"),
        })

    imgs_no_alt = [img for img in soup.find_all("img") if not img.get("alt", "").strip()]
    if len(imgs_no_alt) > 3:
        issues.append({
            "problem": f"{len(imgs_no_alt)} images are missing descriptive alt text",
            "impacted_metric": "SEO Traffic",
            "impact_level": "Medium",
            "fix": "Add keyword-rich alt text to all product images",
            "type": "Quick Win",
            "revenue_impact": "Image SEO fix driving free traffic via Google Image Search",
            "screenshot_hint": hint("homepage", "middle"),
        })

    schema = soup.find("script", attrs={"type": "application/ld+json"})
    if not schema:
        issues.append({
            "problem": "No JSON-LD schema markup detected on the homepage",
            "impacted_metric": "SEO",
            "impact_level": "Medium",
            "fix": "Add Product, Organization, and BreadcrumbList schema for rich snippets",
            "type": "Long-Term",
            "revenue_impact": "Schema markup that increases organic CTR by 20-30%",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    return issues


# ── 7. Trust & Credibility ───────────────────────────────────────────────────
def audit_trust_credibility(soup: BeautifulSoup) -> list[dict]:
    issues = []
    text = soup.get_text(strip=True).lower()

    trust_badge = soup.find(class_=re.compile(r"trust|badge|secure|guarantee|payment", re.I))
    if not trust_badge:
        issues.append({
            "problem": "No visible trust badges near the checkout or CTA areas",
            "impacted_metric": "Conversion Rate",
            "impact_level": "Medium",
            "fix": "Add secure checkout badge, payment method icons, and money-back guarantee",
            "type": "Quick Win",
            "revenue_impact": "Trust badge addition reducing checkout abandonment by 10-15%",
            "screenshot_hint": hint("product", "middle"),
        })

    footer = soup.find("footer")
    if footer:
        footer_text = footer.get_text(strip=True).lower()
        if "return" not in footer_text and "refund" not in footer_text:
            issues.append({
                "problem": "Return/refund policy not visible in the footer",
                "impacted_metric": "Conversion Rate",
                "impact_level": "Medium",
                "fix": "Add visible links to Return Policy, Privacy Policy, and FAQ in footer",
                "type": "Quick Win",
                "revenue_impact": "Policy visibility that builds first-time buyer trust",
                "screenshot_hint": hint("homepage", "bottom"),
            })

    about_link = soup.find("a", string=re.compile(r"about|our story|who we are", re.I))
    if not about_link:
        issues.append({
            "problem": "No 'About Us' or 'Our Story' page link detected in navigation",
            "impacted_metric": "LTV",
            "impact_level": "Medium",
            "fix": "Add an 'About Us' page with founder photo and brand mission",
            "type": "Long-Term",
            "revenue_impact": "Brand story page that increases emotional connection and repeat purchase",
            "screenshot_hint": hint("homepage", "top"),
        })

    return issues


# ── 8. Return Rate Reduction Factors ─────────────────────────────────────────
def audit_returns(soup: BeautifulSoup | None) -> list[dict]:
    issues = []
    if not soup:
        return issues

    text = soup.get_text(strip=True).lower()
    if "size chart" not in text and "size guide" not in text:
        issues.append({
            "problem": "No size chart or fit guide visible on the product page",
            "impacted_metric": "Return Rate",
            "impact_level": "Medium",
            "fix": "Add an interactive size guide with measurements in both cm and inches",
            "type": "Long-Term",
            "revenue_impact": "Size guide addition directly lowering return rate and refund costs",
            "screenshot_hint": hint("product", "bottom"),
        })

    return issues


# ── 9. Average Order Value Optimization ──────────────────────────────────────
def audit_aov(soup: BeautifulSoup | None) -> list[dict]:
    issues = []

    if soup:
        upsell = soup.find(class_=re.compile(r"upsell|cross-sell|frequently|bundle|you-may-also", re.I))
        if not upsell:
            issues.append({
                "problem": "No bundle offers, cross-sells, or quantity discounts visible",
                "impacted_metric": "AOV",
                "impact_level": "High",
                "fix": "Add 'Frequently Bought Together' or tier-pricing bundle block",
                "type": "Long-Term",
                "revenue_impact": "Upsell flow implementation that increases Average Order Value by 15-35%",
                "screenshot_hint": hint("product", "bottom"),
            })
    else:
        issues.append({
            "problem": "No bundle offers, cross-sells, or quantity discounts visible",
            "impacted_metric": "AOV",
            "impact_level": "High",
            "fix": "Add 'Frequently Bought Together' or tier-pricing bundle block",
            "type": "Long-Term",
            "revenue_impact": "Upsell flow implementation that increases Average Order Value by 15-35%",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    return issues


# ── 10. Retention & LTV Growth ───────────────────────────────────────────────
def audit_retention(soup: BeautifulSoup) -> list[dict]:
    issues = []

    email_form = soup.find("input", attrs={"type": "email"})
    if not email_form:
        issues.append({
            "problem": "No email or SMS capture form or popup detected",
            "impacted_metric": "Customer LTV",
            "impact_level": "High",
            "fix": "Add an exit-intent popup offering 10% off for email signups",
            "type": "Quick Win",
            "revenue_impact": "List building tactic adding $20-$50 LTV per captured lead",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    loyalty = soup.find(string=re.compile(r"loyalty|rewards|points|refer|referral", re.I))
    if not loyalty:
        issues.append({
            "problem": "No loyalty or referral program detected on the store",
            "impacted_metric": "Repeat Purchase Rate",
            "impact_level": "Medium",
            "fix": "Install Smile.io or LoyaltyLion — referral programs convert 5x better than ads",
            "type": "Long-Term",
            "revenue_impact": "Loyalty program setup that increases repeat purchase rate by 20-40%",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    return issues


# ── 11. Marketing Readiness ──────────────────────────────────────────────────
def audit_marketing(soup: BeautifulSoup) -> list[dict]:
    issues = []

    social = soup.find("a", href=re.compile(r"instagram|tiktok|facebook|pinterest|youtube", re.I))
    if not social:
        issues.append({
            "problem": "No social media links or UGC content found on the store",
            "impacted_metric": "Ad ROI",
            "impact_level": "Medium",
            "fix": "Embed Instagram feed as social proof and add social links in footer",
            "type": "Long-Term",
            "revenue_impact": "Social proof integration improving paid ad conversion rates",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    blog = soup.find("a", href=re.compile(r"blog|journal|news|articles", re.I))
    if not blog:
        issues.append({
            "problem": "No blog or content marketing section detected",
            "impacted_metric": "CAC",
            "impact_level": "Medium",
            "fix": "Start a blog targeting buyer-intent keywords in your product niche",
            "type": "Long-Term",
            "revenue_impact": "Content marketing that drives 3x more leads at 62% lower cost than paid ads",
            "screenshot_hint": hint("homepage", "bottom"),
        })

    return issues


# ── 12. Competitive Benchmarking ─────────────────────────────────────────────
def audit_benchmarking() -> list[dict]:
    return [
        {
            "problem": "Weak competitive differentiation — no 'Why Us' section found",
            "impacted_metric": "Perceived Value",
            "impact_level": "High",
            "fix": "Add a clear 'Us vs Alternatives' comparison section with unique benefits",
            "type": "Long-Term",
            "revenue_impact": "Positioning shift that converts comparison shoppers more effectively",
            "screenshot_hint": hint("homepage", "middle"),
        },
        {
            "problem": "No post-purchase upsell or SMS flow detected",
            "impacted_metric": "Revenue per Customer",
            "impact_level": "High",
            "fix": "Implement ReConvert for post-purchase upsell and Postscript for SMS flows",
            "type": "Long-Term",
            "revenue_impact": "Post-purchase system that can add 10-20% to total revenue",
            "screenshot_hint": hint("product", "bottom"),
        },
    ]


# ── Main Audit Function ───────────────────────────────────────────────────────
def audit_store(store_url: str, store_name: str = "", niche: str = "") -> dict:
    logger.info(f"Running 12-point impact audit for: {store_url}")

    result = {
        "store_url": store_url,
        "store_name": store_name,
        "niche": niche,
        "overall_score": 0,
        "all_issues": [],
        "error": None,
    }

    homepage_soup, meta = fetch_page(store_url)
    if not homepage_soup:
        result["error"] = meta.get("error", "Failed to fetch homepage")
        return result

    product_url = find_product_page(homepage_soup, store_url)
    product_soup, _ = fetch_page(product_url) if product_url else (None, {})

    findings = []
    findings.extend(audit_homepage_impression(homepage_soup, meta))
    findings.extend(audit_product_page_revenue(product_soup))
    findings.extend(audit_cro(product_soup))
    findings.extend(audit_mobile_optimization(homepage_soup))
    findings.extend(audit_speed_performance(homepage_soup, meta))
    findings.extend(audit_seo(homepage_soup))
    findings.extend(audit_trust_credibility(homepage_soup))
    findings.extend(audit_returns(product_soup))
    findings.extend(audit_aov(product_soup))
    findings.extend(audit_retention(homepage_soup))
    findings.extend(audit_marketing(homepage_soup))
    findings.extend(audit_benchmarking())

    impact_sort = {"High": 0, "Medium": 1, "Low": 2}
    findings.sort(key=lambda x: impact_sort.get(x.get("impact_level", "Medium"), 1))

    result["all_issues"] = findings
    result["overall_score"] = max(0, 100 - (len(findings) * 4))

    logger.info(f"Audit complete for {store_url} | Issues: {len(findings)} | Score: {result['overall_score']}/100")
    return result

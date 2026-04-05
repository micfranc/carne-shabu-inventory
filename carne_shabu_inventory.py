import streamlit as st
import pandas as pd
from datetime import datetime
import json
from supabase import create_client, Client

st.set_page_config(page_title="Carne Shabu · Inventory", page_icon="🥩", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0e0a06; color: #f0ead6; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.main-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 900; color: #f0ead6; letter-spacing: -1px; line-height: 1; }
.sub-title { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c4984a; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 0.5rem; }
.flavor-card { background: #1a1208; border: 1px solid #2e1f0a; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem; }
.bag-count { font-family: 'Playfair Display', serif; font-size: 2.75rem; font-weight: 900; color: #c4984a; line-height: 1; }
.bag-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #7a6040; text-transform: uppercase; letter-spacing: 2px; }
.flavor-name { font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 600; color: #f0ead6; margin-bottom: 0.15rem; }
.cook-card { background: #12100a; border: 1px solid #2e1f0a; border-left: 3px solid #e05c2a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; }
.cook-need { font-family: 'Playfair Display', serif; font-size: 1.75rem; font-weight: 900; color: #e05c2a; line-height: 1; }
.cook-have { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #7a6040; }
.section-header { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c4984a; letter-spacing: 3px; text-transform: uppercase; border-bottom: 1px solid #2e1f0a; padding-bottom: 0.5rem; margin: 1.5rem 0 1rem 0; }
.order-card { background: #120e08; border: 1px solid #2e1f0a; border-left: 3px solid #c4984a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.6rem; }
.order-customer { font-family: 'Playfair Display', serif; font-size: 1rem; color: #f0ead6; font-weight: 700; }
.order-date { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #7a6040; letter-spacing: 0.5px; line-height: 1.6; }
.order-details { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: #a08060; margin-top: 0.25rem; }
.total-badge { background: #c4984a22; border: 1px solid #c4984a44; border-radius: 20px; padding: 0.15rem 0.65rem; font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c4984a; display: inline-block; margin-top: 0.4rem; }
.divider { border: none; border-top: 1px solid #2e1f0a; margin: 1rem 0; }

/* ── Inputs ── */
div[data-testid="stNumberInput"] input { background: #1a1208 !important; border: 1px solid #2e1f0a !important; color: #f0ead6 !important; font-family: 'DM Mono', monospace !important; border-radius: 8px !important; font-size: 1rem !important; min-height: 44px !important; }
div[data-testid="stTextInput"] input { background: #1a1208 !important; border: 1px solid #2e1f0a !important; color: #f0ead6 !important; border-radius: 8px !important; font-size: 1rem !important; min-height: 44px !important; }
div[data-testid="stSelectbox"] select, div[data-testid="stSelectbox"] > div { background: #1a1208 !important; border: 1px solid #2e1f0a !important; color: #f0ead6 !important; border-radius: 8px !important; min-height: 44px !important; }

/* ── Buttons — big tap targets ── */
.stButton > button { 
    background: #c4984a !important; color: #0e0a06 !important; border: none !important; 
    font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; 
    letter-spacing: 2px !important; text-transform: uppercase !important; 
    border-radius: 8px !important; padding: 0.65rem 1.25rem !important; 
    font-weight: 500 !important; min-height: 44px !important; width: 100% !important;
}

/* ── Labels ── */
div[data-testid="stVerticalBlock"] label { color: #a08060 !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 1px !important; }

/* ── Tabs — bigger on mobile ── */
.stTabs [data-baseweb="tab"] { font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important; padding: 0.5rem 0.4rem !important; }
.stTabs [data-baseweb="tab-list"] { background: #0e0a06 !important; border-bottom: 1px solid #2e1f0a !important; gap: 0 !important; }
.stTabs [aria-selected="true"] { color: #c4984a !important; border-bottom: 2px solid #c4984a !important; }

/* ── Checkbox — bigger tap target ── */
[data-testid="stCheckbox"] { min-height: 44px !important; display: flex !important; align-items: center !important; }
[data-testid="stCheckbox"] label { font-size: 0.9rem !important; }

/* ── Mobile: single column, remove side padding ── */
@media (max-width: 768px) {
    .main-title { font-size: 2rem !important; }
    .block-container { padding: 1rem 0.75rem !important; max-width: 100% !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.6rem !important; padding: 0.4rem 0.25rem !important; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    .stButton > button { font-size: 0.7rem !important; padding: 0.6rem 0.75rem !important; }
    .order-date { font-size: 0.58rem !important; }
    .bag-count { font-size: 2.25rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()

DEFAULT_FLAVORS = ["Truffle Sea Salt", "Lemon Pepper", "Spicy Lemon Pepper", "Ghost Pepper"]
FLAVOR_MAP = {
    "truffle sea salt": "Truffle Sea Salt", "lemon pepper": "Lemon Pepper",
    "lemon pep": "Lemon Pepper", "spicy lemon pepper": "Spicy Lemon Pepper",
    "spicy lemon pep": "Spicy Lemon Pepper", "ghost pepper": "Ghost Pepper", "ghost pep": "Ghost Pepper",
}

PACK_MAP = {
    "Truffle Sea Salt - 1-Pack": {"Truffle Sea Salt": 1},
    "Lemon Pepper - 1-Pack": {"Lemon Pepper": 1},
    "Spicy Lemon Pepper - 1-Pack": {"Spicy Lemon Pepper": 1},
    "Ghost Pepper - 1-Pack": {"Ghost Pepper": 1},
    "Truffle Sea Salt - 4-Pack": {"Truffle Sea Salt": 4},
    "Lemon Pepper - 4-Pack": {"Lemon Pepper": 4},
    "Spicy Lemon Pepper - 4-Pack": {"Spicy Lemon Pepper": 4},
    "Ghost Pepper - 4-Pack": {"Ghost Pepper": 4},
    "Truffle Sea Salt - 8-Pack": {"Truffle Sea Salt": 8},
    "Lemon Pepper - 8-Pack": {"Lemon Pepper": 8},
    "Spicy Lemon Pepper - 8-Pack": {"Spicy Lemon Pepper": 8},
    "Ghost Pepper - 8-Pack": {"Ghost Pepper": 8},
    "Variety Pack": {"Truffle Sea Salt": 1, "Lemon Pepper": 1, "Spicy Lemon Pepper": 1, "Ghost Pepper": 1},
}

def normalize_flavor(raw):
    return FLAVOR_MAP.get(str(raw).strip().lower(), str(raw).strip())

def parse_shopify_product(product_name, line_qty=1):
    """Convert Shopify product name + quantity into {flavor: bags}."""
    product_name = product_name.strip()
    if product_name in PACK_MAP:
        return {f: q * line_qty for f, q in PACK_MAP[product_name].items()}
    for flavor in DEFAULT_FLAVORS:
        if flavor.lower() in product_name.lower():
            return {flavor: line_qty}
    return {}

def parse_shopify_csv(df):
    """Parse Shopify orders export CSV into order dicts.
    Handles multi-row orders (one row per line item)."""
    orders_dict = {}
    cur_customer = cur_status = cur_fulfillment = cur_date = cur_location = None

    for _, row in df.iterrows():
        order_name = str(row.get("Name", "")).strip()
        billing_name = str(row.get("Billing Name", "")).strip()

        if billing_name and billing_name not in ("", "nan"):
            cur_customer = billing_name
            cur_status = str(row.get("Financial Status", "")).strip()
            cur_fulfillment = str(row.get("Fulfillment Status", "")).strip()
            cur_date = str(row.get("Created at", "")).strip()
            ship_city = str(row.get("Shipping City", "")).strip()
            ship_prov = str(row.get("Shipping Province Name", row.get("Shipping Province", ""))).strip()
            loc_parts = [p for p in [ship_city, ship_prov] if p and p != "nan"]
            cur_location = ", ".join(loc_parts)

        if order_name not in orders_dict:
            orders_dict[order_name] = {
                "order_number": order_name,
                "customer": cur_customer or "Unknown",
                "date": cur_date[:10] if cur_date and cur_date != "nan" else "",
                "status": cur_fulfillment if cur_fulfillment and cur_fulfillment != "nan" else (cur_status or "New"),
                "location": cur_location or "",
                "items": {},
                "total_revenue": 0.0,
                "source": "shopify",
                "notes": "",
            }

        product = str(row.get("Lineitem name", "")).strip()
        line_qty = int(float(row.get("Lineitem quantity", 0) or 0))
        line_price = float(row.get("Lineitem price", 0) or 0)

        if product and product != "nan":
            bags = parse_shopify_product(product, line_qty)
            for flavor, qty in bags.items():
                orders_dict[order_name]["items"][flavor] = orders_dict[order_name]["items"].get(flavor, 0) + qty
            orders_dict[order_name]["total_revenue"] += line_price * line_qty

    result = []
    for o in orders_dict.values():
        o["total"] = sum(o["items"].values())
        result.append(o)
    return result

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_inventory():
    rows = sb.table("inventory").select("*").execute().data
    inv = {f: 0 for f in DEFAULT_FLAVORS}
    for r in rows: inv[r["flavor"]] = r["quantity"]
    return inv

@st.cache_data(ttl=5)
def load_orders():
    rows = sb.table("orders").select("*").order("date", desc=True).execute().data
    for r in rows:
        if isinstance(r.get("items"), str): r["items"] = json.loads(r["items"])
    return rows

@st.cache_data(ttl=5)
def load_supplies():
    return sb.table("supplies").select("*").order("id").execute().data

@st.cache_data(ttl=5)
def load_projects():
    rows = sb.table("projects").select("*").execute().data
    for r in rows:
        if isinstance(r.get("order_ids"), str): r["order_ids"] = json.loads(r["order_ids"])
    return rows

def clear_cache():
    load_inventory.clear(); load_orders.clear(); load_supplies.clear(); load_projects.clear()

def set_inventory(flavor, qty):
    sb.table("inventory").upsert({"flavor": flavor, "quantity": qty}).execute(); clear_cache()

def upsert_order(order):
    payload = {k: (json.dumps(v) if isinstance(v, dict) else v) for k, v in order.items()}
    sb.table("orders").upsert(payload).execute(); clear_cache()

def delete_order(oid):
    sb.table("orders").delete().eq("id", oid).execute(); clear_cache()

def upsert_supply(supply):
    sb.table("supplies").upsert(supply).execute(); clear_cache()

def delete_supply(sid):
    sb.table("supplies").delete().eq("id", sid).execute(); clear_cache()

def upsert_project(proj):
    payload = {k: (json.dumps(v) if isinstance(v, list) else v) for k, v in proj.items()}
    sb.table("projects").upsert(payload).execute(); clear_cache()

def delete_project(pid):
    sb.table("projects").delete().eq("id", pid).execute(); clear_cache()

def get_next_id(table):
    rows = sb.table(table).select("id").execute().data
    return max([r["id"] for r in rows], default=0) + 1

# ── Session state ─────────────────────────────────────────────────────────────
if "editing_order_id" not in st.session_state: st.session_state.editing_order_id = None
if "inline_selected" not in st.session_state: st.session_state.inline_selected = set()

# ── Load ──────────────────────────────────────────────────────────────────────
inventory = load_inventory()
orders    = load_orders()
supplies  = load_supplies()
projects  = load_projects()
flavors   = DEFAULT_FLAVORS

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sub-title">🥩 Carne Shabu · Wagyu Jerky</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Inventory</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📦 Stock & Orders", "➕ New Order", "📥 Import Faire", "🛒 Import Shopify", "🛒 Supplies", "📋 Projects"])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    # ── Stock ──
    st.markdown('<div class="section-header">Current Stock</div>', unsafe_allow_html=True)
    total_bags = sum(inventory.values())
    st.markdown(f'<div class="flavor-card"><div class="bag-label">Total Bags in Stock</div><div class="bag-count">{total_bags}</div></div>', unsafe_allow_html=True)
    cols2 = st.columns(2)
    for i, f in enumerate(flavors):
        with cols2[i % 2]:
            st.markdown(f'<div class="flavor-card"><div class="flavor-name">{f}</div><div class="bag-count">{inventory.get(f,0)}</div><div class="bag-label">bags</div></div>', unsafe_allow_html=True)

    # ── Adjust ──
    st.markdown('<div class="section-header">Adjust Inventory</div>', unsafe_allow_html=True)
    adj_flavor = st.selectbox("Flavor", flavors, key="adj_flavor")
    adj_qty = st.number_input("Quantity", min_value=1, value=1, step=1, key="adj_qty")
    ba1, ba2 = st.columns(2)
    with ba1:
        if st.button("＋ Add", key="btn_add"):
            set_inventory(adj_flavor, inventory.get(adj_flavor, 0) + adj_qty); st.rerun()
    with ba2:
        if st.button("－ Subtract", key="btn_sub"):
            set_inventory(adj_flavor, max(0, inventory.get(adj_flavor, 0) - adj_qty)); st.rerun()

    # ── Cook Queue ──
    st.markdown('<div class="section-header">Cook Queue</div>', unsafe_allow_html=True)
    open_needed = {f: 0 for f in flavors}
    for order in orders:
        if order.get("status", "New").lower() != "delivered":
            for f, qty in order.get("items", {}).items():
                open_needed[f] = open_needed.get(f, 0) + qty

    total_to_cook = 0
    for f in flavors:
        needed = open_needed.get(f, 0)
        have = inventory.get(f, 0)
        gap = needed - have
        if gap > 0:
            total_to_cook += gap
            st.markdown(f'<div class="cook-card"><div class="flavor-name">{f}</div><div class="cook-need">{gap} bags</div><div class="cook-have">Ordered: {needed} · In stock: {have}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cook-card" style="border-left-color:#4caf7a;"><div class="flavor-name">{f}</div><div style="font-family:Playfair Display,serif;font-size:1.5rem;font-weight:900;color:#4caf7a;">✓ Covered</div><div class="cook-have">Ordered: {needed} · Stock: {have} · Surplus: {have-needed}</div></div>', unsafe_allow_html=True)

    if total_to_cook > 0:
        trays = round(total_to_cook / (50/36), 1)
        batches = round(trays / 36, 2)
        lbs = round(total_to_cook / 50 * 10, 1)
        st.markdown(f'<div style="background:#1a1208;border:1px solid #e05c2a44;border-radius:12px;padding:1.25rem;margin-top:1rem;"><div class="bag-label">Total to Cook</div><div style="font-family:Playfair Display,serif;font-size:2.25rem;font-weight:900;color:#e05c2a;">{total_to_cook} bags</div><div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:0.75rem;"><div><div class="bag-label">Meat to Buy</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{lbs} lbs</div></div><div><div class="bag-label">Trays</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{trays}</div></div><div><div class="bag-label">Batches</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{batches}</div></div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#1a1208;border:1px solid #4caf7a44;border-radius:12px;padding:1.25rem;margin-top:1rem;text-align:center;"><div style="font-family:Playfair Display,serif;font-size:1.5rem;color:#4caf7a;">All orders covered 🎉</div></div>', unsafe_allow_html=True)

    # ── Orders ──
    st.markdown('<div class="section-header">Orders</div>', unsafe_allow_html=True)
    status_filter = st.selectbox("Filter by Status", ["All", "New", "Processing", "Delivered"], index=2, key="tab1_filter")
    sort_order = st.selectbox("Sort by Date", ["Newest First", "Oldest First"], index=1, key="tab1_sort")

    orders_to_show = orders if status_filter == "All" else [o for o in orders if o.get("status","").lower() == status_filter.lower()]
    orders_to_show = sorted(orders_to_show, key=lambda o: o.get("date",""), reverse=(sort_order == "Newest First"))

    if orders_to_show and st.button("Clear Selection", key="clear_sel"):
        st.session_state.inline_selected = set(); st.rerun()

    for idx, order in enumerate(orders_to_show):
        oid = order.get("id", idx)
        status = order.get("status", "New")
        source_badge = "🔗 Faire" if order.get("source") == "faire" else "✏️ Manual"
        ship_date = order.get("ship_date", "")
        ship_str = f"Ships {ship_date} · " if ship_date and ship_date not in ["No ship date", "nan", ""] else ""
        order_num = f"#{order['order_number']} · " if order.get("order_number") else ""
        items_str = " · ".join([f"{qty} {f}" for f, qty in order["items"].items()])
        notes = order.get("notes", "")
        location = order.get("location", "")
        notes_html = f'<div class="order-details" style="margin-top:0.2rem;">📝 {notes}</div>' if notes and notes not in ["", "nan", "-"] else ""
        location_html = f'<div class="order-details" style="margin-top:0.1rem;">📍 {location}</div>' if location and location.strip() not in ["", "nan", ", "] else ""
        is_editing = st.session_state.editing_order_id == oid
        is_checked = oid in st.session_state.inline_selected

        chk_col, card_col = st.columns([0.5, 10])
        with chk_col:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            checked = st.checkbox("", value=is_checked, key=f"chk_{oid}_{idx}")
            if checked != is_checked:
                if checked: st.session_state.inline_selected.add(oid)
                else: st.session_state.inline_selected.discard(oid)
                st.rerun()

        with card_col:
            st.markdown(f"""
            <div class="order-card" style="{'border-left-color:#e05c2a;' if is_checked else ''}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div style="flex:1;min-width:0;">
                        <div class="order-customer">{order['customer']}</div>
                        <div class="order-date">📅 {order['date']}<br>{ship_str}{order_num}{source_badge}</div>
                        <div class="order-details">{items_str}</div>{location_html}{notes_html}
                    </div>
                    <div style="text-align:right;flex-shrink:0;margin-left:0.5rem;">
                        <div class="total-badge">{order['total']} bags</div>
                        <div style="font-family:DM Mono;font-size:0.65rem;color:#c4984a;margin-top:0.3rem;">{status}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            new_status = st.selectbox("Status", ["New", "Processing", "Delivered"],
                index=["New","Processing","Delivered"].index(status) if status in ["New","Processing","Delivered"] else 0,
                key=f"status_{oid}_{idx}")
            if new_status != status:
                order["status"] = new_status; upsert_order(order); st.rerun()

            btn1, btn2, btn3 = st.columns(3)
            with btn1:
                if st.button("✏️ Edit" if not is_editing else "✏️ Close", key=f"edit_{oid}_{idx}"):
                    st.session_state.editing_order_id = None if is_editing else oid; st.rerun()
            with btn2:
                if st.button("🗑 Delete", key=f"del_{oid}_{idx}"):
                    delete_order(oid); st.rerun()

            if is_editing:
                with st.form(key=f"edit_form_{oid}"):
                    st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#c4984a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;">Edit Order</div>', unsafe_allow_html=True)
                    e_customer = st.text_input("Customer", value=order["customer"])
                    e_location = st.text_input("Location", value=order.get("location",""), placeholder="e.g. Austin, TX")
                    e_notes = st.text_input("Notes", value=order.get("notes",""), placeholder="e.g. repeat customer")
                    st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin-top:0.5rem;">Bags per Flavor</div>', unsafe_allow_html=True)
                    e_qtys = {}
                    for f in DEFAULT_FLAVORS:
                        e_qtys[f] = st.number_input(f, min_value=0, value=order["items"].get(f, 0), step=1, key=f"eq_{oid}_{f}")
                    if st.form_submit_button("💾 Save Changes"):
                        new_items = {f: q for f, q in e_qtys.items() if q > 0}
                        order.update({"customer": e_customer, "location": e_location, "notes": e_notes, "items": new_items, "total": sum(new_items.values())})
                        upsert_order(order); st.session_state.editing_order_id = None; st.rerun()

    # ── Selection summary ──
    if st.session_state.inline_selected:
        sel_orders = [o for o in orders if o.get("id") in st.session_state.inline_selected]
        flavor_totals = {}
        for o in sel_orders:
            for f, qty in o.get("items", {}).items():
                flavor_totals[f] = flavor_totals.get(f, 0) + qty

        flavor_to_cook = {}
        for f, ordered in flavor_totals.items():
            in_stock = inventory.get(f, 0)
            flavor_to_cook[f] = {"ordered": ordered, "in_stock": in_stock, "to_cook": max(0, ordered - in_stock)}

        total_to_cook_sel = sum(v["to_cook"] for v in flavor_to_cook.values())
        trays_sel = round(total_to_cook_sel / (50/36), 1) if total_to_cook_sel > 0 else 0
        batches_sel = round(trays_sel / 36, 2) if total_to_cook_sel > 0 else 0
        summary_color = "#e05c2a" if total_to_cook_sel > 0 else "#4caf7a"

        flavor_rows_html = ""
        for f, v in flavor_to_cook.items():
            f_trays = round(v["to_cook"] / (50/36), 1) if v["to_cook"] > 0 else 0
            tray_str = f' <span style="color:#7a6040;font-size:0.7rem;">({f_trays} trays)</span>' if v["to_cook"] > 0 else ""
            cook_span = (f'<span style="color:#e05c2a;font-weight:600;">cook {v["to_cook"]}</span>{tray_str}' if v["to_cook"] > 0
                         else '<span style="color:#4caf7a;">✓ covered</span>')
            flavor_rows_html += (f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid #2e1f0a;flex-wrap:wrap;gap:0.25rem;">'
                                 f'<span style="font-family:DM Sans;font-size:0.9rem;color:#f0ead6;">{f}</span>'
                                 f'<span style="font-family:DM Mono;font-size:0.72rem;color:#7a6040;">{v["ordered"]} ordered · {v["in_stock"]} stock → {cook_span}</span>'
                                 f'</div>')

        lbs_sel = round(total_to_cook_sel / 50 * 10, 1) if total_to_cook_sel > 0 else 0
        cook_label = f"{total_to_cook_sel} bags to cook" if total_to_cook_sel > 0 else "All covered ✓"
        trays_html = (f'<div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:0.75rem;">'
                      f'<div><div class="bag-label">Meat to Buy</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{lbs_sel} lbs</div></div>'
                      f'<div><div class="bag-label">Trays</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{trays_sel}</div></div>'
                      f'<div><div class="bag-label">Batches</div><div style="font-family:DM Mono;font-size:1.25rem;color:#c4984a;">{batches_sel}</div></div>'
                      f'</div>') if total_to_cook_sel > 0 else ""

        st.markdown(f"""
        <div style="background:#1a1208;border:2px solid {summary_color}44;border-radius:12px;padding:1.25rem;margin-top:1.5rem;">
            <div style="font-family:DM Mono;font-size:0.7rem;color:{summary_color};letter-spacing:3px;text-transform:uppercase;margin-bottom:0.75rem;">{len(sel_orders)} Orders Selected</div>
            {flavor_rows_html}
            <div style="margin-top:0.75rem;">
                <div class="bag-label">To Cook</div>
                <div style="font-family:Playfair Display,serif;font-size:1.75rem;font-weight:900;color:{summary_color};">{cook_label}</div>
                {trays_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    if orders:
        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
        rows_csv = []
        for o in orders:
            for f, qty in o["items"].items():
                rows_csv.append({"Customer": o["customer"], "Date": o["date"], "Flavor": f, "Bags": qty, "Status": o.get("status",""), "Source": o.get("source","manual")})
        csv = pd.DataFrame(rows_csv).to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download CSV", data=csv, file_name=f"carne_shabu_orders_{datetime.today().strftime('%Y%m%d')}.csv", mime="text/csv")

# ── TAB 2 — New Order ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">New Manual Order</div>', unsafe_allow_html=True)
    with st.form("new_order_form", clear_on_submit=True):
        customer_name = st.text_input("Customer Name")
        order_date = st.date_input("Order Date", value=datetime.today())
        order_location = st.text_input("Location", placeholder="e.g. Austin, TX")
        order_notes = st.text_input("Notes (optional)", placeholder="e.g. repeat customer")
        st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin-top:0.5rem;">Bags per Flavor</div>', unsafe_allow_html=True)
        order_quantities = {}
        for f in DEFAULT_FLAVORS:
            order_quantities[f] = st.number_input(f, min_value=0, value=0, step=1, key=f"order_{f}")
        if st.form_submit_button("📦 Submit Order"):
            order_items = {f: q for f, q in order_quantities.items() if q > 0}
            if not customer_name: st.error("Enter a customer name.")
            elif not order_items: st.error("Add at least one bag.")
            else:
                upsert_order({"id": get_next_id("orders"), "customer": customer_name, "date": str(order_date),
                              "items": order_items, "total": sum(order_items.values()), "notes": order_notes,
                              "location": order_location, "status": "New", "source": "manual",
                              "timestamp": datetime.now().isoformat()})
                st.success(f"Order added for {customer_name}!"); st.rerun()

# ── TAB 3 — Import Faire ──────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Import Faire Orders</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Upload your Faire orders summary CSV. Duplicates are skipped automatically.</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Faire CSV", type=["csv"], label_visibility="collapsed")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()
            st.dataframe(df.head(10), use_container_width=True)

            parsed_orders = []
            for order_num, group in df.groupby("Order Number"):
                row = group.iloc[0]
                items = {}
                for _, item_row in group.iterrows():
                    flavor = normalize_flavor(item_row.get("Product Name", ""))
                    qty = int(item_row.get("Quantity", 0))
                    if flavor and qty > 0: items[flavor] = items.get(flavor, 0) + qty
                if not items: continue
                parsed_orders.append({
                    "order_number": str(order_num), "customer": str(row.get("Retailer Name", "Unknown")),
                    "date": str(row.get("Order Date", "")), "ship_date": str(row.get("Ship Date", "")),
                    "status": str(row.get("Status", "New")), "location": f"{row.get('City','')}, {row.get('State','')}",
                    "notes": "", "items": items, "total": sum(items.values()), "source": "faire",
                    "timestamp": datetime.now().isoformat()
                })

            existing_nums = {o.get("order_number") for o in orders}
            new_orders = [o for o in parsed_orders if o["order_number"] not in existing_nums]
            st.markdown(f'<div style="font-family:DM Mono;font-size:0.8rem;color:#c4984a;margin:0.75rem 0;">{len(parsed_orders)} found · {len(new_orders)} new · {len(parsed_orders)-len(new_orders)} already imported</div>', unsafe_allow_html=True)

            for o in parsed_orders:
                is_dupe = o["order_number"] in existing_nums
                items_str = " · ".join([f"{qty} {f}" for f, qty in o["items"].items()])
                border = "#2e1f0a" if is_dupe else "#c4984a"
                dupe = ' <span style="color:#7a6040;font-size:0.65rem;">(already imported)</span>' if is_dupe else ""
                st.markdown(f'<div class="order-card" style="border-left-color:{border};"><div class="order-customer">{o["customer"]}{dupe}</div><div class="order-date">📅 {o["date"]} · #{o["order_number"]}</div><div class="order-details">{items_str}</div><div class="total-badge">{o["total"]} bags</div></div>', unsafe_allow_html=True)

            if new_orders:
                if st.button(f"✅ Import {len(new_orders)} New Orders"):
                    next_id = get_next_id("orders")
                    for o in new_orders:
                        o["id"] = next_id; next_id += 1; upsert_order(o)
                    st.success(f"Imported {len(new_orders)} orders!"); st.rerun()
            else:
                st.info("All orders already imported.")
        except Exception as e:
            st.error(f"Error: {e}")

# ── TAB 4 — Import Shopify ────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Import Shopify Orders</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Upload a Shopify orders export CSV. Duplicates are skipped automatically.</div>', unsafe_allow_html=True)

    shopify_file = st.file_uploader("Upload Shopify CSV", type=["csv"], label_visibility="collapsed", key="shopify_upload")
    if shopify_file:
        try:
            sdf = pd.read_csv(shopify_file)
            sdf.columns = sdf.columns.str.strip()
            st.markdown('<div class="section-header">Preview</div>', unsafe_allow_html=True)
            st.dataframe(sdf.head(10), use_container_width=True)

            parsed_shopify = parse_shopify_csv(sdf)
            existing_nums = {o.get("order_number") for o in orders}
            new_shopify = [o for o in parsed_shopify if o["order_number"] not in existing_nums]

            st.markdown(
                f'<div style="font-family:DM Mono;font-size:0.8rem;color:#c4984a;margin:0.75rem 0;">'
                f'{len(parsed_shopify)} found · {len(new_shopify)} new · '
                f'{len(parsed_shopify)-len(new_shopify)} already imported</div>',
                unsafe_allow_html=True)

            for o in parsed_shopify:
                is_dupe = o["order_number"] in existing_nums
                items_str = " · ".join([f"{qty} {f}" for f, qty in o["items"].items()])
                border = "#2e1f0a" if is_dupe else "#c4984a"
                dupe = (' <span style="color:#7a6040;font-size:0.65rem;">'
                        '(already imported)</span>') if is_dupe else ""
                revenue = f" · ${o['total_revenue']:.2f}" if o.get("total_revenue") else ""
                location = (f" · {o['location']}"
                            if o.get("location") and o["location"] not in ("", ", ")
                            else "")
                st.markdown(f'''
                <div class="order-card" style="border-left-color:{border};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="order-customer">{o["customer"]}{dupe}</div>
                            <div class="order-date">📅 {o["date"]} · {o["order_number"]} · {o["status"]}{location}{revenue}</div>
                            <div class="order-details" style="margin-top:0.4rem">{items_str}</div>
                        </div>
                        <div class="total-badge">{o["total"]} bags</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            if new_shopify:
                if st.button(f"✅ Import {len(new_shopify)} New Shopify Orders"):
                    next_id = get_next_id("orders")
                    for o in new_shopify:
                        o["id"] = next_id
                        o["timestamp"] = datetime.now().isoformat()
                        # Remove total_revenue from the order dict before saving (not in DB schema)
                        o.pop("total_revenue", None)
                        next_id += 1
                        upsert_order(o)
                    st.success(f"Imported {len(new_shopify)} Shopify orders!")
                    st.rerun()
            else:
                st.info("All Shopify orders already imported.")
        except Exception as e:
            st.error(f"Error parsing Shopify CSV: {e}")

# ── TAB 5 — Supplies ──────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Supplies Checklist</div>', unsafe_allow_html=True)
    with st.form("add_supply", clear_on_submit=True):
        new_item = st.text_input("Item", placeholder="e.g. Wagyu beef, 1oz bags...")
        new_qty_s = st.text_input("Qty / Notes", placeholder="e.g. 10 lbs")
        new_priority = st.selectbox("Priority", ["Normal", "Urgent", "Low"])
        if st.form_submit_button("＋ Add Item"):
            if new_item:
                upsert_supply({"id": get_next_id("supplies"), "item": new_item, "qty": new_qty_s,
                               "priority": new_priority, "checked": False, "added": datetime.now().strftime("%b %d")})
                st.rerun()

    if not supplies:
        st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No supplies added yet.</div>', unsafe_allow_html=True)
    else:
        priority_colors = {"Urgent": "#e05c2a", "Normal": "#c4984a", "Low": "#7a6040"}
        priority_order  = {"Urgent": 0, "Normal": 1, "Low": 2}
        sorted_supplies = sorted(supplies, key=lambda x: (x.get("checked", False), priority_order.get(x.get("priority","Normal"), 1)))

        for supply in sorted_supplies:
            sid = supply.get("id", 0)
            checked = supply.get("checked", False)
            priority = supply.get("priority", "Normal")
            pcolor = priority_colors.get(priority, "#c4984a")
            opacity = "0.4" if checked else "1"
            strikethrough = "line-through" if checked else "none"
            sc1, sc2, sc3 = st.columns([0.6, 6, 1.5])
            with sc1:
                new_checked = st.checkbox("", value=checked, key=f"supply_check_{sid}")
                if new_checked != checked:
                    supply["checked"] = new_checked; upsert_supply(supply); st.rerun()
            with sc2:
                qty_str = f' <span style="color:#7a6040;font-size:0.8rem;">— {supply["qty"]}</span>' if supply.get("qty") else ""
                st.markdown(f'<div style="opacity:{opacity};padding:0.5rem 0;"><span style="font-family:DM Sans;font-size:1rem;color:#f0ead6;text-decoration:{strikethrough};">{supply["item"]}</span>{qty_str} <span style="font-family:DM Mono;font-size:0.65rem;color:{pcolor};border:1px solid {pcolor}44;border-radius:10px;padding:0.1rem 0.5rem;">{priority}</span></div>', unsafe_allow_html=True)
            with sc3:
                if st.button("Remove", key=f"del_supply_{sid}"): delete_supply(sid); st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("✅ Clear Checked"):
                for s in [s for s in supplies if s.get("checked")]: delete_supply(s["id"])
                st.rerun()
        with bc2:
            if st.button("🗑 Clear All"):
                for s in supplies: delete_supply(s["id"])
                st.rerun()

# ── TAB 6 — Projects ──────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-header">Projects</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Group orders to see how many bags you need to cook.</div>', unsafe_allow_html=True)

    if not orders:
        st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No orders yet.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">Create / Update Project</div>', unsafe_allow_html=True)
        with st.form("project_form", clear_on_submit=False):
            proj_name = st.text_input("Project Name", placeholder="e.g. Feb Batch, Week 1 Ship...")
            st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin:0.75rem 0 0.25rem 0;">Select Orders</div>', unsafe_allow_html=True)
            selected_ids = []
            for order in sorted(orders, key=lambda o: o.get("date",""), reverse=True):
                oid = order.get("id")
                items_str = " · ".join([f"{qty} {f}" for f, qty in order["items"].items()])
                label = f"{order['customer']} — {items_str} ({order.get('status','New')})"
                if st.checkbox(label, key=f"proj_sel_{oid}"): selected_ids.append(oid)
            if st.form_submit_button("💾 Save Project"):
                if not proj_name: st.error("Enter a project name.")
                elif not selected_ids: st.error("Select at least one order.")
                else:
                    existing = next((p for p in projects if p["name"] == proj_name), None)
                    pid = existing["id"] if existing else get_next_id("projects")
                    upsert_project({"id": pid, "name": proj_name, "order_ids": selected_ids, "updated": datetime.now().strftime("%b %d")})
                    st.success(f"Project '{proj_name}' saved!"); st.rerun()

        st.markdown('<div class="section-header">Saved Projects</div>', unsafe_allow_html=True)
        if not projects:
            st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No projects yet.</div>', unsafe_allow_html=True)
        else:
            for proj in projects:
                proj_orders = [o for o in orders if o.get("id") in proj["order_ids"]]
                flavor_totals = {}
                for o in proj_orders:
                    for f, qty in o.get("items", {}).items():
                        flavor_totals[f] = flavor_totals.get(f, 0) + qty
                total_bags_proj = sum(flavor_totals.values())
                trays_proj = round(total_bags_proj / (50/36), 1)
                batches_proj = round(trays_proj / 36, 2)
                flavor_rows = "".join([f'<div style="display:flex;justify-content:space-between;padding:0.25rem 0;border-bottom:1px solid #2e1f0a;"><span style="font-family:DM Sans;font-size:0.85rem;color:#f0ead6;">{f}</span><span style="font-family:DM Mono;font-size:0.85rem;color:#c4984a;">{q} bags</span></div>' for f, q in flavor_totals.items()])
                customer_list = ", ".join([o["customer"] for o in proj_orders])
                st.markdown(f"""
                <div style="background:#1a1208;border:1px solid #2e1f0a;border-radius:12px;padding:1.25rem;margin-bottom:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem;flex-wrap:wrap;gap:0.5rem;">
                        <div>
                            <div style="font-family:Playfair Display,serif;font-size:1.1rem;font-weight:700;color:#f0ead6;">{proj["name"]}</div>
                            <div style="font-family:DM Mono;font-size:0.65rem;color:#7a6040;margin-top:0.1rem;">{len(proj_orders)} orders · {proj.get("updated","")}</div>
                            <div style="font-family:DM Sans;font-size:0.78rem;color:#7a6040;margin-top:0.15rem;">{customer_list}</div>
                        </div>
                        <div style="text-align:right;">
                            <div class="total-badge">{total_bags_proj} bags</div>
                            <div style="font-family:DM Mono;font-size:0.65rem;color:#c4984a;margin-top:0.3rem;">{trays_proj} trays · {batches_proj} batches</div>
                        </div>
                    </div>
                    {flavor_rows}
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑 Delete Project", key=f"del_proj_{proj['id']}"):
                    delete_project(proj["id"]); st.rerun()

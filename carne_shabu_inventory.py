import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(page_title="Carne Shabu · Inventory", page_icon="🥩", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0e0a06; color: #f0ead6; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }
.main-title { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 900; color: #f0ead6; letter-spacing: -1px; line-height: 1; }
.sub-title { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #c4984a; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 0.5rem; }
.flavor-card { background: #1a1208; border: 1px solid #2e1f0a; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem; }
.bag-count { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 900; color: #c4984a; line-height: 1; }
.bag-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #7a6040; text-transform: uppercase; letter-spacing: 2px; }
.flavor-name { font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 600; color: #f0ead6; margin-bottom: 0.15rem; }
.cook-card { background: #12100a; border: 1px solid #2e1f0a; border-left: 3px solid #e05c2a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; }
.cook-need { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 900; color: #e05c2a; line-height: 1; }
.cook-have { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #7a6040; }
.section-header { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c4984a; letter-spacing: 3px; text-transform: uppercase; border-bottom: 1px solid #2e1f0a; padding-bottom: 0.5rem; margin: 1.5rem 0 1rem 0; }
.order-card { background: #120e08; border: 1px solid #2e1f0a; border-left: 3px solid #c4984a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.6rem; }
.order-customer { font-family: 'Playfair Display', serif; font-size: 1rem; color: #f0ead6; font-weight: 700; }
.order-date { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #7a6040; letter-spacing: 1px; }
.order-details { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: #a08060; margin-top: 0.25rem; }
.total-badge { background: #c4984a22; border: 1px solid #c4984a44; border-radius: 20px; padding: 0.15rem 0.65rem; font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #c4984a; display: inline-block; margin-top: 0.4rem; }
div[data-testid="stNumberInput"] input { background: #1a1208 !important; border: 1px solid #2e1f0a !important; color: #f0ead6 !important; font-family: 'DM Mono', monospace !important; border-radius: 8px !important; }
div[data-testid="stTextInput"] input { background: #1a1208 !important; border: 1px solid #2e1f0a !important; color: #f0ead6 !important; border-radius: 8px !important; }
.stButton > button { background: #c4984a !important; color: #0e0a06 !important; border: none !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 2px !important; text-transform: uppercase !important; border-radius: 8px !important; padding: 0.5rem 1.25rem !important; font-weight: 500 !important; }
[data-testid="stSidebar"] { background: #0a0804 !important; border-right: 1px solid #2e1f0a !important; }
div[data-testid="stVerticalBlock"] label { color: #a08060 !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 1px !important; }
.divider { border: none; border-top: 1px solid #2e1f0a; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "carne_shabu_data.json"
DEFAULT_FLAVORS = ["Truffle Sea Salt", "Lemon Pepper", "Spicy Lemon Pepper", "Ghost Pepper"]
FLAVOR_MAP = {
    "truffle sea salt": "Truffle Sea Salt",
    "lemon pepper": "Lemon Pepper",
    "lemon pep": "Lemon Pepper",
    "spicy lemon pepper": "Spicy Lemon Pepper",
    "spicy lemon pep": "Spicy Lemon Pepper",
    "ghost pepper": "Ghost Pepper",
    "ghost pep": "Ghost Pepper",
}

def normalize_flavor(raw):
    return FLAVOR_MAP.get(str(raw).strip().lower(), str(raw).strip())

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"inventory": {f: 0 for f in DEFAULT_FLAVORS}, "orders": [], "supplies": []}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()
if "editing_order_id" not in st.session_state:
    st.session_state.editing_order_id = None

data = st.session_state.data

for flavor in DEFAULT_FLAVORS:
    if flavor not in data["inventory"]:
        data["inventory"][flavor] = 0
if "supplies" not in data:
    data["supplies"] = []

# Migrate old orders: move city/state from notes -> location
import re as _re
_migrated = False
for _o in data["orders"]:
    if not _o.get("location") and _o.get("notes"):
        # If notes looks like "City, ST" pattern, move it to location
        if _re.match(r'^[A-Za-z\s]+,\s*[A-Z]{2}$', _o["notes"].strip()):
            _o["location"] = _o["notes"]
            _o["notes"] = ""
            _migrated = True
if _migrated:
    save_data(data)

st.markdown('<div class="sub-title">🥩 Carne Shabu · Wagyu Jerky</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Inventory</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Inventory & Orders", "➕ New Order", "📥 Import Faire CSV", "🛒 Supplies", "📋 Projects"])

flavors = list(data["inventory"].keys())

# ── helper to render order list ───────────────────────────────────────────────
def render_orders(orders_to_show, key_prefix=""):
    if not orders_to_show:
        st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No orders found.</div>', unsafe_allow_html=True)
        return

    for idx, order in enumerate(orders_to_show):
        oid = order.get("id", idx)
        status = order.get("status", "New")
        source_badge = "🔗 Faire" if order.get("source") == "faire" else "✏️ Manual"
        ship_date = order.get("ship_date", "")
        ship_str = f" · Ships {ship_date}" if ship_date and ship_date not in ["No ship date", "nan", ""] else ""
        order_num = f" · #{order['order_number']}" if order.get("order_number") else ""
        items_str = " · ".join([f"{qty} {flavor}" for flavor, qty in order["items"].items()])
        notes = order.get("notes", "")
        location = order.get("location", "")
        notes_html = f'<div class="order-details" style="margin-top:0.25rem;">📝 {notes}</div>' if notes and notes not in ["", "nan", "-", "'-"] else ""
        location_html = f'<div class="order-details" style="margin-top:0.1rem;">📍 {location}</div>' if location and location.strip() not in ["", "nan", ", "] else ""

        is_editing = st.session_state.editing_order_id == oid

        st.markdown(f"""
        <div class="order-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="order-customer">{order['customer']}</div>
                    <div class="order-date">📅 {order['date']}{ship_str}{order_num} · {source_badge}</div>
                    <div class="order-details">{items_str}</div>{location_html}{notes_html}
                </div>
                <div style="text-align:right;">
                    <div class="total-badge">{order['total']} bags</div>
                    <div style="font-family:DM Mono;font-size:0.65rem;color:#c4984a;margin-top:0.3rem;">{status}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_s, col_e, col_d = st.columns([2, 1, 1])
        with col_s:
            new_status = st.selectbox("Status", ["New", "Processing", "Delivered"],
                index=["New","Processing","Delivered"].index(status) if status in ["New","Processing","Delivered"] else 0,
                key=f"{key_prefix}status_{oid}_{idx}")
            if new_status != status:
                for o in data["orders"]:
                    if o.get("id") == oid:
                        o["status"] = new_status
                save_data(data)
                st.rerun()
        with col_e:
            edit_label = "✏️ Close" if is_editing else "✏️ Edit"
            if st.button(edit_label, key=f"{key_prefix}edit_{oid}_{idx}"):
                st.session_state.editing_order_id = None if is_editing else oid
                st.rerun()
        with col_d:
            if st.button("🗑 Delete", key=f"{key_prefix}del_{oid}_{idx}"):
                data["orders"] = [o for o in data["orders"] if o.get("id") != oid]
                save_data(data)
                st.rerun()

        if is_editing:
            with st.form(key=f"{key_prefix}edit_form_{oid}"):
                st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#c4984a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;">Edit Order</div>', unsafe_allow_html=True)
                e_customer = st.text_input("Customer", value=order["customer"])
                e_location = st.text_input("Location", value=order.get("location",""), placeholder="e.g. Austin, TX")
                e_notes = st.text_input("Notes", value=order.get("notes",""), placeholder="e.g. repeat customer, fragile")
                st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin-top:0.5rem;">Bags per Flavor</div>', unsafe_allow_html=True)
                e_qtys = {}
                for flavor in DEFAULT_FLAVORS:
                    e_qtys[flavor] = st.number_input(flavor, min_value=0, value=order["items"].get(flavor, 0), step=1, key=f"{key_prefix}eq_{oid}_{flavor}")
                if st.form_submit_button("💾 Save Changes"):
                    new_items = {f: q for f, q in e_qtys.items() if q > 0}
                    for o in data["orders"]:
                        if o.get("id") == oid:
                            o["customer"] = e_customer
                            o["location"] = e_location
                            o["notes"] = e_notes
                            o["items"] = new_items
                            o["total"] = sum(new_items.values())
                    save_data(data)
                    st.session_state.editing_order_id = None
                    st.rerun()

# ── TAB 1 — Inventory & Orders ────────────────────────────────────────────────
with tab1:
    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown('<div class="section-header">Current Stock</div>', unsafe_allow_html=True)
        total_bags = sum(data["inventory"].values())
        st.markdown(f'<div class="flavor-card"><div class="bag-label">Total Bags in Stock</div><div class="bag-count">{total_bags}</div></div>', unsafe_allow_html=True)

        for i in range(0, len(flavors), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(flavors):
                    flavor = flavors[i + j]
                    count = data["inventory"][flavor]
                    with col:
                        st.markdown(f'<div class="flavor-card"><div class="flavor-name">{flavor}</div><div class="bag-count">{count}</div><div class="bag-label">bags</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">Adjust Inventory</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            adj_flavor = st.selectbox("Flavor", flavors, key="adj_flavor")
        with c2:
            adj_qty = st.number_input("Quantity", min_value=1, value=1, step=1, key="adj_qty")
        with c3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("＋ Add"):
                    data["inventory"][adj_flavor] += adj_qty
                    save_data(data)
                    st.rerun()
            with b2:
                if st.button("－ Sub"):
                    data["inventory"][adj_flavor] = max(0, data["inventory"][adj_flavor] - adj_qty)
                    save_data(data)
                    st.rerun()

        # Cook Queue
        st.markdown('<div class="section-header">Cook Queue</div>', unsafe_allow_html=True)
        open_needed = {f: 0 for f in data["inventory"].keys()}
        for order in data["orders"]:
            if order.get("status", "New").lower() not in ["delivered"]:
                for flavor, qty in order.get("items", {}).items():
                    if flavor in open_needed:
                        open_needed[flavor] += qty
                    else:
                        open_needed[flavor] = qty

        total_to_cook = 0
        for flavor in data["inventory"].keys():
            needed = open_needed.get(flavor, 0)
            have = data["inventory"].get(flavor, 0)
            gap = needed - have
            if gap > 0:
                total_to_cook += gap
                st.markdown(f'<div class="cook-card"><div class="flavor-name">{flavor}</div><div class="cook-need">{gap} bags to cook</div><div class="cook-have">Ordered: {needed} &nbsp;·&nbsp; In stock: {have}</div></div>', unsafe_allow_html=True)
            else:
                surplus = have - needed
                st.markdown(f'<div class="cook-card" style="border-left-color:#4caf7a;"><div class="flavor-name">{flavor}</div><div style="font-family:Playfair Display,serif;font-size:2rem;font-weight:900;color:#4caf7a;line-height:1;">✓ Covered</div><div class="cook-have">Ordered: {needed} &nbsp;·&nbsp; In stock: {have} &nbsp;·&nbsp; Surplus: {surplus}</div></div>', unsafe_allow_html=True)

        if total_to_cook > 0:
            trays = round(total_to_cook / (50/36), 1)
            batches = round(trays / 36, 2)
            st.markdown(f'<div style="background:#1a1208;border:1px solid #e05c2a44;border-radius:12px;padding:1.25rem;margin-top:1rem;"><div class="bag-label">Total Bags to Cook</div><div style="font-family:Playfair Display,serif;font-size:2.5rem;font-weight:900;color:#e05c2a;">{total_to_cook}</div><div class="bag-label" style="margin-top:0.5rem;">Estimated Trays Needed</div><div style="font-family:DM Mono,monospace;font-size:1.25rem;color:#c4984a;">{trays} trays</div><div class="bag-label" style="margin-top:0.5rem;">Batches (36 trays each)</div><div style="font-family:DM Mono,monospace;font-size:1.25rem;color:#c4984a;">{batches} batches</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#1a1208;border:1px solid #4caf7a44;border-radius:12px;padding:1.25rem;margin-top:1rem;text-align:center;"><div style="font-family:Playfair Display,serif;font-size:1.5rem;color:#4caf7a;">All orders covered 🎉</div><div class="bag-label" style="margin-top:0.25rem;">No cooking needed right now</div></div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-header">Orders</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            status_filter = st.selectbox("Filter by Status", ["All", "New", "Processing", "Delivered"], index=2, key="tab1_filter")
        with fc2:
            sort_order = st.selectbox("Sort by Date", ["Newest First", "Oldest First"], index=1, key="tab1_sort")
        orders_to_show = data["orders"] if status_filter == "All" else [o for o in data["orders"] if o.get("status","").lower() == status_filter.lower()]
        orders_to_show = sorted(orders_to_show, key=lambda o: o.get("date",""), reverse=(sort_order == "Newest First"))

        # ── Inline order selection + cook summary ─────────────────────────
        if "inline_selected" not in st.session_state:
            st.session_state.inline_selected = set()

        if orders_to_show:
            sel_col1, sel_col2 = st.columns([3,1])
            with sel_col2:
                if st.button("Clear Selection", key="clear_sel"):
                    st.session_state.inline_selected = set()
                    st.rerun()

        # Render each order with a checkbox
        for idx, order in enumerate(orders_to_show):
            oid = order.get("id", idx)
            status = order.get("status", "New")
            source_badge = "🔗 Faire" if order.get("source") == "faire" else "✏️ Manual"
            ship_date = order.get("ship_date", "")
            ship_str = f" · Ships {ship_date}" if ship_date and ship_date not in ["No ship date", "nan", ""] else ""
            order_num = f" · #{order['order_number']}" if order.get("order_number") else ""
            items_str = " · ".join([f"{qty} {f}" for f, qty in order["items"].items()])
            notes = order.get("notes", "")
            location = order.get("location", "")
            notes_html = f'<div class="order-details" style="margin-top:0.25rem;">📝 {notes}</div>' if notes and notes not in ["", "nan", "-", "\'-"] else ""
            location_html = f'<div class="order-details" style="margin-top:0.1rem;">📍 {location}</div>' if location and location.strip() not in ["", "nan", ", "] else ""
            is_editing = st.session_state.editing_order_id == oid
            is_checked = oid in st.session_state.inline_selected

            chk_col, card_col = st.columns([0.4, 10])
            with chk_col:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                checked = st.checkbox("", value=is_checked, key=f"inline_chk_{oid}_{idx}")
                if checked != is_checked:
                    if checked:
                        st.session_state.inline_selected.add(oid)
                    else:
                        st.session_state.inline_selected.discard(oid)
                    st.rerun()

            with card_col:
                st.markdown(f"""
                <div class="order-card" style="{'border-left-color:#e05c2a;' if is_checked else ''}">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="order-customer">{order['customer']}</div>
                            <div class="order-date">📅 {order['date']}{ship_str}{order_num} · {source_badge}</div>
                            <div class="order-details">{items_str}</div>{location_html}{notes_html}
                        </div>
                        <div style="text-align:right;">
                            <div class="total-badge">{order['total']} bags</div>
                            <div style="font-family:DM Mono;font-size:0.65rem;color:#c4984a;margin-top:0.3rem;">{status}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_s, col_e, col_d = st.columns([2, 1, 1])
                with col_s:
                    new_status = st.selectbox("Status", ["New", "Processing", "Delivered"],
                        index=["New","Processing","Delivered"].index(status) if status in ["New","Processing","Delivered"] else 0,
                        key=f"t1_status_{oid}_{idx}")
                    if new_status != status:
                        for o in data["orders"]:
                            if o.get("id") == oid:
                                o["status"] = new_status
                        save_data(data)
                        st.rerun()
                with col_e:
                    edit_label = "✏️ Close" if is_editing else "✏️ Edit"
                    if st.button(edit_label, key=f"t1_edit_{oid}_{idx}"):
                        st.session_state.editing_order_id = None if is_editing else oid
                        st.rerun()
                with col_d:
                    if st.button("🗑 Delete", key=f"t1_del_{oid}_{idx}"):
                        data["orders"] = [o for o in data["orders"] if o.get("id") != oid]
                        save_data(data)
                        st.rerun()

                if is_editing:
                    with st.form(key=f"t1_edit_form_{oid}"):
                        st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#c4984a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;">Edit Order</div>', unsafe_allow_html=True)
                        e_customer = st.text_input("Customer", value=order["customer"])
                        e_location = st.text_input("Location", value=order.get("location",""), placeholder="e.g. Austin, TX")
                        e_notes = st.text_input("Notes", value=order.get("notes",""), placeholder="e.g. repeat customer, fragile")
                        st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin-top:0.5rem;">Bags per Flavor</div>', unsafe_allow_html=True)
                        e_qtys = {}
                        for flavor in DEFAULT_FLAVORS:
                            e_qtys[flavor] = st.number_input(flavor, min_value=0, value=order["items"].get(flavor, 0), step=1, key=f"t1_eq_{oid}_{flavor}")
                        if st.form_submit_button("💾 Save Changes"):
                            new_items = {f: q for f, q in e_qtys.items() if q > 0}
                            for o in data["orders"]:
                                if o.get("id") == oid:
                                    o["customer"] = e_customer
                                    o["location"] = e_location
                                    o["notes"] = e_notes
                                    o["items"] = new_items
                                    o["total"] = sum(new_items.values())
                            save_data(data)
                            st.session_state.editing_order_id = None
                            st.rerun()

        # ── Selection summary ─────────────────────────────────────────────
        if st.session_state.inline_selected:
            sel_orders = [o for o in data["orders"] if o.get("id") in st.session_state.inline_selected]
            flavor_totals = {}
            for o in sel_orders:
                for flavor, qty in o.get("items", {}).items():
                    flavor_totals[flavor] = flavor_totals.get(flavor, 0) + qty

            # Subtract current inventory
            flavor_to_cook = {}
            for flavor, ordered in flavor_totals.items():
                in_stock = data["inventory"].get(flavor, 0)
                to_cook = max(0, ordered - in_stock)
                flavor_to_cook[flavor] = {"ordered": ordered, "in_stock": in_stock, "to_cook": to_cook}

            total_to_cook = sum(v["to_cook"] for v in flavor_to_cook.values())
            trays = round(total_to_cook / (50/36), 1) if total_to_cook > 0 else 0
            batches = round(trays / 36, 2) if total_to_cook > 0 else 0
            summary_color = "#e05c2a" if total_to_cook > 0 else "#4caf7a"

            flavor_rows_html = ""
            for f, v in flavor_to_cook.items():
                cook_span = f'<span style="font-family:DM Mono;font-size:0.88rem;color:#e05c2a;font-weight:600;">cook {v["to_cook"]}</span>' if v["to_cook"] > 0 else '<span style="font-family:DM Mono;font-size:0.88rem;color:#4caf7a;">&#10003; covered</span>'
                flavor_rows_html += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.35rem 0;border-bottom:1px solid #2e1f0a;"><span style="font-family:DM Sans;font-size:0.88rem;color:#f0ead6;">{f}</span><span style="font-family:DM Mono;font-size:0.72rem;color:#7a6040;">ordered {v["ordered"]} &middot; stock {v["in_stock"]} &rarr; </span>{cook_span}</div>'

            if total_to_cook > 0:
                trays_batches_html = (
                    '<div><div class="bag-label">Trays</div>'
                    f'<div style="font-family:DM Mono;font-size:1.5rem;color:#c4984a;">{trays}</div></div>'
                    '<div><div class="bag-label">Batches</div>'
                    f'<div style="font-family:DM Mono;font-size:1.5rem;color:#c4984a;">{batches}</div></div>'
                )
            else:
                trays_batches_html = ""

            cook_label = f"{total_to_cook} bags to cook" if total_to_cook > 0 else "All covered ✓"

            st.markdown(f"""
            <div style="background:#1a1208;border:2px solid {summary_color}44;border-radius:12px;padding:1.25rem;margin-top:1.5rem;">
                <div style="font-family:DM Mono;font-size:0.7rem;color:{summary_color};letter-spacing:3px;text-transform:uppercase;margin-bottom:0.75rem;">
                    {len(sel_orders)} Orders Selected
                </div>
                {flavor_rows_html}
                <div style="margin-top:0.75rem;display:flex;gap:1.5rem;align-items:flex-end;">
                    <div>
                        <div class="bag-label">To Cook</div>
                        <div style="font-family:Playfair Display,serif;font-size:2rem;font-weight:900;color:{summary_color};">{cook_label}</div>
                    </div>
                    {trays_batches_html}
                </div>
            </div>
            """, unsafe_allow_html=True)


        if data["orders"]:
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            rows = []
            for o in data["orders"]:
                for flavor, qty in o["items"].items():
                    rows.append({"Customer": o["customer"], "Date": o["date"], "Flavor": flavor, "Bags": qty, "Status": o.get("status",""), "Source": o.get("source","manual")})
            csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
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
        for flavor in DEFAULT_FLAVORS:
            qty = st.number_input(flavor, min_value=0, value=0, step=1, key=f"order_{flavor}")
            order_quantities[flavor] = qty
        if st.form_submit_button("📦 Submit Order"):
            order_items = {f: q for f, q in order_quantities.items() if q > 0}
            if not customer_name:
                st.error("Enter a customer name.")
            elif not order_items:
                st.error("Add at least one bag.")
            else:
                order = {
                    "id": max([o.get("id",0) for o in data["orders"]], default=0) + 1,
                    "customer": customer_name,
                    "date": str(order_date),
                    "items": order_items,
                    "total": sum(order_items.values()),
                    "notes": order_notes,
                    "location": order_location,
                    "status": "New",
                    "source": "manual",
                    "timestamp": datetime.now().isoformat()
                }
                data["orders"].insert(0, order)
                save_data(data)
                st.success(f"Order added for {customer_name}!")
                st.rerun()

# ── TAB 3 — Import Faire ──────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Import Faire Orders</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Upload your Faire orders summary CSV. Duplicates (matched by Order Number) are skipped automatically.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Faire CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = df.columns.str.strip()

            st.markdown('<div class="section-header">Preview (first 10 rows)</div>', unsafe_allow_html=True)
            st.dataframe(df.head(10), use_container_width=True)

            parsed_orders = []
            for order_num, group in df.groupby("Order Number"):
                row = group.iloc[0]
                items = {}
                for _, item_row in group.iterrows():
                    flavor = normalize_flavor(item_row.get("Product Name", ""))
                    qty = int(item_row.get("Quantity", 0))
                    if flavor and qty > 0:
                        items[flavor] = items.get(flavor, 0) + qty
                if not items:
                    continue
                parsed_orders.append({
                    "order_number": str(order_num),
                    "customer": str(row.get("Retailer Name", "Unknown")),
                    "date": str(row.get("Order Date", "")),
                    "ship_date": str(row.get("Ship Date", "")),
                    "status": str(row.get("Status", "New")),
                    "items": items,
                    "total": sum(items.values()),
                    "location": f"{row.get('City','')}, {row.get('State','')}",
                    "notes": "",
                    "source": "faire",
                    "timestamp": datetime.now().isoformat()
                })

            existing_nums = {o.get("order_number") for o in data["orders"]}
            new_orders = [o for o in parsed_orders if o["order_number"] not in existing_nums]

            st.markdown(f'<div style="font-family:DM Mono;font-size:0.8rem;color:#c4984a;margin:0.75rem 0;">{len(parsed_orders)} orders found · {len(new_orders)} new · {len(parsed_orders)-len(new_orders)} already imported</div>', unsafe_allow_html=True)

            for o in parsed_orders:
                is_dupe = o["order_number"] in existing_nums
                items_str = " · ".join([f"{qty} {f}" for f, qty in o["items"].items()])
                border = "#2e1f0a" if is_dupe else "#c4984a"
                dupe = ' <span style="color:#7a6040;font-size:0.65rem;">(already imported)</span>' if is_dupe else ""
                ship = f" · Ships {o['ship_date']}" if o.get("ship_date") and o["ship_date"] not in ["No ship date","nan",""] else ""
                st.markdown(f'<div class="order-card" style="border-left-color:{border};"><div class="order-customer">{o["customer"]}{dupe}</div><div class="order-date">📅 {o["date"]}{ship} · #{o["order_number"]} · {o["status"]}</div><div class="order-details">{items_str}</div><div class="total-badge">{o["total"]} bags</div></div>', unsafe_allow_html=True)

            if new_orders:
                if st.button(f"✅ Import {len(new_orders)} New Orders"):
                    next_id = max([o.get("id", 0) for o in data["orders"]], default=0) + 1
                    for o in new_orders:
                        o["id"] = next_id
                        next_id += 1
                        data["orders"].insert(0, o)
                    save_data(data)
                    st.success(f"Imported {len(new_orders)} orders!")
                    st.rerun()
            else:
                st.info("All orders in this file have already been imported.")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

# ── TAB 4 — Supplies ──────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Supplies Checklist</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Track what you need to order. Check off when ordered, clear when done.</div>', unsafe_allow_html=True)

    with st.form("add_supply", clear_on_submit=True):
        sc1, sc2, sc3 = st.columns([3, 1, 1])
        with sc1:
            new_item = st.text_input("Item", placeholder="e.g. Wagyu beef, 1oz bags, truffle salt...")
        with sc2:
            new_qty = st.text_input("Qty / Notes", placeholder="e.g. 10 lbs")
        with sc3:
            new_priority = st.selectbox("Priority", ["Normal", "Urgent", "Low"])
        if st.form_submit_button("＋ Add Item"):
            if new_item:
                data["supplies"].append({
                    "id": max([s.get("id",0) for s in data["supplies"]], default=0) + 1,
                    "item": new_item,
                    "qty": new_qty,
                    "priority": new_priority,
                    "checked": False,
                    "added": datetime.now().strftime("%b %d")
                })
                save_data(data)
                st.rerun()

    if not data["supplies"]:
        st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No supplies added yet.</div>', unsafe_allow_html=True)
    else:
        priority_colors = {"Urgent": "#e05c2a", "Normal": "#c4984a", "Low": "#7a6040"}
        priority_order = {"Urgent": 0, "Normal": 1, "Low": 2}
        sorted_supplies = sorted(data["supplies"], key=lambda x: (x.get("checked", False), priority_order.get(x.get("priority","Normal"), 1)))

        for supply in sorted_supplies:
            sid = supply.get("id", 0)
            checked = supply.get("checked", False)
            priority = supply.get("priority", "Normal")
            pcolor = priority_colors.get(priority, "#c4984a")
            opacity = "0.4" if checked else "1"
            strikethrough = "line-through" if checked else "none"

            sc1, sc2, sc3 = st.columns([0.5, 6, 1.5])
            with sc1:
                new_checked = st.checkbox("", value=checked, key=f"supply_check_{sid}")
                if new_checked != checked:
                    for s in data["supplies"]:
                        if s.get("id") == sid:
                            s["checked"] = new_checked
                    save_data(data)
                    st.rerun()
            with sc2:
                qty_str = f' <span style="color:#7a6040;font-size:0.8rem;">— {supply["qty"]}</span>' if supply.get("qty") else ""
                st.markdown(f'<div style="opacity:{opacity};padding:0.5rem 0;"><span style="font-family:DM Sans;font-size:1rem;color:#f0ead6;text-decoration:{strikethrough};">{supply["item"]}</span>{qty_str} <span style="font-family:DM Mono;font-size:0.65rem;color:{pcolor};border:1px solid {pcolor}44;border-radius:10px;padding:0.1rem 0.5rem;">{priority}</span> <span style="font-family:DM Mono;font-size:0.6rem;color:#4a3820;">Added {supply.get("added","")}</span></div>', unsafe_allow_html=True)
            with sc3:
                if st.button("Remove", key=f"del_supply_{sid}"):
                    data["supplies"] = [s for s in data["supplies"] if s.get("id") != sid]
                    save_data(data)
                    st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("✅ Clear Checked Items"):
                data["supplies"] = [s for s in data["supplies"] if not s.get("checked", False)]
                save_data(data)
                st.rerun()
        with bc2:
            if st.button("🗑 Clear All"):
                data["supplies"] = []
                save_data(data)
                st.rerun()

# ── TAB 5 — Projects ──────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-header">Projects</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Sans;font-size:0.85rem;color:#a08060;margin-bottom:1rem;">Select orders to group into a project and see exactly how many bags you need to cook.</div>', unsafe_allow_html=True)

    if not data["orders"]:
        st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No orders yet.</div>', unsafe_allow_html=True)
    else:
        if "projects" not in data:
            data["projects"] = []

        proj_left, proj_right = st.columns([1, 1], gap="large")

        with proj_left:
            st.markdown('<div class="section-header">Create / Update Project</div>', unsafe_allow_html=True)

            with st.form("project_form", clear_on_submit=False):
                proj_name = st.text_input("Project Name", placeholder="e.g. Feb Batch, Week 1 Ship...")

                st.markdown('<div style="font-family:DM Mono;font-size:0.7rem;color:#7a6040;letter-spacing:2px;text-transform:uppercase;margin:0.75rem 0 0.25rem 0;">Select Orders</div>', unsafe_allow_html=True)

                selected_ids = []
                for order in sorted(data["orders"], key=lambda o: o.get("date",""), reverse=True):
                    oid = order.get("id")
                    items_str = " · ".join([f"{qty} {f}" for f, qty in order["items"].items()])
                    status = order.get("status", "New")
                    label = f"{order['customer']} — {items_str} ({status})"
                    if st.checkbox(label, key=f"proj_sel_{oid}"):
                        selected_ids.append(oid)

                if st.form_submit_button("💾 Save Project"):
                    if not proj_name:
                        st.error("Enter a project name.")
                    elif not selected_ids:
                        st.error("Select at least one order.")
                    else:
                        # Update existing or add new
                        existing = next((p for p in data["projects"] if p["name"] == proj_name), None)
                        if existing:
                            existing["order_ids"] = selected_ids
                            existing["updated"] = datetime.now().strftime("%b %d")
                        else:
                            data["projects"].append({
                                "id": max([p.get("id",0) for p in data["projects"]], default=0) + 1,
                                "name": proj_name,
                                "order_ids": selected_ids,
                                "created": datetime.now().strftime("%b %d"),
                                "updated": datetime.now().strftime("%b %d"),
                            })
                        save_data(data)
                        st.success(f"Project '{proj_name}' saved!")
                        st.rerun()

        with proj_right:
            st.markdown('<div class="section-header">Saved Projects</div>', unsafe_allow_html=True)

            if not data.get("projects"):
                st.markdown('<div style="color:#7a6040;font-family:DM Mono;font-size:0.8rem;padding:1rem 0;">No projects yet.</div>', unsafe_allow_html=True)
            else:
                for proj in data["projects"]:
                    proj_orders = [o for o in data["orders"] if o.get("id") in proj["order_ids"]]

                    # Tally bags per flavor
                    flavor_totals = {}
                    for o in proj_orders:
                        for flavor, qty in o.get("items", {}).items():
                            flavor_totals[flavor] = flavor_totals.get(flavor, 0) + qty
                    total_bags = sum(flavor_totals.values())
                    trays = round(total_bags / (50/36), 1)
                    batches = round(trays / 36, 2)

                    # Build flavor breakdown HTML
                    flavor_rows = "".join([
                        f'<div style="display:flex;justify-content:space-between;padding:0.2rem 0;border-bottom:1px solid #2e1f0a;"><span style="font-family:DM Sans;font-size:0.85rem;color:#f0ead6;">{f}</span><span style="font-family:DM Mono;font-size:0.85rem;color:#c4984a;">{q} bags</span></div>'
                        for f, q in flavor_totals.items()
                    ])
                    customer_list = ", ".join([o["customer"] for o in proj_orders])

                    st.markdown(f"""
                    <div style="background:#1a1208;border:1px solid #2e1f0a;border-radius:12px;padding:1.25rem;margin-bottom:1rem;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem;">
                            <div>
                                <div style="font-family:Playfair Display,serif;font-size:1.2rem;font-weight:700;color:#f0ead6;">{proj["name"]}</div>
                                <div style="font-family:DM Mono;font-size:0.65rem;color:#7a6040;margin-top:0.15rem;">{len(proj_orders)} orders · Updated {proj.get("updated","")}</div>
                                <div style="font-family:DM Sans;font-size:0.78rem;color:#7a6040;margin-top:0.2rem;">{customer_list}</div>
                            </div>
                            <div style="text-align:right;">
                                <div class="total-badge">{total_bags} bags</div>
                                <div style="font-family:DM Mono;font-size:0.65rem;color:#c4984a;margin-top:0.3rem;">{trays} trays · {batches} batches</div>
                            </div>
                        </div>
                        {flavor_rows}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🗑 Delete Project", key=f"del_proj_{proj['id']}"):
                        data["projects"] = [p for p in data["projects"] if p["id"] != proj["id"]]
                        save_data(data)
                        st.rerun()

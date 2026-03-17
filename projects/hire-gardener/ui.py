import streamlit as st
import pandas as pd
import time
from config import MODE
from workflow import (
    stage_1_discover,
    stage_2_outreach,
    stage_3_quote,
    stage_5_confirm,
    stage_6_verify
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hire Gardener",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state defaults ─────────────────────────────────────────────────────
_defaults = {
    "stage": 0,
    "area": "",
    "uploaded_image": None,
    "vendors": [],
    "conversations": {},
    "quotes": [],
    "selected_vendor": None,
    "job_scope": "",
    "verification_report": "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Hire Gardener")
    st.divider()

    stage_labels = [
        "1. Discovery",
        "2. Outreach",
        "3. Quote Request",
        "4. Select Provider",
        "5. Confirmation",
        "6. Verification",
    ]
    current = st.session_state.stage
    for i, label in enumerate(stage_labels):
        if i < current:
            st.markdown(f"✅ {label}")
        elif i == current:
            st.markdown(f"**▶️ {label}**")
        else:
            st.markdown(f"⬜ {label}")

    st.divider()

    if MODE == "mock":
        st.success("🟢 MOCK MODE")
        st.caption("Vendor responses are simulated by Llama3.")
    else:
        st.error("🔴 LIVE MODE")
        st.caption("Connected to real WhatsApp.")

    if current > 0:
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🌿 Hire Gardener")
st.caption("AI-powered grass cutting service finder — your AI handles all vendor communication")
st.divider()


# ── Helper: render a conversation ─────────────────────────────────────────────
def render_conversation(vendor_id, show_image=False):
    conv = st.session_state.conversations.get(vendor_id, [])
    for msg in conv:
        role = "user" if msg["role"] == "agent" else "assistant"
        with st.chat_message(role):
            if msg.get("has_media") and show_image:
                if st.session_state.uploaded_image:
                    st.image(st.session_state.uploaded_image, width=180,
                             caption="Area photo sent to vendor")
                else:
                    st.markdown("📷 *Area photo attached*")
                st.markdown("🎥 *Area video attached*")
            # Strip the media indicators from display text
            text = msg["text"].replace("\n\n📷 [Area photo attached]\n🎥 [Area video attached]", "")
            st.write(text)


# ── Stage 0: Input ────────────────────────────────────────────────────────────
if current == 0:
    st.subheader("Step 1 — Tell us where you need grass cut")

    area = st.text_input(
        "Service area",
        placeholder="e.g. Taman Tun Dr Ismail, Kuala Lumpur",
        help="Enter the neighbourhood or area where the grass needs cutting"
    )

    st.subheader("Step 2 — Share the area details")
    col1, col2 = st.columns(2)
    with col1:
        image_file = st.file_uploader(
            "Area photo (circle the grass area before uploading)",
            type=["jpg", "jpeg", "png"]
        )
        if image_file:
            st.image(image_file, caption="Your uploaded photo", use_container_width=True)
    with col2:
        video_file = st.file_uploader(
            "Area video (optional but recommended)",
            type=["mp4", "mov", "avi"]
        )
        if video_file:
            st.video(video_file)

    st.divider()

    if st.button("🔍 Find Providers", type="primary", disabled=not area):
        st.session_state.area = area
        st.session_state.uploaded_image = image_file.read() if image_file else None
        with st.spinner("Finding grass cutting providers in your area..."):
            vendors = stage_1_discover(area)
            st.session_state.vendors = vendors
            for v in vendors:
                st.session_state.conversations[v["id"]] = []
        st.session_state.stage = 1
        st.rerun()


# ── Stage 1: Discovery ────────────────────────────────────────────────────────
elif current == 1:
    st.subheader(f"Providers found in {st.session_state.area}")

    cols = st.columns(3)
    for i, v in enumerate(st.session_state.vendors):
        with cols[i]:
            st.metric(label=v["name"], value=v["number"])

    st.divider()
    st.info("Your AI will now contact all 3 providers to check if they cover your area.")

    if st.button("📤 Send Initial Outreach to All Providers", type="primary"):
        with st.spinner("Sending outreach messages and waiting for replies..."):
            conversations = stage_2_outreach(st.session_state.vendors, st.session_state.area)
            st.session_state.conversations = conversations
        st.session_state.stage = 2
        st.rerun()


# ── Stage 2: Outreach ─────────────────────────────────────────────────────────
elif current == 2:
    st.subheader("Initial Outreach — Provider Responses")

    cols = st.columns(3)
    for i, v in enumerate(st.session_state.vendors):
        with cols[i]:
            st.markdown(f"**{v['name']}**")
            st.caption(v["number"])
            st.divider()
            render_conversation(v["id"])

    st.divider()
    st.info("Providers have confirmed availability. Ready to share your area photo and request quotes.")

    if st.button("📎 Send Area Photo & Request Quote from All", type="primary"):
        with st.spinner("Sending photo and video — requesting quotes..."):
            conversations, quotes = stage_3_quote(
                st.session_state.vendors,
                st.session_state.conversations
            )
            st.session_state.conversations = conversations
            st.session_state.quotes = quotes
        st.session_state.stage = 3
        st.rerun()


# ── Stage 3: Quoting ──────────────────────────────────────────────────────────
elif current == 3:
    st.subheader("Quote Requests — Provider Responses")

    cols = st.columns(3)
    for i, v in enumerate(st.session_state.vendors):
        with cols[i]:
            st.markdown(f"**{v['name']}**")
            st.caption(v["number"])
            st.divider()
            render_conversation(v["id"], show_image=True)

    st.divider()

    if st.button("📊 View Quote Comparison", type="primary"):
        st.session_state.stage = 4
        st.rerun()


# ── Stage 4: Quote Comparison ─────────────────────────────────────────────────
elif current == 4:
    st.subheader("Quote Comparison")

    active = [q for q in st.session_state.quotes if not q.get("declined")]
    declined = [q for q in st.session_state.quotes if q.get("declined")]

    if active:
        df = pd.DataFrame([{
            "Provider": q["vendor_name"],
            "WhatsApp": q["number"],
            "Rate (RM)": q["rate"],
            "Available": q["availability"]
        } for q in active])
        st.dataframe(df, use_container_width=True, hide_index=True)

    for d in declined:
        st.warning(f"⚠️ **{d['vendor_name']}** is unable to take this job — outside their service area.")

    st.divider()
    st.subheader("Select Your Provider")

    options = {
        f"{q['vendor_name']}  —  RM {q['rate']}  —  {q['availability']}": q
        for q in active
    }
    selected_label = st.radio("Choose a provider:", list(options.keys()))

    if st.button("✅ Confirm This Provider", type="primary"):
        st.session_state.selected_vendor = options[selected_label]
        with st.spinner("Sending confirmation and job scope to provider..."):
            conversations, job_scope = stage_5_confirm(
                st.session_state.selected_vendor,
                st.session_state.conversations
            )
            st.session_state.conversations = conversations
            st.session_state.job_scope = job_scope
        st.session_state.stage = 5
        st.rerun()


# ── Stage 5: Confirmation ─────────────────────────────────────────────────────
elif current == 5:
    sv = st.session_state.selected_vendor
    st.subheader("Booking Confirmed")

    col1, col2, col3 = st.columns(3)
    col1.metric("Provider", sv["vendor_name"])
    col2.metric("Rate", f"RM {sv['rate']}")
    col3.metric("Service Date", sv["availability"])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Conversation with {sv['vendor_name']}")
        render_conversation(sv["vendor_id"], show_image=True)
    with col2:
        st.subheader("Confirmed Job Scope")
        st.info(st.session_state.job_scope)
        st.caption("Provider has acknowledged and confirmed this scope.")

    st.divider()
    st.info("Waiting for the provider to complete the job and send a completion report.")

    if st.button("⏳ Provider Reports Job Complete — Verify Now", type="primary"):
        with st.spinner("Receiving completion report and running AI verification..."):
            time.sleep(1)
            report = stage_6_verify(sv, st.session_state.job_scope)
            st.session_state.verification_report = report
        st.session_state.stage = 6
        st.rerun()


# ── Stage 6: Verification ─────────────────────────────────────────────────────
elif current == 6:
    sv = st.session_state.selected_vendor
    st.subheader("Job Completion Verification")
    st.success(f"✅ **{sv['vendor_name']}** has reported the job as complete.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Job Scope")
        st.info(st.session_state.job_scope)
    with col2:
        st.subheader("Provider Completion Report")
        st.write(
            "The provider has sent completion photos confirming "
            "all grass has been cut as instructed."
        )
        st.caption("📷 Completion photos received")

    st.divider()
    st.subheader("AI Verification Report")
    st.success(st.session_state.verification_report)

    st.divider()
    st.subheader("Payment")
    col1, col2 = st.columns(2)
    col1.metric("Amount Due", f"RM {sv['rate']}")
    col2.metric("Pay To", sv["vendor_name"])

    if st.button("💰 Payment Sent — Close Job", type="primary"):
        st.balloons()
        st.success(
            f"🎉 Job complete! Payment confirmed. Workflow closed.\n\n"
            f"Job done by **{sv['vendor_name']}** on **{sv['availability']}**."
        )
        st.caption("Thank you for using Hire Gardener.")

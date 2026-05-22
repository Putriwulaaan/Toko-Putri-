import streamlit as st
from FSM import PutriFSM, State

# Konfigurasi Halaman (Opsional, agar judul tab browser lebih bagus)
st.set_page_config(page_title="Toko Putri Chatbot", page_icon="🛍️")

st.title("🛍️ Chatbot Toko Putri")

# --- INISIALISASI SESSION STATE ---
if "bot_fsm" not in st.session_state:
    st.session_state.bot_fsm = PutriFSM()
    st.session_state.bot_fsm.step() # Jalankan sapaan pertama
    
    st.session_state.messages = [
        {"role": "assistant", "content": st.session_state.bot_fsm.get_response()}
    ]

# --- MENAMPILKAN RIWAYAT CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KOLOM INPUT USER & PROSES BALASAN ---
# PERBAIKAN DI SINI: Menggunakan Walrus Operator (:=)
if prompt := st.chat_input("Ketik pesan Anda di sini... (contoh: 'menu', 'pesan 2 jam tangan')"):
    
    # 1. Tampilkan pesan user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Proses pesan ke FSM
    bot = st.session_state.bot_fsm
    bot.step(prompt) 
    balasan = bot.get_response()
    
    # 3. Tampilkan balasan utama dari bot
    with st.chat_message("assistant"):
        st.markdown(balasan)
    st.session_state.messages.append({"role": "assistant", "content": balasan})
    
    # 4. AUTO-RESET SETELAH PEMBAYARAN
    # Jika status kembali ke IDLE setelah transaksi sukses, reset bot untuk pesanan baru
    if bot.state == State.IDLE:
        st.session_state.bot_fsm = PutriFSM()
        st.session_state.bot_fsm.step() # Siapkan sapaan awal
        sapaan_baru = st.session_state.bot_fsm.get_response()
        
        # Tampilkan sapaan awal untuk pesanan berikutnya
        with st.chat_message("assistant"):
            st.markdown(sapaan_baru)
        st.session_state.messages.append({"role": "assistant", "content": sapaan_baru})

# --- SIDEBAR: TAMPILAN KERANJANG REAL-TIME ---
with st.sidebar:
    st.header("🛒 Keranjang Belanja")
    
    keranjang_saat_ini = st.session_state.bot_fsm.cart
    
    if not keranjang_saat_ini:
        st.info("Keranjang Anda masih kosong.")
    else:
        for item in keranjang_saat_ini:
            st.write(f"{item['emoji']} **{item['item']}** (x{item['qty']})")
            st.write(f"Rp {item['price'] * item['qty']:,}")
            st.divider()
        
        total = st.session_state.bot_fsm.calculate_total()
        st.success(f"**Total Sementara: Rp {total:,}**")
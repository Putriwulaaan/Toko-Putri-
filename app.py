import streamlit as st
# Mengimpor FSM yang sudah kamu buat
from FSM import PutriFSM, State

st.title("🛍️ Chatbot Toko Putri")

# --- INISIALISASI SESSION STATE ---
# Kita gunakan session_state agar memori chatbot (state, keranjang, riwayat chat)
# tidak hilang saat halaman web di-refresh atau user mengetik pesan baru.

if "bot_fsm" not in st.session_state:
    st.session_state.bot_fsm = PutriFSM()
    
    # Jalankan step pertama (IDLE ke ORDERING) agar bot menyapa duluan
    st.session_state.bot_fsm.step()
    
    # Simpan sapaan pertama ke dalam riwayat pesan
    st.session_state.messages = [
        {"role": "assistant", "content": st.session_state.bot_fsm.get_response()}
    ]

# --- MENAMPILKAN RIWAYAT CHAT ---
# Loop untuk menampilkan semua pesan yang sudah ada
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KOLOM INPUT USER & PROSES BALASAN ---
# Menampilkan kotak input di bagian bawah
prompt = st.chat_input("Ketik pesan Anda di sini... (contoh: 'menu', 'pesan 2 jam tangan')")

if prompt:
    # 1. Tampilkan pesan yang baru diketik user ke layar
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Simpan pesan user ke dalam riwayat memori
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Proses input user menggunakan FSM (bot berpikir)
    bot = st.session_state.bot_fsm
    bot.step(prompt)

    # 4. Ambil balasan dari bot
    balasan = bot.get_response()

    # 5. Tampilkan pesan balasan bot ke layar
    with st.chat_message("assistant"):
        st.markdown(balasan)

    # 6. Simpan balasan bot ke dalam riwayat memori
    st.session_state.messages.append({"role": "assistant", "content": balasan})

    # (Opsional) Reset otomatis jika state kembali ke IDLE (pembayaran selesai)
    if bot.state == State.IDLE:
        st.session_state.bot_fsm = PutriFSM()
        st.session_state.bot_fsm.step()  # sapaan berikutnya
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.bot_fsm.get_response()})

# --- SIDEBAR: TAMPILAN KERANJANG REAL-TIME ---
# Kita buat sidebar di sebelah kiri untuk melihat isi keranjang dengan mudah
with st.sidebar:
    st.header("🛒 Keranjang Belanja")
    
    keranjang_saat_ini = st.session_state.bot_fsm.cart
    
    if not keranjang_saat_ini:
        st.info("Keranjang Anda masih kosong.")
    else:
        for item in keranjang_saat_ini:
            st.write(f"{item['emoji']} **{item['item']}** (x{item['qty']})")
            st.write(f"Rp {item['price'] * item['qty']:,}")
            st.divider() # Garis pembatas
        
        # Total harga keseluruhan
        total = st.session_state.bot_fsm.calculate_total()
        st.success(f"**Total Sementara: Rp {total:,}**")
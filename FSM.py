from enum import Enum, auto
from engine import NLPEngine

class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()

class PutriFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.cart = []
        self.response = ""

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def get_menu_text(self):
        """Fungsi bantuan untuk merangkai teks daftar barang"""
        teks_menu = "**🛍️ Daftar Barang Logic Toko Putri:**\n\n"
        for key, data in self.nlp.menu_data.items():
            teks_menu += f"- {data['emoji']} **{key.capitalize()}** (Rp {data['price']:,}): *{data['desc']}*\n"
        teks_menu += "\nSilakan ketik pesanan Anda (contoh: *'Pesan , 2 Dress, 1 Jam Tangan'*)."
        return teks_menu

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        """Logika untuk mengurangi qty item atau menghapusnya jika qty <= 0"""
        for item in list(self.cart):
            if item['item'] == item_to_reduce:
                item['qty'] -= qty_to_remove
                if item['qty'] <= 0:
                    self.cart.remove(item)
                    return f"❌ **{item_to_reduce}** telah dihapus dari keranjang."
                return f"📉 **{item_to_reduce}** telah dikurangi {qty_to_remove}. Sisa: {item['qty']}"
        return f"gagal: **{item_to_reduce}** tidak ditemukan di keranjang anda." 

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)
        if self.state == State.IDLE:
            self.response = "Halo! Mau pesan apa hari ini? Ketik 'menu' untuk melihat pilihan."
            self.state = State.ORDERING
            
        elif self.state == State.ORDERING:
            intent = self.nlp.detect_intent(user_input)
            
            if intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang masih kosong."
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"Total: **Rp {self.calculate_total():,}**. Lanjut bayar? (Ya/Tidak)"
            elif intent == "ASK_MENU":
                self.response = self.get_menu_text()
            else:
                # Logika Penambahan Pesanan
                new_orders = self.nlp.parse_orders(user_input)
                if new_orders:
                    for order in new_orders:
                        # Cek jika item sudah ada, tambah qty saja
                        existing = next((i for i in self.cart if i['item'] == order['item']), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            # Info harga & emoji otomatis masuk dari engine
                            menu_info = self.nlp.menu_data[order['item']]
                            order.update({"price": menu_info['price'], "emoji": menu_info['emoji']})
                            self.cart.append(order)
                    self.response = "✔️Pesanan ditambahkan. Ada lagi? (Ketik 'bayar' untuk selesai)"
                else:
                    self.response = "Maaf, saya tidak mengerti. Coba: *'pesan 3 Jam Tangan'* *'2 Tas Punggung'* atau *'hapus 1 Jam Tangan'*"

        elif self.state == State.CONFIRMATION:
            intent = self.nlp.detect_intent(user_input)
            if intent == "YES":
                self.state = State.PAYMENT
                self.step() # Auto-step ke PAYMENT
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Oke, silakan tambah pesanan lagi."
            else:
                self.response = "Mohon jawab dengan 'Ya' atau 'Tidak'."
        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"👍 Pembayaran berhasil diproses! Pembayaran Rp {total:,} diterima. Pesanan diproses."
            self.state = State.IDLE
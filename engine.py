import re

class NLPEngine:
    def __init__(self):
        # Database Menu dengan Info Tambahan untuk UI
        self.menu_data = {
            "Jam Tangan": {"price": 1000000, "emoji": "⌚", "desc": "Jam tangan vintage"},
            "Tas Punggung": {"price": 350000, "emoji": "🎒", "desc": "Tas punggung laptop"},
            "Dress": {"price": 1500000, "emoji": "👗", "desc": "Dress wanita"},
            "Set Seragam Sekolah": {"price": 250000, "emoji": "👔", "desc": "Satu set seragam sekolah dewasa"}
        }
        
        # Regex Patterns
        self.re_number = r"\b(\d+)\b"
        
        # Membuat pola regex dinamis dari keys menu
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b" # Pemisah kalimat (koma, titik, 'dan', '&')
        
        # Regex untuk pembatalan/pengurangan
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def _parse_single_segment(self, text):
        """Helper untuk memproses satu potongan kalimat (misal: '3 Jam Tangan')"""
        text = text.lower().strip()
        
        # 1. Cari Item
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None
        item_key = item_match.group(1)
        
        # 2. Cari Jumlah (Default 1)
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1
        
        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]['price'],
            "emoji": self.menu_data[item_key]['emoji']
        }

    def parse_orders(self, full_text):
        """Memecah kalimat majemuk: 'pesan jam tangan 3, tas punggung 2' Menjadi list orders."""
        segments = re.split(self.re_split, full_text)
        found_orders = []
        for segment in segments:
            if segment.strip():
                order = self._parse_single_segment(segment)
                if order:
                    found_orders.append(order)
        return found_orders

    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang|batal semua)\b", text):
            return "RESET"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        if re.search(r"\b(menu|daftar|apa saja|jual apa|list)\b", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|betul|siap|baik)\b", text):
            return "YES"
        if re.search(r"\b(tidak|enggak|batal|no|salah)\b", text):
            return "NO"
        return "UNKNOWN"

    def print_menu(self):
        print(self.menu_data)
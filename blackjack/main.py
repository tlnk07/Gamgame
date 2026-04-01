import customtkinter as ctk
import random
import os
from tkinter import messagebox
from PIL import Image, ImageDraw

# ------------------ Cấu hình giao diện ------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ------------------ Kích thước ------------------
CARD_WIDTH = 70
CARD_HEIGHT = 98
CHIP_SIZE = 48
SPECIAL_CARD_WIDTH = 80
SPECIAL_CARD_HEIGHT = 110

# ------------------ Lớp xử lý game Blackjack ------------------
class BlackjackGame:
    def __init__(self):
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.player_stand = False
        self.new_deck()

    def new_deck(self):
        suits = ['clubs', 'diamonds', 'hearts', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        self.deck = [f"{rank}_of_{suit}" for suit in suits for rank in ranks]
        random.shuffle(self.deck)

    def deal_card(self):
        return self.deck.pop()

    def calculate_hand(self, hand):
        total = 0
        aces = 0
        for card in hand:
            rank = card.split('_')[0]
            if rank in ['jack', 'queen', 'king']:
                total += 10
            elif rank == 'ace':
                aces += 1
                total += 11
            else:
                total += int(rank)
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total

    def start_round(self):
        self.game_over = False
        self.player_stand = False
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]

    def hit(self):
        if self.game_over or self.player_stand:
            return False
        self.player_hand.append(self.deal_card())
        if self.calculate_hand(self.player_hand) > 21:
            self.game_over = True
            return False
        return True

    def stand(self):
        if self.game_over or self.player_stand:
            return
        self.player_stand = True
        while self.calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deal_card())
        self.game_over = True

    def get_result(self):
        player_score = self.calculate_hand(self.player_hand)
        dealer_score = self.calculate_hand(self.dealer_hand)
        if player_score > 21:
            return "lose"
        if dealer_score > 21:
            return "win"
        if player_score > dealer_score:
            return "win"
        elif player_score < dealer_score:
            return "lose"
        else:
            return "push"

# ------------------ Lớp ứng dụng chính ------------------
class BlackjackApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blackjack - 21 Points")
        self.geometry("1100x700")
        self.resizable(False, False)

        # Dữ liệu game
        self.game = BlackjackGame()
        self.money = 100000
        self.current_bet = 0
        self.bet_in_progress = False
        self.game_active = False
        self.special_cards = {}

        # Tải ảnh
        self.card_images = {}
        self.chip_images = {}
        self.load_card_images()
        self.load_chip_images()

        # Tạo các thẻ đặc biệt
        self.init_special_cards()

        # Xây dựng giao diện
        self.setup_ui()

        # Cập nhật hiển thị ban đầu
        self.update_money_display()
        self.update_bet_display()
        self.update_special_cards_display()
        self.new_game()

    # ------------------ Tải ảnh ------------------
    def load_card_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "card_pngs", "card_faces")
        if not os.path.exists(base_path):
            messagebox.showerror("Error", f"Thư mục ảnh card không tồn tại: {base_path}")
            return
        for filename in os.listdir(base_path):
            if filename.endswith(".png"):
                name = filename[:-4]
                img_path = os.path.join(base_path, filename)
                try:
                    pil_img = Image.open(img_path).resize((CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS)
                    self.card_images[name] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(CARD_WIDTH, CARD_HEIGHT))
                except Exception as e:
                    print(f"Không thể load {img_path}: {e}")

        # Tải ảnh Joker cho thẻ đặc biệt
        joker_path = os.path.join(base_path, "joker.png")
        if os.path.exists(joker_path):
            try:
                pil_img = Image.open(joker_path).resize((SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT), Image.Resampling.LANCZOS)
                self.card_images["joker_front"] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT))
            except Exception as e:
                print(f"Không thể load joker: {e}")

        # Tải ảnh Joker 1 (Joker 1)
        joker1_path = os.path.join(base_path, "joker_1.png")
        if os.path.exists(joker1_path):
            try:
                pil_img = Image.open(joker1_path).resize((SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT), Image.Resampling.LANCZOS)
                self.card_images["joker_1_front"] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT))
            except Exception as e:
                print(f"Không thể load joker_1: {e}")

        # Tải ảnh cho các cấp độ Joker nếu có (joker_2.png, joker_3.png, ...)
        for i in range(2, 10):
            filename = f"joker_{i}.png"
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path).resize((SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT), Image.Resampling.LANCZOS)
                    self.card_images[f"joker_{i}_front"] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT))
                except Exception as e:
                    print(f"Không thể load {filename}: {e}")

        # Mặt sau bài (dùng cho thẻ đặc biệt khi locked)
        back_path = os.path.join(base_path, "back.png")
        if os.path.exists(back_path):
            pil_img = Image.open(back_path).resize((SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT), Image.Resampling.LANCZOS)
            self.card_images["special_back"] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT))
        else:
            img = Image.new("RGB", (SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT), "#2C3E50")
            draw = ImageDraw.Draw(img)
            draw.rectangle([5, 5, SPECIAL_CARD_WIDTH-5, SPECIAL_CARD_HEIGHT-5], outline="#ECF0F1", width=2)
            draw.line([(10, 10), (SPECIAL_CARD_WIDTH-10, SPECIAL_CARD_HEIGHT-10)], fill="#ECF0F1", width=2)
            draw.line([(SPECIAL_CARD_WIDTH-10, 10), (10, SPECIAL_CARD_HEIGHT-10)], fill="#ECF0F1", width=2)
            self.card_images["special_back"] = ctk.CTkImage(light_image=img, dark_image=img, size=(SPECIAL_CARD_WIDTH, SPECIAL_CARD_HEIGHT))

        # Mặt sau bài cho game (kích thước nhỏ)
        back_small_path = os.path.join(base_path, "back.png")
        if os.path.exists(back_small_path):
            pil_img = Image.open(back_small_path).resize((CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS)
            self.card_images["back"] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(CARD_WIDTH, CARD_HEIGHT))
        else:
            img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "#2C3E50")
            draw = ImageDraw.Draw(img)
            draw.rectangle([5, 5, CARD_WIDTH-5, CARD_HEIGHT-5], outline="#ECF0F1", width=2)
            draw.line([(10, 10), (CARD_WIDTH-10, CARD_HEIGHT-10)], fill="#ECF0F1", width=2)
            draw.line([(CARD_WIDTH-10, 10), (10, CARD_HEIGHT-10)], fill="#ECF0F1", width=2)
            self.card_images["back"] = ctk.CTkImage(light_image=img, dark_image=img, size=(CARD_WIDTH, CARD_HEIGHT))

    def load_chip_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "chip_pngs")
        if not os.path.exists(base_path):
            messagebox.showerror("Error", f"Thư mục chip không tồn tại: {base_path}")
            return
        for filename in os.listdir(base_path):
            if filename.endswith(".png") and filename[:-4].isdigit():
                value = int(filename[:-4])
                img_path = os.path.join(base_path, filename)
                try:
                    pil_img = Image.open(img_path).resize((CHIP_SIZE, CHIP_SIZE), Image.Resampling.LANCZOS)
                    self.chip_images[value] = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(CHIP_SIZE, CHIP_SIZE))
                except Exception as e:
                    print(f"Không thể load chip {img_path}: {e}")

    def get_card_image(self, card_name, is_back=False):
        if is_back:
            return self.card_images.get("back", None)
        else:
            return self.card_images.get(card_name, None)

    # ------------------ Quản lý thẻ đặc biệt ------------------
    def init_special_cards(self):
        """Khởi tạo danh sách thẻ đặc biệt"""
        self.special_cards = {
            "joker": {
                "name": "Joker",
                "cost": 5000,
                "unlocked": False,
                "description": "Khi thua, được hoàn lại 50% tiền cược",
                "front_image": self.card_images.get("joker_front", None),
                "back_image": self.card_images.get("special_back", None),
                "type": "defense"
            },
            "joker_1": {
                "name": "Joker 1",
                "cost": 10000,
                "unlocked": False,
                "description": "Khi thắng, tiền thưởng nhân 1.1",
                "front_image": self.card_images.get("joker_1_front", None),
                "back_image": self.card_images.get("special_back", None),
                "type": "attack",
                "level": 1,
                "upgrade_cost": 20000
            }
        }

    def update_special_cards_display(self):
        """Cập nhật giao diện khu vực thẻ đặc biệt - xóa và tạo lại"""
        # Xóa các widget cũ
        for widget in self.special_cards_frame.winfo_children():
            widget.destroy()

        self.special_buttons = {}  # Lưu các frame/button để tiện xử lý

        for card_id, card_data in self.special_cards.items():
            # Tạo frame cho từng thẻ
            card_frame = ctk.CTkFrame(self.special_cards_frame, fg_color="transparent")
            card_frame.pack(pady=10)

            # Tạo nút thẻ
            if card_data["unlocked"]:
                img = card_data.get("front_image")
                text = ""
            else:
                img = card_data.get("back_image")
                text = ""
            btn = ctk.CTkButton(
                card_frame,
                image=img,
                text=text,
                width=SPECIAL_CARD_WIDTH,
                height=SPECIAL_CARD_HEIGHT,
                command=lambda cid=card_id: self.on_special_card_click(cid),
                fg_color="transparent"
            )
            btn.pack()
            self.special_buttons[card_id] = btn

            # Nếu là thẻ attack và đã unlock, thêm nút nâng cấp
            if card_data["unlocked"] and card_data.get("type") == "attack":
                level = card_data.get("level", 1)
                upgrade_cost = card_data.get("upgrade_cost", 20000)
                upgrade_btn = ctk.CTkButton(
                    card_frame,
                    text=f"⬆️ Upgrade to Joker {level+1}\n({upgrade_cost} coins)",
                    command=lambda cid=card_id: self.upgrade_attack_card(cid),
                    width=SPECIAL_CARD_WIDTH,
                    height=35,
                    font=ctk.CTkFont(size=10)
                )
                upgrade_btn.pack(pady=5)

    def upgrade_attack_card(self, card_id):
        """Nâng cấp thẻ tấn công"""
        card = self.special_cards[card_id]
        if not card["unlocked"]:
            messagebox.showwarning("Warning", "Bạn chưa mở khóa thẻ này!")
            return
        upgrade_cost = card.get("upgrade_cost", 20000)
        if self.money < upgrade_cost:
            messagebox.showwarning("Warning", f"Không đủ tiền! Cần {upgrade_cost} coins để nâng cấp.")
            return

        # Trừ tiền, tăng level
        self.money -= upgrade_cost
        card["level"] += 1
        new_level = card["level"]
        # Cập nhật tên và chi phí nâng cấp tiếp theo
        card["name"] = f"Joker {new_level}"
        card["description"] = f"Khi thắng, tiền thưởng nhân {1 + 0.1 * new_level:.1f}"
        card["upgrade_cost"] = upgrade_cost * 2   # Chi phí tăng gấp đôi

        # Cập nhật ảnh nếu có file tương ứng (joker_2.png, joker_3.png,...)
        front_img_key = f"joker_{new_level}_front"
        if front_img_key in self.card_images:
            card["front_image"] = self.card_images[front_img_key]
        # Nếu không có ảnh, vẫn giữ ảnh cũ (hoặc để None)

        self.update_money_display()
        self.update_special_cards_display()   # Refresh toàn bộ khu vực thẻ
        messagebox.showinfo("Success", f"Đã nâng cấp lên {card['name']}!\nHiệu ứng: {card['description']}")

    def on_special_card_click(self, card_id):
        """Xử lý khi click vào thẻ đặc biệt"""
        card = self.special_cards[card_id]
        if card["unlocked"]:
            messagebox.showinfo(card["name"], f"Hiệu ứng: {card['description']}")
        else:
            response = messagebox.askyesno(
                f"Unlock {card['name']}",
                f"Mở khóa {card['name']} với giá {card['cost']} coins?\n\nHiệu ứng: {card['description']}"
            )
            if response:
                self.unlock_special_card(card_id)

    def unlock_special_card(self, card_id):
        if card_id not in self.special_cards:
            return
        card = self.special_cards[card_id]
        if card["unlocked"]:
            messagebox.showinfo("Info", f"Bạn đã sở hữu {card['name']} rồi!")
            return
        if self.money < card["cost"]:
            messagebox.showwarning("Warning", f"Không đủ tiền! Cần {card['cost']} coins.")
            return

        self.money -= card["cost"]
        card["unlocked"] = True
        if card_id == "joker_1":
            card["level"] = 1
            card["upgrade_cost"] = 20000
            card["name"] = "Joker 1"
            card["description"] = "Khi thắng, tiền thưởng nhân 1.1"
        self.update_money_display()
        self.update_special_cards_display()
        messagebox.showinfo("Success", f"Bạn đã mở khóa {card['name']}!\nHiệu ứng: {card['description']}")

    # ------------------ Xây dựng giao diện ------------------
    def setup_ui(self):
        # Tạo container chính với 2 cột
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Cột trái: Game
        self.game_frame = ctk.CTkFrame(self.main_container)
        self.game_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Cột phải: Special Cards
        self.special_frame = ctk.CTkFrame(self.main_container, width=120)
        self.special_frame.pack(side="right", fill="y", padx=(10, 0))
        self.special_frame.pack_propagate(False)

        # Tiêu đề khu đặc biệt
        special_title = ctk.CTkLabel(self.special_frame, text="✨ Special Cards", font=ctk.CTkFont(size=16, weight="bold"))
        special_title.pack(pady=10)

        # Scrollable frame cho các thẻ đặc biệt
        self.special_cards_frame = ctk.CTkScrollableFrame(self.special_frame, width=100)
        self.special_cards_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Tiêu đề game
        title = ctk.CTkLabel(self.game_frame, text="🃏 Blackjack", font=ctk.CTkFont(size=32, weight="bold"))
        title.pack(pady=(5, 5))

        # Khung thông tin tiền và cược
        info_frame = ctk.CTkFrame(self.game_frame)
        info_frame.pack(fill="x", padx=15, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)

        self.money_label = ctk.CTkLabel(info_frame, text="Money: 1000", font=ctk.CTkFont(size=18, weight="bold"))
        self.money_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.bet_label = ctk.CTkLabel(info_frame, text="Bet: 0", font=ctk.CTkFont(size=18, weight="bold"))
        self.bet_label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Nút Work
        self.work_btn = ctk.CTkButton(info_frame, text="💼 Work (+10)", command=self.work, width=100, height=30)
        self.work_btn.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Thanh trượt
        self.bet_slider = ctk.CTkSlider(info_frame, from_=0, to=self.money, command=self.on_bet_slider, width=300)
        self.bet_slider.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.bet_slider.set(0)

        # Chip và nút reset
        self.chip_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        self.chip_frame.grid(row=3, column=0, columnspan=2, pady=5)

        chip_values = [1, 10, 100, 500]
        for val in chip_values:
            if val in self.chip_images:
                btn = ctk.CTkButton(self.chip_frame, image=self.chip_images[val], text="", width=CHIP_SIZE, height=CHIP_SIZE,
                                   command=lambda v=val: self.add_bet(v))
                btn.pack(side="left", padx=3)
            else:
                btn = ctk.CTkButton(self.chip_frame, text=str(val), width=CHIP_SIZE, height=CHIP_SIZE,
                                   command=lambda v=val: self.add_bet(v))
                btn.pack(side="left", padx=3)

        self.reset_bet_btn = ctk.CTkButton(self.chip_frame, text="Reset Bet", command=self.reset_bet, width=80)
        self.reset_bet_btn.pack(side="left", padx=5)

        # Nút Place Bet
        self.bet_btn = ctk.CTkButton(info_frame, text="Place Bet", command=self.place_bet, width=120)
        self.bet_btn.grid(row=4, column=0, columnspan=2, pady=5)

        # Khu vực dealer
        dealer_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        dealer_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(dealer_frame, text="Dealer", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        self.dealer_cards_frame = ctk.CTkFrame(dealer_frame, fg_color="transparent")
        self.dealer_cards_frame.pack(anchor="w")
        self.dealer_score_label = ctk.CTkLabel(dealer_frame, text="Score: ?", font=ctk.CTkFont(size=12))
        self.dealer_score_label.pack(anchor="w")

        # Khu vực người chơi
        player_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        player_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(player_frame, text="You", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        self.player_cards_frame = ctk.CTkFrame(player_frame, fg_color="transparent")
        self.player_cards_frame.pack(anchor="w")
        self.player_score_label = ctk.CTkLabel(player_frame, text="Score: 0", font=ctk.CTkFont(size=12))
        self.player_score_label.pack(anchor="w")

        # Kết quả
        self.result_label = ctk.CTkLabel(self.game_frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.result_label.pack(pady=5)

        # Các nút hành động
        button_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        button_frame.pack(pady=5)
        self.hit_btn = ctk.CTkButton(button_frame, text="Hit", command=self.hit, width=100, height=35,
                                     font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", hover_color="#27ae60", state="disabled")
        self.hit_btn.pack(side="left", padx=8)
        self.stand_btn = ctk.CTkButton(button_frame, text="Stand", command=self.stand, width=100, height=35,
                                       font=ctk.CTkFont(size=14, weight="bold"), fg_color="#e74c3c", hover_color="#c0392b", state="disabled")
        self.stand_btn.pack(side="left", padx=8)
        self.new_game_btn = ctk.CTkButton(button_frame, text="New Game", command=self.new_game, width=100, height=35,
                                          font=ctk.CTkFont(size=14, weight="bold"), fg_color="#3498db", hover_color="#2980b9")
        self.new_game_btn.pack(side="left", padx=8)

        # Lưu reference để dùng trong place_bet, new_game, v.v.
        self.info_frame = info_frame
        self.dealer_frame = dealer_frame
        self.player_frame = player_frame
        self.button_frame = button_frame

    # ------------------ Các phương thức xử lý game ------------------
    def work(self):
        self.money += 10
        self.update_money_display()
        if not self.game_active and not self.bet_in_progress:
            self.update_bet_slider_range()

    def update_money_display(self):
        self.money_label.configure(text=f"Money: {int(self.money)}")
        if not self.game_active and not self.bet_in_progress:
            self.update_bet_slider_range()

    def update_bet_slider_range(self):
        if self.money > 0:
            self.bet_slider.configure(to=self.money)
            if self.current_bet > self.money:
                self.current_bet = self.money
                self.bet_slider.set(self.current_bet)
            else:
                self.bet_slider.set(self.current_bet)
        else:
            self.bet_slider.configure(to=1, from_=0)
            self.bet_slider.set(0)
        self.update_bet_display()

    def update_bet_display(self):
        self.bet_label.configure(text=f"Bet: {int(self.current_bet)}")

    def on_bet_slider(self, value):
        self.current_bet = int(value)
        self.update_bet_display()

    def add_bet(self, amount):
        if self.game_active or self.bet_in_progress:
            return
        new_bet = self.current_bet + amount
        if new_bet <= self.money:
            self.current_bet = new_bet
            self.bet_slider.set(self.current_bet)
            self.update_bet_display()

    def reset_bet(self):
        if self.game_active or self.bet_in_progress:
            messagebox.showinfo("Info", "Cannot reset bet while game is in progress.")
            return
        self.current_bet = 0
        if self.money > 0:
            self.bet_slider.set(0)
        else:
            self.bet_slider.configure(to=1)
            self.bet_slider.set(0)
        self.update_bet_display()

    def place_bet(self):
        if self.game_active or self.bet_in_progress:
            messagebox.showwarning("Warning", "Game is in progress. Finish or start new game.")
            return
        if self.current_bet <= 0:
            messagebox.showwarning("Warning", "Please set a bet greater than 0.")
            return
        if self.current_bet > self.money:
            messagebox.showwarning("Warning", "Insufficient money.")
            return

        self.bet_in_progress = True
        self.game_active = True
        self.money -= self.current_bet
        self.update_money_display()

        # Vô hiệu hóa các điều khiển đặt cược
        self.bet_btn.configure(state="disabled")
        self.bet_slider.configure(state="disabled")
        self.reset_bet_btn.configure(state="disabled")
        self.work_btn.configure(state="disabled")
        for child in self.chip_frame.winfo_children():
            if isinstance(child, ctk.CTkButton):
                child.configure(state="disabled")

        self.game.start_round()
        self.update_display(show_all_dealer=False)
        self.hit_btn.configure(state="normal")
        self.stand_btn.configure(state="normal")

    def clear_cards_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def display_cards(self, frame, hand, hide_second=False):
        self.clear_cards_frame(frame)
        for i, card in enumerate(hand):
            if hide_second and i == 1:
                img = self.get_card_image("", is_back=True)
            else:
                img = self.get_card_image(card, is_back=False)
            if img:
                lbl = ctk.CTkLabel(frame, image=img, text="")
                lbl.pack(side="left", padx=3)

    def update_display(self, show_all_dealer=False):
        # Dealer
        if show_all_dealer:
            self.display_cards(self.dealer_cards_frame, self.game.dealer_hand, hide_second=False)
            dealer_score = self.game.calculate_hand(self.game.dealer_hand)
            self.dealer_score_label.configure(text=f"Score: {dealer_score}")
        else:
            self.display_cards(self.dealer_cards_frame, self.game.dealer_hand, hide_second=True)
            if self.game.game_over:
                dealer_score = self.game.calculate_hand(self.game.dealer_hand)
                self.dealer_score_label.configure(text=f"Score: {dealer_score}")
            else:
                self.dealer_score_label.configure(text="Score: ?")

        # Player
        self.display_cards(self.player_cards_frame, self.game.player_hand, hide_second=False)
        player_score = self.game.calculate_hand(self.game.player_hand)
        self.player_score_label.configure(text=f"Score: {player_score}")

        if self.game.game_over:
            result = self.game.get_result()
            joker_unlocked = self.special_cards.get("joker", {}).get("unlocked", False)
            joker_card = self.special_cards.get("joker_1", {})
            joker_unlocked = joker_card.get("unlocked", False)
            joker_level = joker_card.get("level", 1) if joker_unlocked else 0

            if result == "win":
                win_amount = self.current_bet * 2
                if joker_unlocked:
                    multiplier = 1 + 0.1 * joker_level
                    win_amount = int(win_amount * multiplier)
                    result_text = f"You win! +{win_amount} (x{multiplier:.1f} from Joker {joker_level})"
                else:
                    result_text = f"You win! +{win_amount}"
                self.money += win_amount
            elif result == "lose":
                if joker_unlocked:
                    refund = self.current_bet // 2
                    self.money += refund
                    result_text = f"You lose! Joker saved you: +{refund} coins"
                else:
                    result_text = "You lose!"
            else:  # push
                self.money += self.current_bet
                result_text = "Push! Your bet is returned."

            self.update_money_display()
            self.result_label.configure(text=result_text)
            self.hit_btn.configure(state="disabled")
            self.stand_btn.configure(state="disabled")

            # Kết thúc ván, reset trạng thái
            self.bet_in_progress = False
            self.game_active = False

            # Bật lại các điều khiển cược
            self.bet_btn.configure(state="normal")
            self.bet_slider.configure(state="normal")
            self.reset_bet_btn.configure(state="normal")
            self.work_btn.configure(state="normal")
            for child in self.chip_frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state="normal")

            # Reset cược
            self.current_bet = 0
            if self.money > 0:
                self.bet_slider.set(0)
            else:
                self.bet_slider.configure(to=1)
                self.bet_slider.set(0)
            self.update_bet_display()
        else:
            self.result_label.configure(text="")
            self.hit_btn.configure(state="normal")
            self.stand_btn.configure(state="normal")

    def hit(self):
        if self.game.game_over or not self.game_active:
            return
        self.game.hit()
        self.update_display(show_all_dealer=False)
        if self.game.game_over:
            self.update_display(show_all_dealer=True)

    def stand(self):
        if self.game.game_over or not self.game_active:
            return
        self.game.stand()
        self.update_display(show_all_dealer=True)

    def new_game(self):
        if self.game_active:
            if not messagebox.askyesno("New Game", "Are you sure? Current game will be lost."):
                return
        self.game_active = False
        self.bet_in_progress = False
        self.game.new_deck()

        self.clear_cards_frame(self.dealer_cards_frame)
        self.clear_cards_frame(self.player_cards_frame)
        self.dealer_score_label.configure(text="Score: ?")
        self.player_score_label.configure(text="Score: 0")
        self.result_label.configure(text="")
        self.hit_btn.configure(state="disabled")
        self.stand_btn.configure(state="disabled")

        self.bet_btn.configure(state="normal")
        self.bet_slider.configure(state="normal")
        self.reset_bet_btn.configure(state="normal")
        self.work_btn.configure(state="normal")
        for child in self.chip_frame.winfo_children():
            if isinstance(child, ctk.CTkButton):
                child.configure(state="normal")

        self.update_money_display()
        self.current_bet = 0
        if self.money > 0:
            self.bet_slider.set(0)
        else:
            self.bet_slider.configure(to=1)
            self.bet_slider.set(0)
        self.update_bet_display()

    def on_closing(self):
        self.destroy()

# ------------------ Khởi chạy ------------------
if __name__ == "__main__":
    app = BlackjackApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
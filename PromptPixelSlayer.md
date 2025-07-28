# Prompt Yêu Cầu Lập Trình: Game Widget "Pixel Slayer"

## Mục tiêu dự án

Tạo một ứng dụng widget desktop siêu nhẹ. Widget này hiển thị một nhân vật pixel đang chiến đấu với một quái vật. Mỗi khi người dùng **gõ một phím bất kỳ** trên máy tính, nhân vật sẽ thực hiện một hành động tấn công. Sau khi đạt đủ số lần tấn công, nhân vật và quái vật sẽ tiến hóa lên hình dạng mới.

---

## Yêu cầu chức năng (MVP - Phiên bản tối thiểu)

1.  **Cửa sổ ứng dụng:**
    * Phải là một cửa sổ nhỏ, **không có viền** và **nền trong suốt**.
    * Luôn hiển thị trên cùng (Always on Top).
    * Người dùng có thể kéo thả để thay đổi vị trí.

2.  **Bắt sự kiện:**
    * Phải lắng nghe **sự kiện gõ phím trên toàn hệ thống** (global key listener), không chỉ khi cửa sổ game được focus.
    * Mỗi lần một phím được nhấn, bộ đếm sẽ tăng lên 1.

3.  **Hiển thị & Hoạt ảnh:**
    * Hiển thị 2 hình ảnh pixel art: **Nhân vật** và **Quái vật**.
    * Khi người dùng gõ phím, thay thế hình ảnh của nhân vật bằng sprite "tấn công" trong một khoảnh khắc ngắn (khoảng 100ms) rồi quay về trạng thái đứng yên.
    * Quái vật có thể có hoạt ảnh "nhận sát thương" (ví dụ: chớp đỏ) khi bị tấn công.

4.  **Hệ thống tiến hóa:**
    * Khởi tạo một bộ đếm `attack_count = 0`.
    * Xác định các mốc tiến hóa, ví dụ: `LEVEL_2_THRESHOLD = 5000`.
    * Khi `attack_count` đạt đến mốc, thay đổi file ảnh của Nhân vật và Quái vật sang cấp độ tiếp theo.

---

## Gợi ý về công nghệ (Nhẹ & Nhanh)

* **Ngôn ngữ:** **Python 3**.
* **Thư viện GUI:** **PyQt6** hoặc **PySide6** (rất mạnh để làm cửa sổ trong suốt và tùy biến). Hoặc **Tkinter** (có sẵn nhưng khó tùy biến hơn).
* **Thư viện lắng nghe phím:** **pynput**.

---

## Các bước thực hiện gợi ý

1.  **Bước 1: Dựng giao diện:** Tạo một cửa sổ `QMainWindow` (PyQt) cơ bản. Thiết lập các thuộc tính để cửa sổ trong suốt, không viền và luôn ở trên cùng.
2.  **Bước 2: Hiển thị Sprite:** Dùng `QLabel` để hiển thị 2 file ảnh `.png` (nhân vật và quái vật) trên cửa sổ.
3.  **Bước 3: Lắng nghe phím:** Tích hợp thư viện `pynput` để chạy một listener trong một luồng (thread) riêng. Khi có phím được nhấn, gọi một hàm xử lý trong code chính.
4.  **Bước 4: Logic tấn công & tiến hóa:**
    * Viết hàm `handle_attack()` được gọi bởi listener.
    * Trong hàm này: tăng bộ đếm, kích hoạt hoạt ảnh tấn công (dùng `QTimer` để đổi ảnh trong 100ms), và kiểm tra điều kiện tiến hóa.
    * Nếu đủ điều kiện, cập nhật đường dẫn file ảnh cho các `QLabel`.

---

## Tài nguyên đồ họa cần chuẩn bị (Dạng .PNG nền trong)

* **Nhân vật Cấp 1:**
    * `warrior_lv1_idle.png` (đứng yên)
    * `warrior_lv1_attack.png` (vung kiếm)
* **Quái vật Cấp 1:**
    * `monster_lv1_idle.png`
    * `monster_lv1_hurt.png` (hiệu ứng bị đánh)
* **(Tương tự cho các cấp 2, 3...)**

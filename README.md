# Pixel Slayer

Pixel Slayer là một ứng dụng nhỏ gọn hiển thị ảnh GIF trên màn hình của bạn mỗi khi bạn nhấn một phím. Ứng dụng này được thiết kế để mang lại trải nghiệm tương tác thú vị và tùy chỉnh cao.

## Tính năng

*   **Hiển thị linh hoạt:** Có thể hiển thị một hoặc hai ảnh GIF cùng lúc.
*   **Lựa chọn ngẫu nhiên:** Ảnh GIF được chọn ngẫu nhiên từ các thư mục `assets/left` và `assets/right`.
*   **Hiệu ứng lật ảnh:** Ảnh GIF có thể được lật ngẫu nhiên theo chiều ngang để tạo ra các hiệu ứng đa dạng (ví dụ: đối xứng, giao chiến).
*   **Điều chỉnh kích thước thông minh:** Tất cả ảnh GIF được tự động điều chỉnh kích thước để phù hợp với kích thước mục tiêu (mặc định 200x200) trong khi vẫn giữ nguyên tỷ lệ khung hình, đảm bảo không bị méo.
*   **Hiệu ứng giao nhau:** Khi hiển thị hai ảnh GIF, chúng có thể giao nhau một khoảng nhất định (mặc định 100px) để tạo hiệu ứng "giao chiến" hoặc tương tác.
*   **Vị trí ngẫu nhiên:** Cửa sổ ứng dụng xuất hiện ở một vị trí ngẫu nhiên trên màn hình.
*   **Tự động ẩn:** Ảnh GIF sẽ tự động ẩn đi sau khi phát xong một chu kỳ.

## Cài đặt

1.  **Clone repository:**
    ```bash
    git clone https://github.com/haketienloc10/Pixel_Slayer.git
    cd Pixel_Slayer
    ```
2.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Chuẩn bị ảnh GIF:**
    *   Tạo hai thư mục con `left` và `right` bên trong thư mục `assets`.
    *   Đặt các tệp `.gif` của bạn vào `assets/left` và `assets/right`.

## Cách sử dụng

1.  **Chạy ứng dụng:**
    ```bash
    python key_gif_app.py
    ```
2.  **Nhấn phím:** Nhấn bất kỳ phím nào trên bàn phím để kích hoạt hiển thị ảnh GIF.

## Cấu hình

Bạn có thể tùy chỉnh hành vi của ứng dụng bằng cách chỉnh sửa biến `CONFIG` trong tệp `key_gif_app.py`:

```python
CONFIG = {
    "position": "random", # Vị trí xuất hiện: "random", "bottom-right", "bottom-left", "top-right", "top-left", "center"
    "target_gif_size": (200, 200), # Kích thước mục tiêu cho ảnh GIF (chiều rộng, chiều cao)
    "gif_overlap_px": 100, # Khoảng giao nhau giữa 2 ảnh GIF khi ở chế độ "double"
    "display_mode": "double", # Chế độ hiển thị: "single" hoặc "double"
}
```

---

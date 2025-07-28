# Hướng Dẫn Lập Trình Python

Khi viết hoặc chỉnh sửa mã nguồn Python, hãy tuân thủ nghiêm ngặt các quy tắc sau:

## 1. Tiêu Chuẩn & Định Dạng
- **PEP 8:** Toàn bộ mã nguồn phải tuân theo chuẩn [PEP 8](https://peps.python.org/pep-0008/). Sử dụng `black` hoặc `autopep8` để tự động định dạng nếu có thể.
- **Sắp xếp import:** Các thư viện import phải được sắp xếp theo thứ tự: thư viện chuẩn của Python, thư viện của bên thứ ba, và cuối cùng là code của dự án.

## 2. Type Hinting
- **Bắt buộc:** Tất cả các tham số của hàm và giá trị trả về phải có [Type Hint](https://docs.python.org/3/library/typing.html) (ví dụ: `def my_function(name: str) -> bool:`).
- Sử dụng các kiểu dữ liệu phức tạp từ module `typing` khi cần thiết (ví dụ: `List`, `Dict`, `Optional`).

## 3. Docstrings
- **Bắt buộc:** Tất cả các module, class, và hàm public phải có docstring.
- **Định dạng Google:** Sử dụng [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings). Docstring phải mô tả rõ chức năng, các tham số (`Args:`), và giá trị trả về (`Returns:`).

## 4. Xử Lý Lỗi (Exception Handling)
- **Cụ thể:** Luôn bắt các exception một cách cụ thể (ví dụ: `except FileNotFoundError:`), **tránh dùng `except:` hoặc `except Exception:` chung chung.**
- Cung cấp thông điệp lỗi rõ ràng hoặc ghi log khi một exception xảy ra.

## 5. Các Thói Quen Tốt
- **f-Strings:** Luôn sử dụng f-Strings để định dạng chuỗi (`f"Hello, {name}"`).
- **Pathlib:** Sử dụng module `pathlib` để xử lý các đường dẫn file thay vì `os.path`.
- **List Comprehensions:** Ưu tiên sử dụng list/dict comprehensions để tạo các cấu trúc dữ liệu một cách ngắn gọn và hiệu quả.

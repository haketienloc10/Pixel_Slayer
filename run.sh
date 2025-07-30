#!/bin/bash
# Lấy đường dẫn tuyệt đối đến thư mục của script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Đường dẫn đến thư mục môi trường ảo
VENV_DIR="$SCRIPT_DIR/.env"

# 1. Kiểm tra nếu môi trường ảo chưa tồn tại
if [ ! -d "$VENV_DIR" ]; then
    echo "Môi trường ảo chưa tồn tại. Đang tự động cài đặt..."
    
    # Tạo môi trường ảo mới bằng python3
    python3 -m venv "$VENV_DIR"
    
    # Kích hoạt pip từ môi trường ảo để cài đặt thư viện
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    
    echo "Cài đặt hoàn tất."
fi

LOCAL_LIBS_DIR="$SCRIPT_DIR/local_libs"
if [ ! -d "$LOCAL_LIBS_DIR" ]; then
    echo "Thư mục local_libs không tồn tại. Đang tạo mới..."
    mkdir -p "$LOCAL_LIBS_DIR"
    cd "$LOCAL_LIBS_DIR"
    # Tải xuống và giải nén các thư viện cần thiết
    apt-get download libxcb-cursor0
    dpkg -x libxcb-cursor0_*.deb ./
fi

# 2. Thiết lập đường dẫn thư viện hệ thống cục bộ (dành cho Linux)
export LD_LIBRARY_PATH=$LOCAL_LIBS_DIR/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# 3. Chạy ứng dụng bằng trình thông dịch Python trong môi trường ảo
echo "Khởi động ứng dụng..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/key_gif_app.py"
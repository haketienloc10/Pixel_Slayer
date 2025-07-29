#!/bin/bash
# Lấy đường dẫn tuyệt đối đến thư mục của script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Thiết lập đường dẫn thư viện và chạy ứng dụng Python
export LD_LIBRARY_PATH=$SCRIPT_DIR/lib/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
python $SCRIPT_DIR/key_gif_app.py
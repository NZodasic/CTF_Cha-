# Thử Thách CTF: The Forgotten Command

Thử thách CTF **"The Forgotten Command"** là một game giải đố điều tra hệ thống di sản (legacy system investigation) tương tác trực tiếp qua **giao diện dòng lệnh (Text Shell) trong tin nhắn riêng (Direct Message - DM) với Bot**. Người chơi sẽ đóng vai trò là một chuyên viên phân tích an ninh mạng được giao nhiệm vụ nhắn tin trực tiếp với một bot quản trị cổ xưa, gõ các lệnh như một terminal thực thụ để khám phá các thông tin bị ẩn giấu và lấy được cờ chiến thắng (**FLAG**).

---

## 💾 Tổng Quan 6 Tầng Giao Diện & Câu Đố

Thử thách được thiết kế cực kỳ logic với cơ chế bảo mật **Anti Brute-Force** (ngăn chặn đoán mò các lệnh nâng cao). Nếu người chơi chưa đạt đến cấp độ yêu cầu mà cố tình gõ các lệnh ẩn, hệ thống sẽ trả về lỗi kết nối mạng giả lập: `[ERROR] Connection timeout: Target node unreachable`.

Các tầng thử thách bao gồm:
1.  **Stage 1: `help`** - Gửi tin nhắn `help` trong DM để đọc chẩn đoán hệ thống. Giải mã Base64 ẩn ở footer để tìm lệnh tiếp theo: `dev_system_info`.
2.  **Stage 2: `dev_system_info`** - Phân tích log bộ nhớ chẩn đoán (Memory Dump) dạng Hex để tìm đường dẫn thư mục lưu trữ dự phòng: `secure_backup`.
3.  **Stage 3: `secure_backup`** - Kiểm tra danh mục file dự phòng và tải xuống `avatar_source.jpg`. Đọc ghi chú `admin_notes.txt` và `sys_config.bak`. Phân tích siêu dữ liệu **EXIF ImageDescription** của ảnh avatar để lấy khóa xác thực `portal_key: legacy_handshake_99`.
4.  **Stage 4: `legacy_portal_auth`** - Nhập khóa cổng để khởi động chế độ xác thực hai lớp (2FA). Giải bài toán logic về dãy số $T(n) = T(n-1) \times 3 - T(n-2)$ với $T(0)=2, T(1)=5$. Tính toán giá trị $T(7) = 1597$ làm mã OTP.
5.  **Stage 5: `archive_terminal`** - Đăng nhập bằng mã OTP. Mở khóa bảng điều khiển nén dữ liệu. Phát hiện API cục bộ đang chạy tại `http://127.0.0.1:8080/debug_console`. Sử dụng lệnh mô phỏng mạng nội bộ `curl` (SSRF Proxy) kết hợp với Header quản trị `X-Admin-Auth = admin_super_secret_token_2026` lấy được ở Stage 3 để rút trích khóa giải mã cuối cùng đã được mã hóa Base64: `Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY=`. Giải mã Base64 này để lấy cipher khôi phục thực tế: `command_restored_success_2026`.
6.  **Stage 6: `restore_system`** - Cung cấp cipher khôi phục hệ thống để mở khóa màn hình ăn mừng và nhận **FLAG**.

---

## 🛡️ Điểm Độc Đáo về Độ Khó & Giao Diện DM Shell

*   **Chặn Kênh Công Khai (Server-Side Block)**: Nếu người chơi gõ bất kỳ lệnh CTF nào (`help`, `curl`, v.v.) trong kênh chat công khai của máy chủ Discord, bot sẽ tự động chặn lại và trả về cảnh báo nguy cơ nghe lén: `[SECURITY ERR] Connection eavesdropping risk detected!`. Yêu cầu người chơi bắt buộc phải nhắn tin riêng (DM) với Bot. Điều này giúp ngăn chặn việc người chơi nhìn thấy đáp án của nhau.
*   **Không Có Autocomplete (Hacker Vibe)**: Vì người chơi tương tác qua DM văn bản thông thường và không sử dụng Slash Commands, Discord sẽ không hiển thị bất kỳ gợi ý lệnh nào. Người chơi phải thực sự điều tra, suy luận tên lệnh từ các manh mối và gõ chính xác tham số theo phong cách dòng lệnh Linux (hỗ trợ phân tích cú pháp nâng cao bằng `shlex` để xử lý các tham số có chứa dấu nháy kép như cấu hình JSON).

---

## 🛠️ Yêu Cầu Hệ Thống & Cài Đặt

### 1. Yêu cầu phần mềm
*   **Python 3.8** trở lên (Khuyên dùng Python 3.10+)
*   Các thư viện Python: `discord.py`, `Pillow`

### 2. Cài đặt môi trường & Cài đặt Dependencies

Mở Terminal tại thư mục dự án và thực hiện các bước sau:

```bash
# Tạo môi trường ảo cách ly (Virtual Environment)
python3 -m venv venv

# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 3. Khởi tạo Tài Nguyên (Tự động)
Nếu bạn chưa có file ảnh gốc chứa mã EXIF ẩn trong thư mục `assets/`, hãy chạy script tạo ảnh tự động:
```bash
python generate_assets.py
```
Script này sẽ vẽ một ảnh avatar phong cách neon cyberpunk cực đẹp mang tên `avatar_source.jpg` và nhúng sẵn thẻ EXIF cần thiết cho phần Stage 3.

---

## 🤖 Hướng Dẫn Cấu Hấu Trên Discord Developer Portal

Để chạy bot trên server Discord của bạn, hãy làm theo các bước chuẩn sau:

1.  Truy cập [Discord Developer Portal](https://discord.com/developers/applications).
2.  Nhấp vào **New Application**, đặt tên cho ứng dụng (ví dụ: `Core OS Legacy Bot`) và nhấn **Create**.
3.  Di chuyển tới tab **Bot** ở thanh menu bên trái:
    *   Nhấp vào **Add Bot** (nếu có).
    *   Tại mục **Privileged Gateway Intents**, bật 3 tùy chọn:
        *   **Presence Intent** (Bắt buộc để bot thay đổi trạng thái hoạt động).
        *   **Server Members Intent** (Bắt buộc để kiểm tra quyền admin).
        *   **Message Content Intent** (CỰC KỲ QUAN TRỌNG: Bắt buộc để đọc tin nhắn văn bản của người chơi trong DM).
    *   Nhấp vào **Reset Token** để lấy chuỗi **Token** bí mật của Bot. Sao chép và lưu trữ Token này (Không được chia sẻ công khai).
4.  Di chuyển tới tab **OAuth2** -> **URL Generator**:
    *   Tại phần **Scopes**, tích chọn: `bot`, `applications.commands`.
    *   Tại phần **Bot Permissions**, tích chọn:
        *   *General Permissions*: `Read Messages/View Channels`
        *   *Text Permissions*: `Send Messages`, `Embed Links`, `Attach Files`, `Use Slash Commands`.
    *   Sao chép liên kết được tạo ra ở dưới cùng của trang, dán vào trình duyệt để mời Bot tham gia server Discord test của bạn.

---

## 🚀 Khởi Chạy Bot

Trên máy chủ hosting hoặc máy local của bạn, xuất biến môi trường Token và khởi chạy bot:

**Trên Linux / macOS:**
```bash
export DISCORD_BOT_TOKEN="TOKEN_DISCORD_BOT_CUA_BAN_O_DAY"
python bot.py
```

**Trên Windows (PowerShell):**
```powershell
$env:DISCORD_BOT_TOKEN="TOKEN_DISCORD_BOT_CUA_BAN_O_DAY"
python bot.py
```

Khi chạy thành công, Terminal sẽ hiển thị:
```
Registering commands and syncing with Discord...
Logged in as Core OS Legacy Bot#1234 (ID: ...)
Successfully synced application commands.
```
Bot sẽ đổi trạng thái hiển thị sang chấm đỏ **Do Not Disturb** cùng dòng trạng thái hoạt động: `Watching for DMs | help`.

---

## 📦 Hướng Dẫn Deploy (Deployment Guide)

Để bot hoạt động liên tục 24/7 trên môi trường sản xuất (VPS Linux, Cloud VM như Railway, Render), bạn có thể lựa chọn chạy bằng Systemd Service hoặc Containerize bằng Docker.

### Cách 1: Chạy nền bằng Systemd Service (Khuyên dùng cho Ubuntu/Debian VPS)
1. Tạo file service cấu hình:
   ```bash
   sudo nano /etc/systemd/system/ctf-bot.service
   ```
2. Dán nội dung sau vào file (thay đổi đường dẫn và token cho đúng với hệ thống của bạn):
   ```ini
   [Unit]
   Description=CTF The Forgotten Command Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=raymond
   WorkingDirectory=/home/raymond/Desktop/MC-Resource/CTF_Cha
   ExecStart=/home/raymond/Desktop/MC-Resource/CTF_Cha/venv/bin/python bot.py
   Environment="DISCORD_BOT_TOKEN=TOKEN_BOT_CUA_BAN"
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
3. Nạp lại systemd, kích hoạt dịch vụ tự khởi động và chạy bot:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ctf-bot
   sudo systemctl start ctf-bot
   ```

### Cách 2: Deploy bằng Docker Container / Docker Compose
Bạn chỉ cần đưa mã nguồn lên GitHub và liên kết với Railway, Dockerfile và docker-compose.yml đã được cấu hình sẵn sẽ tự động thực hiện build và khởi chạy bot chỉ trong vài phút.

---

## ⚙️ Các Lệnh Hỗ Trợ Ban Tổ Chức (CTF Admin Tools)

Để Ban tổ chức hoặc người thiết kế giải đấu có thể dễ dàng quản lý, kiểm thử hoặc hỗ trợ người chơi, bot được trang bị các lệnh tiện ích:

### 1. Dành cho Người Chơi (Trong DMs)
*   **`status`** hoặc **`ctf_status`**: Xem tiến độ chơi hiện tại của bản thân.
*   **`reset`** hoặc **`ctf_reset`**: Xóa sạch tiến trình hiện tại để chơi lại thử thách từ Stage 0.

### 2. Lệnh Slash Command quản trị (Chỉ chạy trên Server bởi Admin)
*   **`/ctf_admin_set_stage user_mention:<@User> stage:<0-6>`**: *(Chỉ dành cho Administrator máy chủ)* Cài đặt ngay lập tức tiến trình của một người chơi cụ thể tới stage chỉ định. Rất hữu ích để Admin kiểm thử nhanh từng Stage mà không cần đi qua toàn bộ luồng.

---

## 📖 Lời Giải Chi Tiết Cho Ban Tổ Chức (Official Writeup)

### Bước 1: Khởi động hệ thống
Người chơi mở tin nhắn riêng (DM) với bot và gõ lệnh `help`. Bot trả lời bằng một Embed thông báo hệ thống đã bị vô hiệu hóa. Ở chân trang (Footer), người chơi tìm thấy chuỗi: `System ID: ZGV2X3N5c3RlbV9pbmZv`.
*   **Giải quyết**: Giải mã Base64 chuỗi `ZGV2X3N5c3RlbV9pbmZv` thu được lệnh tiếp theo: `dev_system_info`.

### Bước 2: Đọc chẩn đoán nhà phát triển
Người chơi gõ lệnh `dev_system_info` trong DM. Bot trả về log chẩn đoán lỗi. Trong đó có vùng dump bộ nhớ Hex: `42 61 63 6b 75 70 3a 20 2f 73 65 63 75 72 65 5f 62 61 63 6b 75 70`.
*   **Giải quyết**: Dịch chuỗi Hex trên sang ký tự Plaintext (bỏ các ký tự khoảng trắng) để thu được `Backup: /secure_backup`. Lệnh cần chạy tiếp theo trong DM là `secure_backup`.

### Bước 3: Đọc phân vùng sao lưu
Người chơi gõ lệnh `secure_backup` trong DM. Bot hiển thị danh sách file sao lưu.
1.  Người chơi chạy `secure_backup sys_config.bak` để tìm thấy Admin Header Token: `admin_super_secret_token_2026`.
2.  Người chơi chạy `secure_backup admin_notes.txt` để đọc ghi chú hướng dẫn lấy khóa cổng kết nối cổ xưa được nhúng trong metadata ảnh avatar `avatar_source.jpg`.
3.  Người chơi chạy `secure_backup avatar_source.jpg`. Bot sẽ gửi đính kèm tệp ảnh gốc. Người chơi tải ảnh về máy.
*   **Giải quyết**: Sử dụng các công cụ phân tích siêu dữ liệu (EXIF) để trích xuất thẻ metadata `ImageDescription` của ảnh. Người chơi sẽ tìm thấy chuỗi: `portal_key: legacy_handshake_99`.

### Bước 4: Vượt cổng kiểm soát di sản
Người chơi gõ lệnh `legacy_portal_auth legacy_handshake_99` trong DM. Xác thực thành công. Bot hiển thị yêu cầu tính toán OTP cho Stage tiếp theo.
*   **Toán học**:
    *   $T(n) = T(n-1) \times 3 - T(n-2)$ với $T(0)=2, T(1)=5$.
    *   $T(2) = 5 \times 3 - 2 = 13$
    *   $T(3) = 13 \times 3 - 5 = 34$
    *   $T(4) = 34 \times 3 - 13 = 89$
    *   $T(5) = 89 \times 3 - 34 = 233$
    *   $T(6) = 233 \times 3 - 89 = 610$
    *   $T(7) = 610 \times 3 - 233 = 1597$
*   **Giải quyết**: OTP cần điền là `1597`.

### Bước 5: Mở khóa lưu trữ & Mô phỏng SSRF (Thêm độ khó)
Người chơi gõ lệnh `archive_terminal 1597` trong DM. Khởi động thành công console lưu trữ. Bot hướng dẫn người chơi thực hiện kiểm tra dịch vụ cục bộ qua API `http://127.0.0.1:8080/debug_console` để lấy cipher giải mã cuối cùng.
Người chơi được trang bị lệnh `curl <url> <json_headers>`.
1.  Nếu chạy thường: `curl http://127.0.0.1:8080/debug_console` -> Trả về lỗi `401 Unauthorized` yêu cầu header quản trị `X-Admin-Auth`.
2.  Người chơi sử dụng Token tìm được ở `sys_config.bak` tại Stage 3 và định dạng lại thành chuỗi JSON:
    `curl http://127.0.0.1:8080/debug_console '{"X-Admin-Auth": "admin_super_secret_token_2026"}'`
3.  API nội bộ của bot sẽ phản hồi thành công và trả về mã cipher đã mã hóa Base64:
    `System Flag Decryption Key (Base64 Encoded): Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY=`
*   **Giải quyết**: Người chơi thực hiện giải mã Base64 chuỗi `Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY=` để thu được cipher thực sự: `command_restored_success_2026`.

### Bước 6: Khôi phục hệ thống và lấy FLAG
Người chơi gõ lệnh `restore_system command_restored_success_2026` trong DM.
*   **Kết quả**: Hệ thống thông báo khôi phục hoàn chỉnh, hiển thị màn hình chúc mừng Hacker neon xanh rực rỡ và trao **FLAG**:
    `flag{f0rg0tt3n_c0mm4nd_syst3m_unl0ck3d_9a2f}`

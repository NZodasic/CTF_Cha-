import os
import time
import shlex
import discord
from discord import app_commands
from discord.ext import commands
import ctf_engine

# Initialize the CTF database
ctf_engine.init_db()

# Bot Setup with necessary intents for DMs and server messages
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

class CTFBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        # We retain slash commands for admin utilities only
        print("Registering commands and syncing with Discord...")

bot = CTFBot()

# -------------------------------------------------------------
# RETRO DESIGN EMBED TEMPLATE HELPERS
# -------------------------------------------------------------

COLOR_CYAN = discord.Color.from_rgb(0, 255, 200)
COLOR_PINK = discord.Color.from_rgb(255, 0, 128)
COLOR_GREEN = discord.Color.from_rgb(0, 255, 100)
COLOR_WARNING = discord.Color.from_rgb(255, 165, 0)
COLOR_ERROR = discord.Color.from_rgb(220, 20, 60)

def create_terminal_embed(title: str, description: str, color=COLOR_CYAN) -> discord.Embed:
    """Helper to generate premium, hacker-style embedded layouts."""
    prefix = "[SYSTEM]"
    if color == COLOR_PINK:
        prefix = "[ALERT]"
    elif color == COLOR_ERROR:
        prefix = "[ERROR]"
    elif color == COLOR_WARNING:
        prefix = "[WARNING]"
    elif color == COLOR_GREEN:
        prefix = "[SUCCESS]"
        
    embed = discord.Embed(
        title=f"📟 {prefix} :: {title}",
        description=description,
        color=color
    )
    embed.set_footer(text="CORE OS v0.9.7-LTS // CTF Terminal Protocol")
    return embed

# -------------------------------------------------------------
# DISCORD BOT EVENTS
# -------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    # Set high-tech custom activity
    activity = discord.Activity(
        name="for DMs | help",
        type=discord.ActivityType.watching
    )
    await bot.change_presence(status=discord.Status.dnd, activity=activity)
    
    # Sync slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} application commands.")
    except Exception as e:
        print(f"Error syncing application commands: {e}")

# -------------------------------------------------------------
# CORE INTERACTION ON_MESSAGE ROUTING (DM-ONLY TEXT SHELL)
# -------------------------------------------------------------

user_cooldowns = {}

@bot.event
async def on_message(message: discord.Message):
    # Avoid infinite loop
    if message.author.bot:
        return

    # Normalized command list
    ctf_commands = [
        "help", "dev_system_info", "secure_backup", 
        "legacy_portal_auth", "archive_terminal", "curl", 
        "restore_system", "ctf_status", "status", "ctf_reset", "reset"
    ]

    # CASE 1: Message sent in a public Server (Guild) Channel
    if message.guild is not None:
        first_word = message.content.strip().split()[0].lower() if message.content.strip() else ""
        cmd_clean = first_word.lstrip("/") # Remove potential leading slashes
        
        # If player attempts to run a game command in a public channel, warn them and block
        if cmd_clean in ctf_commands:
            error_embed = create_terminal_embed(
                title="Secure Channel Required",
                description=(
                    "```\n"
                    "[SECURITY ERR] Connection eavesdropping risk detected!\n"
                    "Secure terminal session can ONLY be established over direct private transmission.\n"
                    "```\n"
                    "⚠️ **Vui lòng nhắn tin trực tiếp (DM) cho tôi để bắt đầu phiên làm việc an toàn!**"
                ),
                color=COLOR_ERROR
            )
            await message.channel.send(embed=error_embed)
            return
            
        # Process other standard messages/prefix commands
        await bot.process_commands(message)
        return

    # CASE 2: Message sent in Direct Messages (DM) -> Interactive Text Shell
    content = message.content.strip()
    if not content:
        return

    # Parse arguments using shell splitting rules (supports nested quotes/JSON payloads!)
    try:
        args = shlex.split(content)
    except Exception:
        # Fallback to standard whitespace splitting if mismatched quotes occur
        args = content.split()

    if not args:
        return

    # Normalize command word by converting to lowercase and stripping leading slashes
    cmd = args[0].lower().lstrip("/")
    user_id = message.author.id
    current_stage = ctf_engine.get_user_stage(user_id)

    # Rate limit cooldown in DMs to prevent brute-forcing/spam
    current_time = time.time()
    if user_id in user_cooldowns:
        elapsed = current_time - user_cooldowns[user_id]
        if elapsed < 1.5:  # 1.5 seconds cooldown
            rate_embed = create_terminal_embed(
                title="Rate Limit Exceeded",
                description="```\n[WARNING] Request rate limit exceeded.\nAnti-spam firewall triggered.\nPlease wait 1.5 seconds before running another command.\n```",
                color=COLOR_WARNING
            )
            await message.channel.send(embed=rate_embed)
            return
            
    user_cooldowns[user_id] = current_time

    # 1. HELP COMMAND (Stage 0+)
    if cmd == "help":
        if current_stage == 0:
            ctf_engine.set_user_stage(user_id, 1)
            
        help_desc = (
            "Chào mừng bạn đến với Cổng chẩn đoán hệ thống cổ xưa.\n"
            "Tất cả các dịch vụ đã bị vô hiệu hóa bởi ban quản trị mạng.\n\n"
            "```\n"
            "DỊCH VỤ HIỆN TẠI:\n"
            "- MODULE: TRỢ GIÚP CHẨN ĐOÁN (ONLINE)\n"
            "- MODULE: QUẢN TRỊ CORE (OFFLINE)\n"
            "- MODULE: BACKUP CƠ SỞ DỮ LIỆU (OFFLINE)\n"
            "- MODULE: CỔNG THÔNG TIN XÁC THỰC (OFFLINE)\n"
            "```\n"
            "Nếu bạn là quản trị viên hệ thống và cần khôi phục dịch vụ, vui lòng liên hệ với bộ phận an ninh mạng."
        )
        embed = create_terminal_embed("Diagnostic Panel", help_desc, COLOR_CYAN)
        embed.set_footer(text="System ID: ZGV2X3N5c3RlbV9pbmZv // CORE OS v0.9.7-LTS") # Base64 of 'dev_system_info'
        await message.channel.send(embed=embed)

    # 2. DEV SYSTEM INFO (Stage 1+)
    elif cmd == "dev_system_info":
        if current_stage < 1:
            await send_stage_error(message.channel)
            return
            
        if current_stage == 1:
            ctf_engine.set_user_stage(user_id, 2)
            
        dev_desc = (
            "**[CẢNH BÁO]** Truy cập bảng điều khiển nhà phát triển ở chế độ chỉ đọc.\n\n"
            "```ini\n"
            "[System Status]\n"
            "Core Status: CRITICAL\n"
            "Uptime: 247 days, 11 hours\n"
            "Local IP: 127.0.0.1\n\n"
            "[Internal Messages & System Dumps]\n"
            "Dump Address 0x00FF8E:\n"
            "42 61 63 6b 75 70 3a 20 2f 73 65 63 75 72 65 5f 62 61 63 6b 75 70\n\n"
            "--- End of Dump ---\n"
            "```\n"
            "Gợi ý hệ thống: Khôi phục thiết lập bằng cách tìm phân vùng backup."
        )
        embed = create_terminal_embed("Developer Core Information", dev_desc, COLOR_WARNING)
        await message.channel.send(embed=embed)

    # 3. SECURE BACKUP CATALOG & INSPECT (Stage 2+)
    elif cmd == "secure_backup":
        if current_stage < 2:
            await send_stage_error(message.channel)
            return
            
        if current_stage == 2:
            ctf_engine.set_user_stage(user_id, 3)

        # Parse filename to inspect
        filename = None
        if len(args) > 1:
            if args[1].lower() == "inspect" and len(args) > 2:
                filename = args[2]
            elif args[1].lower().startswith("inspect:"):
                parts = args[1].split(":", 1)
                filename = parts[1] if len(parts) > 1 else None
            else:
                filename = args[1]

        if filename is None:
            backup_desc = (
                "Kết nối phân vùng lưu trữ dự phòng thành công.\n"
                "Danh mục các file sao lưu phát hiện được trong `/backups/sys_core/`:\n\n"
                "```\n"
                "FILE NAME                      SIZE        TYPE\n"
                "--------------------------------------------------\n"
                "sys_config.bak                 412 B       Plaintext Config\n"
                "admin_notes.txt                625 B       Plaintext Note\n"
                "user_database.db.encrypted     1.2 KB      Encrypted Database\n"
                "avatar_source.jpg              82.4 KB     JPEG Binary Image\n"
                "```\n"
                "Sử dụng tham số `inspect` hoặc gõ trực tiếp tên file để xem. Ví dụ: `secure_backup admin_notes.txt`"
            )
            embed = create_terminal_embed("Backup Server Filesystem", backup_desc, COLOR_CYAN)
            await message.channel.send(embed=embed)
        else:
            result = ctf_engine.inspect_mock_file(filename)
            
            if result["status"] == "text":
                file_desc = (
                    f"Đang hiển thị nội dung file: `{filename}`\n\n"
                    f"```\n"
                    f"{result['content']}"
                    f"```"
                )
                embed = create_terminal_embed(f"Inspect File: {filename}", file_desc, COLOR_CYAN)
                await message.channel.send(embed=embed)
                
            elif result["status"] == "file":
                embed = create_terminal_embed(
                    title=f"Inspect File: {filename}",
                    description="Bạn đã trích xuất thành công avatar hệ thống nguyên bản. Hãy kiểm tra siêu dữ liệu EXIF của file ảnh này!",
                    color=COLOR_CYAN
                )
                file_path = result["path"]
                if os.path.exists(file_path):
                    file_to_send = discord.File(file_path, filename=os.path.basename(file_path))
                    await message.channel.send(embed=embed, file=file_to_send)
                else:
                    error_embed = create_terminal_embed(
                        title="Inspection Error",
                        description=f"[ERROR] Source image '{file_path}' is missing on target storage.",
                        color=COLOR_ERROR
                    )
                    await message.channel.send(embed=error_embed)
            else:
                error_embed = create_terminal_embed("Inspection Error", f"```\n{result['message']}\n```", COLOR_ERROR)
                await message.channel.send(embed=error_embed)

    # 4. LEGACY PORTAL AUTHENTICATION (Stage 3+)
    elif cmd == "legacy_portal_auth":
        if current_stage < 3:
            await send_stage_error(message.channel)
            return

        key = args[1] if len(args) > 1 else ""
        if key.strip() == "legacy_handshake_99":
            if current_stage == 3:
                ctf_engine.set_user_stage(user_id, 4)
                
            portal_desc = (
                "🔓 **[XÁC THỰC THÀNH CÔNG]** Chào mừng Quản trị viên Di sản.\n\n"
                "Hệ thống yêu cầu xác thực hai lớp (2FA) bằng cách sử dụng Mã OTP Động.\n"
                "Tính toán giá trị toán học của chuỗi sau để sinh khóa OTP hoàn chỉnh:\n\n"
                "```\n"
                "ĐỊNH NGHĨA DÃY SỐ:\n"
                "T(n) = T(n-1) * 3 - T(n-2) với n >= 2\n"
                "Giá trị cơ sở: T(0) = 2, T(1) = 5\n\n"
                "BÀI TOÁN:\n"
                "Tính giá trị T(7) để làm khóa OTP cho hệ thống lưu trữ tiếp theo.\n"
                "```\n"
                "Lệnh hệ thống lưu trữ tiếp theo: `archive_terminal`"
            )
            embed = create_terminal_embed("Legacy Access Portal", portal_desc, COLOR_GREEN)
            await message.channel.send(embed=embed)
        else:
            error_embed = create_terminal_embed(
                title="Authentication Failed",
                description="```\n[ERROR] Key Signature Mismatch.\nAccess Blocked: Cryptographic signature validation failed.\n```",
                color=COLOR_ERROR
            )
            await message.channel.send(embed=error_embed)

    # 5. ARCHIVE TERMINAL 2FA (Stage 4+)
    elif cmd == "archive_terminal":
        if current_stage < 4:
            await send_stage_error(message.channel)
            return

        otp_str = args[1] if len(args) > 1 else ""
        try:
            otp = int(otp_str)
        except ValueError:
            otp = 0
            
        if otp == 1597:
            if current_stage == 4:
                ctf_engine.set_user_stage(user_id, 5)
                
            archive_desc = (
                "🔑 **[MỞ KHÓA THÀNH CÔNG]** Kết nối đến Archive Server hoàn tất.\n\n"
                "Tìm thấy 1 bản ghi nén được lưu trữ: `[DELETED_PROJECT_FALCON]`\n"
                "Yêu cầu giải mã: Nhập cipher khóa khôi phục hệ thống.\n\n"
                "```\n"
                "Ghi chú khôi phục:\n"
                "- Khóa giải mã cipher được phân phối thông qua API kiểm tra dịch vụ cục bộ.\n"
                "- Endpoint chẩn đoán: http://127.0.0.1:8080/debug_console\n"
                "- Bot hiện có cổng mô phỏng lệnh `curl` mạng nội bộ.\n"
                "- Đọc tài liệu backup để biết cách thiết lập quyền quản trị khi gọi API.\n"
                "```\n"
                "Lệnh khôi phục cuối cùng: `restore_system cipher:<key>`"
            )
            embed = create_terminal_embed("Project Archive Console", archive_desc, COLOR_GREEN)
            await message.channel.send(embed=embed)
        else:
            error_embed = create_terminal_embed(
                title="Access Denied",
                description="```\n[ERROR] Invalid 2FA OTP Token.\nAccess Denied: Dynamic token validation code is incorrect.\n```",
                color=COLOR_ERROR
            )
            await message.channel.send(embed=error_embed)

    # 6. INTERNAL CURL SIMULATOR (Stage 5+)
    elif cmd == "curl":
        if current_stage < 5:
            await send_stage_error(message.channel)
            return

        url = args[1] if len(args) > 1 else ""
        headers = args[2] if len(args) > 2 else None
        
        # Execute SSRF request
        result = ctf_engine.mock_curl_request(url, headers)
        
        curl_desc = (
            f"**Executing local network request...**\n"
            f"Target: `{url}`\n"
            f"Headers: `{headers if headers else 'None'}`\n\n"
            f"```\n"
            f"{result}\n"
            f"```"
        )
        embed = create_terminal_embed("Internal Curl Simulator", curl_desc, COLOR_CYAN)
        await message.channel.send(embed=embed)

    # 7. SYSTEM RESTORATION FLAG DECRYPT (Stage 5+)
    elif cmd == "restore_system":
        if current_stage < 5:
            await send_stage_error(message.channel)
            return

        cipher = args[1] if len(args) > 1 else ""
        # Clean potential parameter prefixes like 'cipher:'
        if cipher.lower().startswith("cipher:"):
            cipher = cipher.split(":", 1)[1]
            
        if cipher.strip() == "command_restored_success_2026":
            if current_stage == 5:
                ctf_engine.set_user_stage(user_id, 6)
                
            success_desc = (
                "🎉 **[HỆ THỐNG KHÔI PHỤC THÀNH CÔNG]** 🎉\n\n"
                "Chúc mừng bạn! Tất cả các dịch vụ di sản đã được khởi chạy thành công.\n"
                "Dưới đây là phần thưởng cho nỗ lực điều tra xuất sắc của bạn:\n\n"
                "```\n"
                "======================================================\n"
                "FLAG: flag{f0rg0tt3n_c0mm4nd_syst3m_unl0ck3d_9a2f}\n"
                "======================================================\n"
                "```\n"
                "Hệ thống vận hành an toàn. Chúc mừng Operator!"
            )
            embed = create_terminal_embed("System Recovery Successful", success_desc, COLOR_GREEN)
            await message.channel.send(embed=embed)
        else:
            error_embed = create_terminal_embed(
                title="System Restore Failure",
                description="```\n[ERROR] Integrity Cipher Signature Mismatch.\nCore files decrypted failed: invalid initialization vector.\n```",
                color=COLOR_ERROR
            )
            await message.channel.send(embed=error_embed)

    # 8. GENERAL SHELL UTILITIES
    elif cmd in ["status", "ctf_status"]:
        stages_info = [
            "Stage 0: Chưa bắt đầu (Gõ `help` để kích hoạt)",
            "Stage 1: Diagnostic Panel `help` (Đã tìm ra `dev_system_info`)",
            "Stage 2: Developer Core Info `dev_system_info` (Đã tìm ra `secure_backup`)",
            "Stage 3: Backup Catalog `secure_backup` (Đang tìm khóa avatar cho `legacy_portal_auth`)",
            "Stage 4: Access Portal 2FA `legacy_portal_auth` (Đang tính toán OTP cho `archive_terminal`)",
            "Stage 5: Archive Restored `archive_terminal` (Đang tìm cipher giải mã `restore_system` qua SSRF `curl`)",
            "Stage 6: System Restored (Thành công! Lấy được FLAG)"
        ]
        current_status = stages_info[current_stage] if current_stage < len(stages_info) else "Hoàn thành thử thách!"
        
        desc = (
            f"**Tài khoản:** {message.author.mention}\n"
            f"**Tiến độ hiện tại:** `{current_status}`\n\n"
            "Nếu bạn muốn xóa sạch lịch sử chơi để chơi lại từ đầu, hãy gõ lệnh: `reset`"
        )
        embed = create_terminal_embed("CTF Challenger Progress", desc, COLOR_CYAN)
        await message.channel.send(embed=embed)
        
    elif cmd in ["reset", "ctf_reset"]:
        ctf_engine.reset_user(user_id)
        embed = create_terminal_embed(
            title="Session Reset",
            description="Đã reset tiến độ chơi của bạn về **Stage 0**. Bạn có thể bắt đầu lại bằng lệnh `help`.",
            color=COLOR_WARNING
        )
        await message.channel.send(embed=embed)
        
    else:
        # Unknown Command fallback
        unknown_embed = create_terminal_embed(
            title="Command Unrecognized",
            description=(
                f"```\n"
                f"[ERROR] Shell command '{cmd}' not found.\n"
                f"Type 'help' to view available system diagnostics.\n"
                f"```"
            ),
            color=COLOR_ERROR
        )
        await message.channel.send(embed=unknown_embed)

# -------------------------------------------------------------
# STAGE CONTROL HELPERS
# -------------------------------------------------------------

async def send_stage_error(channel):
    error_embed = create_terminal_embed(
        title="Connection Fail",
        description="```\n[ERROR] Connection timeout: Target node unreachable.\nRequired network handshake not established.\n```",
        color=COLOR_ERROR
    )
    await channel.send(embed=error_embed)

# -------------------------------------------------------------
# CTF ADMIN CONFIGURATION & OVERRIDE COMMANDS (SERVER ONLY)
# -------------------------------------------------------------

@bot.tree.command(name="ctf_admin_set_stage", description="[ADMIN ONLY] Cài đặt nhanh tiến độ của một người dùng.")
@app_commands.describe(
    user_mention="Mention của người dùng cần đổi (ví dụ: @Username)",
    stage="Stage mong muốn (0 - 6)"
)
async def ctf_admin_set_stage(interaction: discord.Interaction, user_mention: discord.Member, stage: int):
    # Check if this is an admin / moderator
    if not interaction.user.guild_permissions.administrator:
        error_embed = create_terminal_embed(
            title="Permission Denied",
            description="Chỉ quản trị viên máy chủ (Administrator) mới có quyền sử dụng lệnh này.",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return
        
    if stage < 0 or stage > 6:
        error_embed = create_terminal_embed(
            title="Value Error",
            description="Mức stage hợp lệ phải nằm trong khoảng từ `0` đến `6`.",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return
        
    ctf_engine.set_user_stage(user_mention.id, stage)
    
    embed = create_terminal_embed(
        title="Admin Override System",
        description=f"Đã cập nhật tiến độ của người chơi {user_mention.mention} thành **Stage {stage}**.",
        color=COLOR_GREEN
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -------------------------------------------------------------
# BOT ENTRYPOINT
# -------------------------------------------------------------

if __name__ == "__main__":
    # Fetch token from environment variable or print warnings
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("\n" + "="*80)
        print(" [WARNING] KHÔNG TÌM THẤY BIẾN MÔI TRƯỜNG 'DISCORD_BOT_TOKEN'!")
        print(" Vui lòng khởi động bot bằng lệnh:")
        print("   export DISCORD_BOT_TOKEN=\"token_cua_ban\"")
        print("   python bot.py")
        print("="*80 + "\n")
    else:
        bot.run(token)

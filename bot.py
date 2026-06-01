import os
import discord
from discord import app_commands
from discord.ext import commands
import ctf_engine

# Initialize the CTF database
ctf_engine.init_db()

# Bot Setup
# Note: You can customize intents here. Default + Message content is usually enough.
intents = discord.Intents.default()
intents.message_content = True

class CTFBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        
    async def setup_hook(self):
        # Synchronize slash commands globally on startup
        print("Registering commands and syncing with Discord...")
        # In a real environment, you might want to call tree.sync() manually or on demand.

bot = CTFBot()

# -------------------------------------------------------------
# RETRO DESIGN EMBED TEMPLATE HELPERS
# -------------------------------------------------------------

COLOR_CYAN = discord.Color.from_rgb(0, 255, 200)
COLOR_PINK = discord.Color.from_rgb(255, 0, 128)
COLOR_GREEN = discord.Color.from_rgb(0, 255, 100)
COLOR_WARNING = discord.Color.from_rgb(255, 165, 0)
COLOR_ERROR = discord.Color.from_rgb(220, 20, 60)

def create_terminal_embed(title: str, description: str, color=COLOR_CYAN, error_type=None) -> discord.Embed:
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
# COMMAND PREREQUISITE CHECK (ANTI BRUTE-FORCE)
# -------------------------------------------------------------

def check_stage_requirement(required_stage: int):
    """
    Returns a check function to verify if user has reached the required stage.
    If not, returns a simulated connection network timeout.
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        user_id = interaction.user.id
        current_stage = ctf_engine.get_user_stage(user_id)
        
        if current_stage >= required_stage:
            return True
            
        # Simulate network failure to prevent brute forcing
        error_embed = create_terminal_embed(
            title="Connection Fail",
            description="```\n[ERROR] Connection timeout: Target node unreachable.\nRequired network handshake not established.\n```",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return False
        
    return app_commands.check(predicate)

# -------------------------------------------------------------
# DISCORD BOT EVENTS
# -------------------------------------------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    # Set high-tech custom activity
    activity = discord.Activity(
        name="for administration /help",
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
# CTF CHALLENGE COMMANDS
# -------------------------------------------------------------

@bot.tree.command(name="help", description="Hiển thị menu trợ giúp và chuẩn đoán bot.")
async def ctf_help(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    # Initialize state to 1 if starting for the first time
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
    
    # Secret encoded link in footer to prevent simple visual discovery
    # Base64 for '/dev_system_info' is 'L2Rldl9zeXN0ZW1faW5mbw=='
    embed.set_footer(text="System ID: L2Rldl9zeXN0ZW1faW5mbw== // CORE OS v0.9.7-LTS")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="dev_system_info", description="[BỊ KHÓA] Truy cập trang thông tin cấu hình nhà phát triển.")
@check_stage_requirement(1)
async def ctf_dev_info(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    # Advance to stage 2 if currently at 1
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
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="secure_backup", description="[BỊ KHÓA] Kiểm tra và tải xuống các bản sao lưu cấu hình.")
@app_commands.describe(inspect="Tên file bạn muốn kiểm tra trong bộ sao lưu (Không bắt buộc)")
@check_stage_requirement(2)
async def ctf_backup(interaction: discord.Interaction, inspect: str = None):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    # Advance to stage 3 if currently at 2
    if current_stage == 2:
        ctf_engine.set_user_stage(user_id, 3)
        
    if inspect is None:
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
            "Sử dụng tham số `inspect` để xem nội dung file. Ví dụ: `/secure_backup inspect:admin_notes.txt`"
        )
        embed = create_terminal_embed("Backup Server Filesystem", backup_desc, COLOR_CYAN)
        await interaction.response.send_message(embed=embed)
    else:
        result = ctf_engine.inspect_mock_file(inspect)
        
        if result["status"] == "text":
            file_desc = (
                f"Đang hiển thị nội dung file: `{inspect}`\n\n"
                f"```\n"
                f"{result['content']}"
                f"```"
            )
            embed = create_terminal_embed(f"Inspect File: {inspect}", file_desc, COLOR_CYAN)
            await interaction.response.send_message(embed=embed)
            
        elif result["status"] == "file":
            embed = create_terminal_embed(
                title=f"Inspect File: {inspect}",
                description="Bạn đã trích xuất thành công avatar hệ thống nguyên bản. Hãy kiểm tra siêu dữ liệu EXIF của file ảnh này!",
                color=COLOR_CYAN
            )
            file_path = result["path"]
            if os.path.exists(file_path):
                file_to_send = discord.File(file_path, filename=os.path.basename(file_path))
                await interaction.response.send_message(embed=embed, file=file_to_send)
            else:
                error_embed = create_terminal_embed(
                    title="Inspection Error",
                    description=f"[ERROR] Source image '{file_path}' is missing on target storage. Contact the challenge host.",
                    color=COLOR_ERROR
                )
                await interaction.response.send_message(embed=error_embed)
        else:
            error_embed = create_terminal_embed("Inspection Error", f"```\n{result['message']}\n```", COLOR_ERROR)
            await interaction.response.send_message(embed=error_embed)


@bot.tree.command(name="legacy_portal_auth", description="[BỊ KHÓA] Xác thực với Cổng kiểm soát di sản.")
@app_commands.describe(key="Nhập mã khóa xác thực bảo mật")
@check_stage_requirement(3)
async def ctf_portal(interaction: discord.Interaction, key: str):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    if key.strip() == "legacy_handshake_99":
        # Advance to stage 4 if currently at 3
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
            "Lệnh hệ thống lưu trữ tiếp theo: `/archive_terminal`"
        )
        embed = create_terminal_embed("Legacy Access Portal", portal_desc, COLOR_GREEN)
        await interaction.response.send_message(embed=embed)
    else:
        error_embed = create_terminal_embed(
            title="Authentication Failed",
            description="```\n[ERROR] Key Signature Mismatch.\nAccess Blocked: Cryptographic signature validation failed.\n```",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed)


@bot.tree.command(name="archive_terminal", description="[BỊ KHÓA] Truy cập trung tâm lưu trữ dự án mật.")
@app_commands.describe(otp="Nhập mã số OTP 2FA")
@check_stage_requirement(4)
async def ctf_archive(interaction: discord.Interaction, otp: int):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    if otp == 1597:
        # Advance to stage 5 if currently at 4
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
            "- Bot hiện có cổng mô phỏng lệnh `/curl` mạng nội bộ.\n"
            "- Đọc tài liệu backup để biết cách thiết lập quyền quản trị khi gọi API.\n"
            "```\n"
            "Lệnh khôi phục cuối cùng: `/restore_system cipher:<key>`"
        )
        embed = create_terminal_embed("Project Archive Console", archive_desc, COLOR_GREEN)
        await interaction.response.send_message(embed=embed)
    else:
        error_embed = create_terminal_embed(
            title="Access Denied",
            description="```\n[ERROR] Invalid 2FA OTP Token.\nAccess Denied: Dynamic token validation code is incorrect.\n```",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed)


@bot.tree.command(name="curl", description="[BỊ KHÓA] Mô phỏng một yêu cầu mạng nội bộ bằng curl.")
@app_commands.describe(
    url="URL mục tiêu (ví dụ: http://127.0.0.1:8080/)",
    headers="Chuỗi JSON đại diện cho các HTTP Headers (ví dụ: {\"X-Admin-Auth\": \"token\"})"
)
@check_stage_requirement(5)
async def ctf_curl(interaction: discord.Interaction, url: str, headers: str = None):
    # Perform mock curl request
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
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="restore_system", description="[BỊ KHÓA] Khôi phục toàn bộ lõi dữ liệu hệ thống.")
@app_commands.describe(cipher="Nhập mã cipher giải mã cuối cùng thu thập được")
@check_stage_requirement(5)
async def ctf_restore(interaction: discord.Interaction, cipher: str):
    user_id = interaction.user.id
    current_stage = ctf_engine.get_user_stage(user_id)
    
    if cipher.strip() == "command_restored_success_2026":
        # System restored successfully
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
        await interaction.response.send_message(embed=embed)
    else:
        error_embed = create_terminal_embed(
            title="System Restore Failure",
            description="```\n[ERROR] Integrity Cipher Signature Mismatch.\nCore files decrypted failed: invalid initialization vector.\n```",
            color=COLOR_ERROR
        )
        await interaction.response.send_message(embed=error_embed)

# -------------------------------------------------------------
# PLAYER CONVENIENCE & HELP UTILITIES
# -------------------------------------------------------------

@bot.tree.command(name="ctf_status", description="Xem tiến độ chơi thử thách CTF hiện tại của bạn.")
async def ctf_status(interaction: discord.Interaction):
    user_id = interaction.user.id
    stage = ctf_engine.get_user_stage(user_id)
    
    stages_info = [
        "Stage 0: Chưa bắt đầu (Chạy `/help` để kích hoạt)",
        "Stage 1: Diagnostic Panel `/help` (Đã tìm ra `/dev_system_info`)",
        "Stage 2: Developer Core Info `/dev_system_info` (Đã tìm ra `/secure_backup`)",
        "Stage 3: Backup Catalog `/secure_backup` (Đang tìm khóa avatar của `/legacy_portal_auth`)",
        "Stage 4: Access Portal 2FA `/legacy_portal_auth` (Đang tính toán OTP `/archive_terminal`)",
        "Stage 5: Archive Restored `/archive_terminal` (Đang tìm cipher `/restore_system` qua SSRF `/curl`)",
        "Stage 6: System Restored (Thành công! Lấy được FLAG)"
    ]
    
    current_status = stages_info[stage] if stage < len(stages_info) else "Hoàn thành thử thách!"
    
    desc = (
        f"**Tài khoản:** {interaction.user.mention}\n"
        f"**Tiến độ hiện tại:** `{current_status}`\n\n"
        "Nếu bạn muốn xóa sạch lịch sử chơi để chơi lại từ đầu, hãy chạy lệnh: `/ctf_reset`"
    )
    
    embed = create_terminal_embed("CTF Challenger Progress", desc, COLOR_CYAN)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ctf_reset", description="Xóa tiến trình và chơi lại thử thách từ đầu.")
async def ctf_reset(interaction: discord.Interaction):
    user_id = interaction.user.id
    ctf_engine.reset_user(user_id)
    
    embed = create_terminal_embed(
        title="Session Reset",
        description="Đã reset tiến độ chơi của bạn về **Stage 0**. Bạn có thể bắt đầu lại bằng lệnh `/help`.",
        color=COLOR_WARNING
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# -------------------------------------------------------------
# CTF ADMIN CONFIGURATION & OVERRIDE COMMANDS
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

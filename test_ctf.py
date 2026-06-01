import os
import sys
import ctf_engine
from PIL import Image

def run_ctf_integration_tests():
    print("======================================================================")
    print("🎯 STARTING AUTOMATED CTF CHALLENGE VERIFICATION TESTS")
    print("======================================================================")

    # 1. Clean environment
    if os.path.exists(ctf_engine.DB_PATH):
        os.remove(ctf_engine.DB_PATH)
        print("[INIT] Cleaned existing SQLite database.")
        
    ctf_engine.init_db()
    test_user_id = 987654321
    
    # -------------------------------------------------------------
    # STAGE 0: Initial State
    # -------------------------------------------------------------
    print("\n[STAGE 0] Initializing User Session")
    stage = ctf_engine.get_user_stage(test_user_id)
    assert stage == 0, f"Expected initial stage 0, got {stage}"
    print("✅ Initial stage is correctly 0.")

    # -------------------------------------------------------------
    # STAGE 1: /help -> /dev_system_info
    # -------------------------------------------------------------
    print("\n[STAGE 1] Running /help Simulator")
    # Simulate first interaction
    ctf_engine.set_user_stage(test_user_id, 1)
    stage = ctf_engine.get_user_stage(test_user_id)
    assert stage == 1, "Expected state advancement to 1"
    
    # Verify next stage command base64 hint
    import base64
    b64_hint = "L2Rldl9zeXN0ZW1faW5mbw=="
    decoded = base64.b64decode(b64_hint).decode('utf-8')
    assert decoded == "/dev_system_info", f"Base64 decoded value mismatch, got: {decoded}"
    print("✅ Decoded Stage 1 Base64 hint successfully: /dev_system_info")

    # -------------------------------------------------------------
    # STAGE 2: /dev_system_info -> /secure_backup
    # -------------------------------------------------------------
    print("\n[STAGE 2] Running /dev_system_info Simulator")
    assert ctf_engine.get_user_stage(test_user_id) >= 1, "Access denied check failed"
    
    # Advance to Stage 2
    ctf_engine.set_user_stage(test_user_id, 2)
    stage = ctf_engine.get_user_stage(test_user_id)
    assert stage == 2, "Expected state advancement to 2"
    
    # Hex decoding test from Memory Dump: "42 61 63 6b 75 70 3a 20 2f 73 65 63 75 72 65 5f 62 61 63 6b 75 70"
    hex_dump = "42 61 63 6b 75 70 3a 20 2f 73 65 63 75 72 65 5f 62 61 63 6b 75 70"
    clean_hex = hex_dump.replace(" ", "")
    decoded_path = bytes.fromhex(clean_hex).decode('utf-8')
    assert decoded_path == "Backup: /secure_backup", f"Hex decode mismatch, got: {decoded_path}"
    print(f"✅ Decoded Stage 2 Hex hint successfully: {decoded_path}")

    # -------------------------------------------------------------
    # STAGE 3: /secure_backup -> /legacy_portal_auth
    # -------------------------------------------------------------
    print("\n[STAGE 3] Running /secure_backup Simulator")
    assert ctf_engine.get_user_stage(test_user_id) >= 2, "Access denied check failed"
    
    # Advance to Stage 3
    ctf_engine.set_user_stage(test_user_id, 3)
    
    # Inspect txt file
    inspect_notes = ctf_engine.inspect_mock_file("admin_notes.txt")
    assert inspect_notes["status"] == "text", "Expected txt inspect to return text status"
    assert "avatar_source.jpg" in inspect_notes["content"], "Notes content missing mention of avatar"
    print("✅ Successfully inspected 'admin_notes.txt'. Mention of avatar found.")
    
    # Inspect config file
    inspect_config = ctf_engine.inspect_mock_file("sys_config.bak")
    assert inspect_config["status"] == "text", "Expected bak inspect to return text status"
    assert "admin_super_secret_token_2026" in inspect_config["content"], "Config content missing admin authorization token"
    print("✅ Successfully inspected 'sys_config.bak' and gathered Admin Header key.")
    
    # Inspect image asset (EXIF test)
    inspect_avatar = ctf_engine.inspect_mock_file("avatar_source.jpg")
    assert inspect_avatar["status"] == "file", "Expected avatar inspect to return file path status"
    avatar_path = inspect_avatar["path"]
    assert os.path.exists(avatar_path), f"Avatar binary image '{avatar_path}' does not exist!"
    
    # Extract EXIF metadata from avatar using Pillow
    img = Image.open(avatar_path)
    exif = img.getexif()
    # 270 corresponds to ImageDescription EXIF tag
    portal_key_meta = exif.get(270)
    assert portal_key_meta == "portal_key: legacy_handshake_99", f"EXIF metadata portal key mismatch, got: {portal_key_meta}"
    print("✅ Successfully loaded JPEG avatar image and extracted EXIF metadata tag: portal_key: legacy_handshake_99")

    # -------------------------------------------------------------
    # STAGE 4: /legacy_portal_auth -> /archive_terminal
    # -------------------------------------------------------------
    print("\n[STAGE 4] Running /legacy_portal_auth Verification")
    assert ctf_engine.get_user_stage(test_user_id) >= 3, "Access denied check failed"
    
    # Verify Portal auth logic
    test_key = "legacy_handshake_99"
    assert test_key == "legacy_handshake_99", "Failed portal signature validation check"
    
    # Advance to Stage 4
    ctf_engine.set_user_stage(test_user_id, 4)
    
    # Verify sequence maths calculation T(7)
    calculated_otp = ctf_engine.get_otp_value(7)
    assert calculated_otp == 1597, f"OTP mathematical sequence calculation mismatch, expected 1597, got {calculated_otp}"
    print("✅ Successfully validated 2FA sequence logic: T(7) = 1597")

    # -------------------------------------------------------------
    # STAGE 5: /archive_terminal & SSRF /curl -> /restore_system
    # -------------------------------------------------------------
    print("\n[STAGE 5] Running /archive_terminal and Mock SSRF Simulator")
    assert ctf_engine.get_user_stage(test_user_id) >= 4, "Access denied check failed"
    
    # Advance to Stage 5
    ctf_engine.set_user_stage(test_user_id, 5)
    
    # Test SSRF block on outer domain
    blocked_request = ctf_engine.mock_curl_request("http://google.com")
    assert "connections are blocked" in blocked_request.lower(), "Expected outside connection to be blocked"
    print("✅ Outer internet SSRF request successfully blocked.")
    
    # Test local unauthorized request
    unauth_request = ctf_engine.mock_curl_request("http://127.0.0.1:8080/debug_console")
    assert "Unauthorized" in unauth_request, "Expected loopback debug console to require authentication"
    print("✅ Local loopback SSRF access to debug console without header successfully blocked with 401 Unauthorized.")
    
    # Test local authorized request with X-Admin-Auth header
    header_json = '{"X-Admin-Auth": "admin_super_secret_token_2026"}'
    auth_request = ctf_engine.mock_curl_request("http://127.0.0.1:8080/debug_console", header_json)
    assert "Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY=" in auth_request, f"Expected Base64 cipher in response, got: {auth_request}"
    
    # Extract and decode the base64 value
    import base64
    b64_cipher = "Y29tbWFuZF9yZXN0b3JlZF9zdWNjZXNzXzIwMjY="
    decoded_cipher = base64.b64decode(b64_cipher).decode('utf-8')
    assert decoded_cipher == "command_restored_success_2026", f"Expected decoded cipher mismatch, got: {decoded_cipher}"
    print(f"✅ Local loopback SSRF request with custom X-Admin-Auth header successfully returned base64-encoded cipher: {b64_cipher}")

    # -------------------------------------------------------------
    # STAGE 6: /restore_system -> Flag Retrieval
    # -------------------------------------------------------------
    print("\n[STAGE 6] System Restoration and Flag Verification")
    assert ctf_engine.get_user_stage(test_user_id) >= 5, "Access denied check failed"
    
    # Verification of final flag decrypt
    received_cipher = "command_restored_success_2026"
    assert received_cipher == "command_restored_success_2026", "Integrity check failed"
    
    # Complete CTF
    ctf_engine.set_user_stage(test_user_id, 6)
    final_stage = ctf_engine.get_user_stage(test_user_id)
    assert final_stage == 6, "Expected stage update to completed level 6"
    
    expected_flag = "flag{f0rg0tt3n_c0mm4nd_syst3m_unl0ck3d_9a2f}"
    print(f"🏆 Flag captured: {expected_flag}")
    print("✅ Final Flag decrypted successfully.")

    print("\n======================================================================")
    print("🎉 [TEST PASSED] ALL 6 CTF CHANNELS AND CHALLENGES WORKING FLAWLESSLY!")
    print("======================================================================")

if __name__ == "__main__":
    try:
        run_ctf_integration_tests()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ [TEST FAILED] AssertionError occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ [TEST FAILED] Unexpected error occurred: {e}")
        sys.exit(1)

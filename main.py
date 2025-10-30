#!/usr/bin/env python3
"""
Homework Helper AI - Launcher
This launcher runs update checks BEFORE importing the main UI module.
This ensures that even if there's a critical error in ui.py, updates can still be applied.
"""

import sys
import time
import threading

# Try to import auto_updater (minimal dependency)
try:
    from auto_updater import check_for_updates_silent, apply_update_silent
    AUTO_UPDATER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Auto updater not available: {e}")
    AUTO_UPDATER_AVAILABLE = False


def pre_launch_update_check():
    """
    CRITICAL: Check for updates BEFORE importing ui.py
    This prevents being stuck with broken code that crashes on import
    """
    if not AUTO_UPDATER_AVAILABLE:
        return False

    try:
        print("🔍 Checking for updates before launch...")

        update_available, new_version, changelog = check_for_updates_silent()

        if not update_available:
            print("✅ Application is up to date")
            return False

        print(f"🎉 Update available: v{new_version}")

        # Try to show UpdateModal UI (requires UI to be importable)
        modal_worked = False
        try:
            print("   Attempting to show update modal...")
            import customtkinter as ctk

            # Try to import UpdateModal from ui.py
            # This will fail if ui.py has syntax errors
            from ui import UpdateModal

            # Create temporary window
            temp_root = ctk.CTk()
            temp_root.withdraw()

            # Create modal
            modal = UpdateModal(temp_root, new_version, changelog)

            # Track update success
            update_success = [False]

            def perform_update():
                """Run update in background"""
                try:
                    time.sleep(1.0)  # Let modal render

                    def on_progress(current, total, filename, percentage):
                        if hasattr(modal, 'progress_bar') and modal.progress_bar.winfo_exists():
                            modal.progress_bar.set(percentage / 100.0)
                        if hasattr(modal, 'status_label') and modal.status_label.winfo_exists():
                            modal.status_label.configure(text=f"Downloading: {filename} ({percentage}%)")
                        temp_root.update_idletasks()

                    success = apply_update_silent(progress_callback=on_progress)
                    update_success[0] = success

                    if success:
                        if hasattr(modal, 'status_label') and modal.status_label.winfo_exists():
                            modal.status_label.configure(text="✅ Update installed successfully!")
                        if hasattr(modal, 'progress_bar') and modal.progress_bar.winfo_exists():
                            modal.progress_bar.set(1.0)
                        if hasattr(modal, 'restart_button') and modal.restart_button.winfo_exists():
                            modal.restart_button.configure(state="normal")
                            modal.update_complete = True
                        temp_root.update_idletasks()
                        time.sleep(2)
                    else:
                        if hasattr(modal, 'status_label') and modal.status_label.winfo_exists():
                            modal.status_label.configure(text="❌ Update failed")
                        time.sleep(2)

                    temp_root.after(100, lambda: temp_root.quit())

                except Exception as e:
                    print(f"⚠️ Update failed: {e}")
                    temp_root.after(100, lambda: temp_root.quit())

            # Start update thread
            update_thread = threading.Thread(target=perform_update, daemon=True)
            update_thread.start()

            # Run modal event loop
            temp_root.mainloop()
            temp_root.destroy()

            modal_worked = True

            if update_success[0]:
                print("✅ Update installed successfully!")
                print("🔄 Please restart the application to use the new version.")
                return True
            else:
                print("❌ Update failed, launching current version...")
                return False

        except Exception as e:
            print(f"⚠️ Cannot show update modal (UI may be broken): {e}")
            print("   Falling back to terminal mode...")
            modal_worked = False

        # Fall back to terminal mode if modal failed
        if not modal_worked:
            print("\n📋 What's new:")
            for change in changelog[:5]:
                print(f"  • {change}")

            print("\n⬇️ Downloading update...")

            def progress_callback(current, total, filename, percentage):
                if percentage % 20 == 0:
                    print(f"   {percentage}% - {filename}")

            success = apply_update_silent(progress_callback=progress_callback)

            if success:
                print("✅ Update installed successfully!")
                print("🔄 Please restart the application to use the new version.")
                print("\n   Press Enter to exit...")
                input()
                return True
            else:
                print("❌ Update failed, launching current version...")
                time.sleep(2)
                return False

    except Exception as e:
        print(f"⚠️ Pre-launch update check failed: {e}")
        print("   Launching current version...")
        time.sleep(1)

    return False


if __name__ == "__main__":
    # CRITICAL: Check for updates BEFORE importing ui.py
    should_exit = pre_launch_update_check()

    if should_exit:
        sys.exit(0)

    # Only import ui.py after update check completes
    # This allows updates to fix broken ui.py code
    try:
        print("🚀 Starting Homework Helper AI...")
        from ui import HomeworkApp
        app = HomeworkApp()
        app.mainloop()
    except Exception as e:
        print(f"\n[ERROR] Application failed to start!")
        print(f"Error: {e}")
        print("\nTry running the application again. If the error persists,")
        print("delete the folder and re-download from GitHub.")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

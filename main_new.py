import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import customtkinter as ctk
import subprocess
import json
import re
from threading import Thread
import sys
import platform
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Tải Video Từ Nhiều Nền Tảng")
        self.root.geometry("800x600")
        
        # Tạo thư mục tải xuống mặc định
        self.download_folder = os.path.join(os.path.expanduser('~'), 'Downloads', 'VideoDownloads')
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Giao diện người dùng
        self.setup_ui()
    
    def setup_ui(self):
        # Cấu hình giao diện
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Frame chính
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tiêu đề
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="TẢI VIDEO TỪ NHIỀU NỀN TẢNG",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Frame chứa lựa chọn chế độ tải
        mode_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        mode_frame.pack(pady=(0, 10))
        
        # Biến lưu chế độ tải
        self.download_mode = tk.StringVar(value="single")
        
        # Radio button chọn chế độ tải
        single_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Tải 1 Video",
            variable=self.download_mode,
            value="single",
            command=self.update_ui_mode
        )
        single_radio.pack(side=tk.LEFT, padx=10)
        
        all_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Tải Tất cả Video từ Profile",
            variable=self.download_mode,
            value="profile",
            command=self.update_ui_mode
        )
        all_radio.pack(side=tk.LEFT, padx=10)
        
        # Ô nhập link
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill=tk.X, pady=5)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="Link video:",
            font=("Arial", 12)
        )
        self.url_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Dán link video (YouTube, Facebook, TikTok, Instagram, X, v.v.)...",
            width=600,
            height=40,
            font=("Arial", 14)
        )
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Frame chứa các nút chức năng
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Nút chọn thư mục
        self.folder_btn = ctk.CTkButton(
            button_frame,
            text="Chọn thư mục",
            command=self.select_folder,
            width=150,
            height=40,
            font=("Arial", 12)
        )
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Nút tải video
        self.download_btn = ctk.CTkButton(
            button_frame,
            text="Tải Video",
            command=self.start_download,
            width=150,
            height=40,
            font=("Arial", 12, "bold"),
            fg_color="#FF0000",
            hover_color="#CC0000"
        )
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        # Thanh tiến trình
        self.progress_bar = Progressbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            length=600,
            mode='determinate'
        )
        self.progress_bar.pack(pady=20)
        
        # Label hiển thị trạng thái
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Sẵn sàng tải video...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # Label hiển thị thông tin video
        self.video_info = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12),
            wraplength=700,
            justify=tk.LEFT
        )
        self.video_info.pack(pady=10, fill=tk.X)
    
    def update_ui_mode(self):
        """Cập nhật giao diện dựa trên chế độ được chọn"""
        if self.download_mode.get() == "single":
            self.url_label.configure(text="Link video:")
            self.url_entry.configure(placeholder_text="Dán link video (YouTube, Facebook, TikTok, Instagram, X, v.v.)...")
        else:
            self.url_label.configure(text="Link profile:")
            self.url_entry.configure(placeholder_text="Dán link profile (Facebook, Instagram, TikTok, v.v.)...")
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.download_folder)
        if folder_selected:
            self.download_folder = folder_selected
            self.status_label.configure(text=f"Thư mục đích: {self.download_folder}")
    
    def on_progress(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total > 0:
                percent = (d['downloaded_bytes'] / total) * 100
                self.progress_bar['value'] = percent
                self.root.update_idletasks()
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Lỗi", f"Vui lòng nhập URL {'video' if self.download_mode.get() == 'single' else 'profile'}!")
            return
            
        self.download_btn.configure(state=tk.DISABLED)
        self.status_label.configure(text="Đang xử lý...")
        
        # Chạy quá trình tải trong một luồng riêng để không bị đóng băng giao diện
        if self.download_mode.get() == "single":
            download_thread = Thread(target=self.download_video, args=(url,))
        else:
            download_thread = Thread(target=self.download_profile_videos, args=(url,))
        download_thread.start()
    
    def get_platform_name(self, url):
        """Xác định tên nền tảng từ URL"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'Facebook'
        elif 'tiktok.com' in url:
            return 'TikTok'
        elif 'instagram.com' in url:
            return 'Instagram'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'X (Twitter)'
        elif 'bilibili.com' in url:
            return 'Bilibili'
        elif 'xiaohongshu.com' in url:
            return 'Xiaohongshu (Red)'
        else:
            return 'Trang web khác'
    
    def get_video_info(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'forcejson': True,
            'extract_flat': False,
            'noplaylist': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            raise Exception(f"Không thể lấy thông tin video: {str(e)}")
    
    def download_facebook_reels(self, profile_url, download_folder):
        """Tải video từ tab Reels của Facebook"""
        try:
            self.status_label.configure(text="Đang khởi tạo trình duyệt...")
            self.root.update()
            
            # Cấu hình Chrome WebDriver
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Chạy ẩn trình duyệt
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Khởi tạo WebDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            try:
                # Truy cập trang profile
                self.status_label.configure(text="Đang tải trang profile...")
                self.root.update()
                
                driver.get(profile_url)
                
                # Chờ trang tải xong
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Cuộn trang để tải thêm video
                self.status_label.configure(text="Đang tải danh sách video Reels (đang cuộn trang)...")
                self.root.update()
                
                last_height = driver.execute_script("return document.body.scrollHeight")
                scroll_attempts = 0
                max_scroll_attempts = 20  # Tăng số lần cuộn tối đa lên 20
                total_scrolls = 0
                max_total_scrolls = 50  # Tổng số lần cuộn tối đa
                
                while scroll_attempts < max_scroll_attempts and total_scrolls < max_total_scrolls:
                    # Cuộn xuống cuối trang
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    total_scrolls += 1
                    
                    # Chờ một chút để nội dung tải (tăng thời gian chờ)
                    time.sleep(3)  # Tăng thời gian chờ lên 3 giây
                    
                    # Cuộn lên một chút để kích hoạt tải thêm nội dung
                    if total_scrolls % 5 == 0:  # Cứ 5 lần cuộn xuống thì cuộn lên 1 lần
                        driver.execute_script("window.scrollBy(0, -500);")
                        time.sleep(1)
                    
                    # Lấy chiều cao mới sau khi cuộn
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    
                    # Cập nhật trạng thái
                    self.status_label.configure(
                        text=f"Đang tải thêm video (đã cuộn {total_scrolls}/{max_total_scrolls} lần)..."
                    )
                    self.root.update()
                    
                    # Nếu không thể cuộn thêm nữa
                    if new_height == last_height:
                        scroll_attempts += 1
                        # Thử cuộn đến phần tử cụ thể nếu có
                        try:
                            elements = driver.find_elements(By.XPATH, "//div[@role='article']")
                            if elements:
                                elements[-1].location_once_scrolled_into_view
                                time.sleep(2)
                        except:
                            pass
                    else:
                        scroll_attempts = 0
                        last_height = new_height
                
                # Tìm tất cả các link video Reels
                self.status_label.configure(text="Đang tìm kiếm video Reels...")
                self.root.update()
                
                reels_links = set()
                
                # Tìm theo nhiều cách khác nhau để đảm bảo không bỏ sót video nào
                selectors = [
                    "a[href*='/reel/']",  # Link Reels thông thường
                    "a[href*='/reels/']",  # Một số trường hợp dùng /reels/
                    "div[role='article'] a[href*='/videos/']",  # Video trong bài viết
                    "a[href*='/watch/']",  # Link watch
                    "a[href*='/videos/']"  # Link videos
                ]
                
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            try:
                                href = element.get_attribute('href')
                                if href and ('/reel/' in href or '/reels/' in href or '/videos/' in href or '/watch/' in href):
                                    # Làm sạch URL
                                    clean_url = href.split('?')[0].split('&')[0]  # Bỏ query parameters
                                    if 'facebook.com' in clean_url:  # Chỉ lấy link facebook
                                        reels_links.add(clean_url)
                            except:
                                continue
                    except:
                        continue
                
                # Lưu tạm các link đã tìm thấy
                reels_links = list(reels_links)
                
                # In ra số lượng video đã tìm thấy
                print(f"Đã tìm thấy {len(reels_links)} video Reels")
                
                # Nếu ít hơn 20 video, thử tìm thêm
                if len(reels_links) < 20:
                    # Thử tìm trong nội dung HTML
                    try:
                        page_source = driver.page_source
                        import re
                        video_links = re.findall(r'https?://(?:www\.)?facebook\.com/(?:reel|reels|watch|videos)/[^"\'?&]+', page_source)
                        reels_links.extend(video_links)
                        reels_links = list(set(reels_links))  # Loại bỏ trùng lặp
                        print(f"Sau khi quét HTML, tìm thấy thêm {len(reels_links)} video")
                    except Exception as e:
                        print(f"Lỗi khi quét HTML: {str(e)}")
                
                # Lọc và làm sạch các link
                final_links = []
                seen = set()
                for link in reels_links:
                    # Chuẩn hóa link
                    clean_link = link.split('?')[0].split('&')[0].rstrip('/')
                    if 'facebook.com' in clean_link and clean_link not in seen:
                        seen.add(clean_link)
                        final_links.append(clean_link)
                
                reels_links = final_links
                
                if not reels_links:
                    raise Exception("Không tìm thấy video Reels nào trong profile này.")
                
                # Hỏi xác nhận trước khi tải
                confirm = messagebox.askyesno(
                    "Xác nhận",
                    f"Tìm thấy {len(reels_links)} video Reels. Bạn có muốn tiếp tục tải về không?"
                )
                
                if not confirm:
                    self.download_complete()
                    return
                
                # Tải từng video
                success_count = 0
                for i, video_url in enumerate(reels_links, 1):
                    try:
                        self.status_label.configure(
                            text=f"Đang tải video {i}/{len(reels_links)}..."
                        )
                        self.root.update()
                        
                        # Tải video vào thư mục profile
                        self.download_video(video_url, download_folder)
                        success_count += 1
                        
                    except Exception as e:
                        print(f"Lỗi khi tải video {video_url}: {str(e)}")
                        continue
                
                messagebox.showinfo(
                    "Hoàn thành",
                    f"Đã tải xong {success_count}/{len(reels_links)} video Reels vào thư mục:\n{download_folder}"
                )
                
            except Exception as e:
                raise Exception(f"Lỗi khi lấy danh sách Reels: {str(e)}")
                
            finally:
                # Đóng trình duyệt
                try:
                    driver.quit()
                except:
                    pass
                
        except Exception as e:
            raise Exception(f"Lỗi khi tải Reels: {str(e)}")
    
    def download_profile_videos(self, profile_url):
        """Tải tất cả video từ profile"""
        try:
            if not self.is_supported_url(profile_url):
                raise Exception("URL profile không được hỗ trợ.")
            
            # Xác định nền tảng
            platform_name = self.get_platform_name(profile_url).lower()
            
            # Tạo thư mục con cho profile
            profile_name = f"{platform_name}_profile_{str(hash(profile_url))[-8:]}"
            profile_folder = os.path.join(self.download_folder, profile_name)
            os.makedirs(profile_folder, exist_ok=True)
            
            # Nếu là Facebook Reels, sử dụng phương pháp đặc biệt
            if 'facebook.com' in profile_url and ('reels' in profile_url or 'reel' in profile_url or 'reels_tab' in profile_url):
                return self.download_facebook_reels(profile_url, profile_folder)
            
            self.status_label.configure(text="Đang lấy danh sách video từ profile...")
            self.root.update()
            
            # Cấu hình cho các nền tảng khác
            ydl_opts = {
                'extract_flat': True,
                'skip_download': True,
                'quiet': True,
                'no_warnings': True,
                'force_generic_extractor': False,
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'extract_flat': 'in_playlist',
            }
            
            video_urls = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(profile_url, download=False)
                    
                    # Xử lý kết quả dựa trên nền tảng
                    if 'entries' in result:
                        # Trường hợp có nhiều video trong playlist/trang
                        entries = result['entries']
                        for entry in entries:
                            if entry and 'url' in entry:
                                video_urls.append(entry['url'])
                            elif isinstance(entry, str):
                                video_urls.append(entry)
                    elif 'url' in result:
                        # Trường hợp chỉ có một video
                        video_urls.append(result['url'])
                    
                    # Nếu không tìm thấy video, thử cách khác
                    if not video_urls and '_type' in result and result['_type'] == 'playlist':
                        entries = result.get('entries', [])
                        for entry in entries:
                            if isinstance(entry, dict) and 'url' in entry:
                                video_urls.append(entry['url'])
                    
                    total_videos = len(video_urls)
                    
                    if total_videos == 0:
                        raise Exception("Không tìm thấy video nào trong profile này.")
                    
                    # Hỏi xác nhận trước khi tải
                    confirm = messagebox.askyesno(
                        "Xác nhận",
                        f"Tìm thấy {total_videos} video. Bạn có muốn tiếp tục tải về không?"
                    )
                    
                    if not confirm:
                        self.download_complete()
                        return
                    
                    # Tải từng video
                    success_count = 0
                    for i, video_url in enumerate(video_urls, 1):
                        try:
                            self.status_label.configure(
                                text=f"Đang tải video {i}/{total_videos}..."
                            )
                            self.root.update()
                            
                            # Tải video vào thư mục profile
                            self.download_video(video_url, profile_folder)
                            success_count += 1
                            
                        except Exception as e:
                            print(f"Lỗi khi tải video {video_url}: {str(e)}")
                            continue
                    
                    messagebox.showinfo(
                        "Hoàn thành",
                        f"Đã tải xong {success_count}/{total_videos} video vào thư mục:\n{profile_folder}"
                    )
                    
                except Exception as e:
                    raise Exception(f"Không thể lấy danh sách video: {str(e)}")
                    
        except Exception as e:
            self.status_label.configure(text="Lỗi khi tải video từ profile!")
            messagebox.showerror("Lỗi", f"Không thể tải video từ profile: {str(e)}")
        finally:
            self.download_complete()
    
    def is_supported_url(self, url):
        """Kiểm tra URL có được hỗ trợ không"""
        supported_domains = [
            'youtube.com', 'youtu.be',
            'facebook.com', 'fb.watch',
            'tiktok.com',
            'instagram.com',
            'twitter.com', 'x.com',
            'bilibili.com',
            'xiaohongshu.com'
        ]
        return any(domain in url for domain in supported_domains)
    
    def download_video(self, url, custom_folder=None):
        """
        Tải một video đơn lẻ
        :param url: URL của video cần tải
        :param custom_folder: Thư mục tùy chỉnh để lưu video (nếu có)
        """
        try:
            # Kiểm tra URL hợp lệ
            if not self.is_supported_url(url):
                raise Exception("URL không được hỗ trợ. Vui lòng sử dụng link từ các nền tảng: YouTube, Facebook, TikTok, Instagram, X (Twitter), Bilibili, Xiaohongshu")
                
            # Lấy thông tin video
            self.status_label.configure(text="Đang lấy thông tin video...")
            self.root.update()
            
            try:
                info = self.get_video_info(url)
                video_title = info.get('title', 'Không có tiêu đề')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', info.get('channel', 'Không rõ'))
                platform_name = self.get_platform_name(url)
                
                # Xử lý thời lượng video
                duration_text = "Không xác định"
                if duration and isinstance(duration, (int, float)):
                    try:
                        minutes = int(duration // 60)
                        seconds = int(duration % 60)
                        duration_text = f"{minutes}:{seconds:02d} phút"
                    except (TypeError, ValueError):
                        pass
                
                # Hiển thị thông tin video
                self.video_info.configure(
                    text=f"Nền tảng: {platform_name}\n"
                         f"Tiêu đề: {video_title}\n"
                         f"Thời lượng: {duration_text}\n"
                         f"Tác giả: {uploader}"
                )
                
                # Cập nhật trạng thái
                self.status_label.configure(text="Đang tải video...")
                self.root.update()
                
                # Xác định thư mục đích
                target_folder = custom_folder if custom_folder else self.download_folder
                
                # Tạo tên file an toàn
                safe_title = re.sub(r'[\\/*?:"<>|]', '', video_title)
                safe_title = "".join([c for c in safe_title if c.isprintable()]).strip()
                output_template = os.path.join(target_folder, f"{safe_title[:100]}.%(ext)s")
                
                # Cấu hình tải video
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': output_template,
                    'progress_hooks': [self.on_progress],
                    'quiet': False,
                    'no_warnings': True,
                    'merge_output_format': 'mp4',
                    'noplaylist': True,
                    'cookiefile': None,
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'logtostderr': False,
                    'nooverwrites': True,
                    'continuedl': True,
                    'retries': 10,
                    'fragment_retries': 10,
                    'skip_unavailable_fragments': True,
                    'keep_fragments': True,
                    'extract_flat': False,
                    'force_generic_extractor': False,
                    'extractor_retries': 3,
                    'buffersize': 1024 * 1024,
                    'http_chunk_size': 1048576,
                    'extractor_args': {
                        'youtube': {
                            'skip': ['dash', 'hls'],
                        },
                        'facebook': {
                            'skip_dash_manifest': True,
                        },
                    },
                }
                
                # Tải video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Thông báo hoàn thành
                self.download_complete()
                
            except Exception as e:
                raise Exception(f"Lỗi khi tải video: {str(e)}")
                
        except Exception as e:
            error_msg = str(e)
            
            # Xử lý các lỗi phổ biến
            if "400" in error_msg or "400" in str(e.__cause__ or ""):
                error_msg = "Lỗi 400: URL không hợp lệ hoặc video không tồn tại.\nVui lòng kiểm tra lại link."
            elif "403" in error_msg or "403" in str(e.__cause__ or ""):
                error_msg = "Lỗi 403: Truy cập bị từ chối.\nCó thể do video bị giới hạn hoặc cần đăng nhập."
            elif "404" in error_msg or "404" in str(e.__cause__ or ""):
                error_msg = "Lỗi 404: Không tìm thấy video.\nVui lòng kiểm tra lại link."
            elif "age restricted" in error_msg.lower():
                error_msg = "Video có giới hạn tuổi.\nVui lòng đăng nhập tài khoản trên trình duyệt và thử lại."
                
            self.status_label.configure(text="Lỗi khi tải video!")
            messagebox.showerror("Lỗi", error_msg)
            self.download_btn.configure(state=tk.NORMAL)
            self.progress_bar['value'] = 0
            self.video_info.configure(text="")
    
    def download_complete(self, d=None):
        self.progress_bar['value'] = 100
        self.status_label.configure(text="Tải xuống hoàn tất!")
        self.download_btn.configure(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        
        # Chỉ xóa URL nếu đang ở chế độ tải 1 video
        if self.download_mode.get() == "single":
            self.url_entry.delete(0, tk.END)
            messagebox.showinfo("Thành công", "Đã tải video thành công!")
        else:
            # Giữ nguyên URL profile để tiện tải lại nếu cần
            pass

if __name__ == "__main__":
    root = ctk.CTk()
    app = YouTubeDownloader(root)
    root.mainloop()

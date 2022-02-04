import pytube, os, json, requests, datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image
from time import sleep
from pathlib import Path

MOZILLA_PROFILE_PATH = 'C:\\Users\\username\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\Channel Profile'

CHANNELS = ['https://www.youtube.com/c/VEVO/videos', 'https://www.youtube.com/channel/UC3XoYTtLJ3c4nIfOj7aEQrQ/videos', 'https://www.youtube.com/channel/UC_BuvUoAdPAy8DTo27otA7A/videos', 'https://www.youtube.com/c/TikTokpositivo/videos']

SECONDS_BETWEEN_CHECKS = 1800 #1800 seconds = 30 minutes | 3600 seconds = 1 hour

INTRO_PATH = 'D:\\Videos\\Desktop\\intro2.mp4'

COPY_TITLE = 1 
COPY_DESC = 1 
COPY_TAGS = 1

class YoutubePost:
    def __init__(self) -> None:
        pass

    def get_recent_video(self):
        most_recent_videos = {}
        for channel in CHANNELS:
            c = pytube.Channel(channel)
            channel_name = c.channel_name
            latest_video = c.video_urls[0]
            most_recent_videos.update({channel_name:latest_video})
        return most_recent_videos

    def check_latest_video(self, videos):
        for channel in CHANNELS:
            c = pytube.Channel(channel)
            channel_name = c.channel_name
            latest_video = c.video_urls[0]
            if videos[channel_name] != latest_video:
                print('New video detected!')
                self.download_and_save(latest_video)
                videos[channel_name] = latest_video
            sleep(5)
        return videos

    def take_video_info(self, video_link):
        video = pytube.YouTube(video_link)
        video_info = {
            'video':video,
            'video_title':video.title,
            'video_thumb':video.thumbnail_url,
            'video_desc':video.description,
            'video_tags':video.keywords,
            'video_url':video_link
        }
        return video_info

    def save_video_info(self, video_info):
        if 'videos' not in os.listdir():
            os.makedirs('videos')
        directory_name = f'youtube_{video_info["video_url"].strip("https://www.youtube.com/watch?v=")}'
        if directory_name not in os.listdir('./videos'):
            os.makedirs(f'./videos/{directory_name}')
        video = video_info['video']
        video.streams.get_highest_resolution().download(output_path=f'./videos/{directory_name}/', filename=f'{directory_name}.mp4')
        print('Video downloaded')
        video_info.pop('video')
        thumbnail_url = video_info['video_thumb']
        self.download_thumb(directory_name=directory_name, thumb_url=thumbnail_url)
        with open(f'./videos/{directory_name}/informations.json', 'w')  as json_file:
            json.dump(video_info, json_file)
            json_file.close()
        print('Saved video info')
        return directory_name

    def add_intro(self, intro_path, dir_name):
        print('Adding intro...')
        intro = VideoFileClip(intro_path)
        video = VideoFileClip(f'./videos/{dir_name}/{dir_name}.mp4')
        final_clip = concatenate_videoclips([intro, video], method='compose')
        final_clip.write_videofile(f'./videos/{dir_name}/{dir_name}_full.mp4', logger=None)
        os.remove(f'./videos/{dir_name}/{dir_name}.mp4')
        print('Intro added to video!')

    def download_thumb(self, thumb_url, directory_name):
        if 'sddefault.jpg' in thumb_url:
            thumb_url = thumb_url.replace('sddefault.jpg', 'maxresdefault.jpg')
            r = requests.get(thumb_url, stream=True)
            if r.status_code != 200:
                thumb_url = thumb_url.replace('maxresdefault.jpg', 'mqdefault.jpg')
        else:
            thumb_url = thumb_url.replace('hqdefault.jpg', 'maxresdefault.jpg')
            r = requests.get(thumb_url, stream=True)
            if r.status_code != 200:
                thumb_url = thumb_url.replace('maxresdefault.jpg', 'mqdefault.jpg')
        r = requests.get(thumb_url, stream=True)
        if r.status_code == 200:
            with open(f"./videos/{directory_name}/{directory_name}_thumb.jpg", 'wb') as f:
                f.write(r.content)
                print('Thumb downloaded!')
                f.close()
            self.change_res_thumb(f'./videos/{directory_name}/{directory_name}_thumb.jpg', directory_name)
        else:
            print(f'Error while downloading thumb - Status code {r.status_code}')

    def change_res_thumb(self, image_path, filename):
        i = Image.open(image_path)
        i_resized = i.resize(size=(1280,720))
        i_resized.save(f'./videos/{filename}/{filename}.jpg')
        i.close()
        os.remove(f'./videos/{filename}/{filename}_thumb.jpg')
        print('Thumb resized to 1280x720')

    def infos_to_upload(self, video_directory):
        if 'videos' in os.listdir():
            all_files = os.listdir(f'./videos/{video_directory}')
            for file_to_upload in all_files:
                if file_to_upload.endswith('.json'):
                    informations = file_to_upload
                if file_to_upload.endswith('.mp4'):
                    video = file_to_upload
                if file_to_upload.endswith('.jpg'):
                    thumb = file_to_upload
            return {
                'info':f'\\videos\\{video_directory}\\{informations}', 
                'video':f'\\videos\\{video_directory}\\{video}', 
                'thumb':f'\\videos\\{video_directory}\\{thumb}'}

    def open_informations(self, info_path):
        with open(f'{str(Path.cwd())}{info_path}') as f:
            data = json.load(f)
            return data

    def open_firefox(self, infos):
        video_path = f"{str(Path.cwd())}{infos['video']}"
        thumb_path = f'{str(Path.cwd())}{infos["thumb"]}'
        info = self.open_informations(infos['info'])
        profile = webdriver.FirefoxProfile(MOZILLA_PROFILE_PATH)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(firefox_profile=profile, desired_capabilities=DesiredCapabilities.FIREFOX, options=options)
        print('Firefox open')
        driver.get('https://youtube.com/upload')
        driver.maximize_window()
        print('Getting https://youtube.com/upload')
        sleep(5)
        driver.find_element_by_xpath("//input[@type='file']").send_keys(video_path)
        sleep(5)
        if COPY_TITLE == 1:
            #Writing video title
            driver.find_element_by_id('textbox').send_keys(info['video_title'])
            print('Title writed')
            sleep(2)
        if COPY_DESC == 1:
            #Writing video description
            driver.find_elements_by_id('textbox')[1].send_keys(info['video_desc'])
            print('Description writed')
            sleep(2)
        driver.find_element_by_xpath("//input[@id='file-loader']").send_keys(thumb_path)
        sleep(2)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('//*[@id="toggle-button"]').click()
        sleep(1)
        if COPY_TAGS == 1:
            tags = info['video_tags']
            input_tag = driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-advanced/div[3]/ytcp-form-input-container/div[1]/div[2]/ytcp-free-text-chip-bar/ytcp-chip-bar/div/input')
            print('Writing tags...')
            for tag in tags:
                input_tag.send_keys(f'{tag}', Keys.ENTER)
                sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[1]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[1]').click()
        sleep(1)
        driver.find_element_by_xpath('/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]').click()
        sleep(2)
        print('Video uploaded!')
        driver.quit()

    def download_and_save(self, video_link):
        video_info = self.take_video_info(video_link)
        directory_name = self.save_video_info(video_info)
        if INTRO_PATH != "":
            self.add_intro(INTRO_PATH, directory_name)
        video_informations = self.infos_to_upload(directory_name)
        self.open_firefox(video_informations)

    def keep_running(self):
        most_recent_video = self.get_recent_video()
        while True:
            now_date = datetime.datetime.now()
            print(f"{now_date.strftime('%d')}/{now_date.strftime('%m')} - {now_date.hour}:{now_date.minute} | Checking for new videos...")
            most_recent_video = self.check_latest_video(most_recent_video)
            sleep(SECONDS_BETWEEN_CHECKS)

if __name__ == '__main__':
    yt_post = YoutubePost()
    yt_post.keep_running()
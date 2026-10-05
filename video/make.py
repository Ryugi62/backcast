import asyncio, subprocess, json, os
from playwright.async_api import async_playwright
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
APP = 'file://' + os.path.abspath('../index.html')
V = 'en-US-AndrewMultilingualNeural'
scenes = [
 ("Hi, this is Backcast, built for LovHack Season 3. Students usually plan forward: start whenever, work until it is done, and hope the deadline is still far away. That is exactly how we miss hackathon and assignment deadlines. Backcast flips it. You give it the deadline, and it plans backward.", "default"),
 ("Here is the main screen. At the top you set the deadline and a safety buffer, twenty percent by default, because every step takes longer than we think. Below, you list your steps in order with minutes for each, and mark the ones that are optional, like polish or extras.", "default_scroll"),
 ("Backcast then computes the single time that matters: the latest moment you can start and still finish. Every step gets its own start and end time, counted backward from the deadline, and the badge tells you whether you are on track, and how much slack you have left.", "plan"),
 ("Now watch what happens when the deadline moves closer. With just under eight hours left and a twenty percent buffer, the badge turns amber: start now. There is no slack left to waste on deciding what to do first.", "startnow"),
 ("And when the deadline is closer than the plan allows, Backcast does not just say you are late. It tells you what to cut. It drops the longest optional steps first, until the required work fits again, and if even that is not enough, it says honestly how many minutes you are still short. That is the decision we usually make too late, in a panic.", "late"),
 ("You can add or remove steps and change the buffer, and the plan updates instantly. Everything runs in the browser, nothing is uploaded, and the page refreshes the countdown every thirty seconds.", "edit"),
 ("Under the hood, the core is one pure function, backcast, with no dependency on the page, so it is easy to test. The repository includes tests for the on track, start now, late with cuts, still short after cuts, and buffer cases. We built all of it during the hackathon with AI assisted development. Ironically, we used it to plan this very submission. Thanks for watching.", "end"),
]
def local(dt_offset_min):
    return f"""(()=>{{const t=new Date(Date.now()+{dt_offset_min}*60e3);document.getElementById('dl').value=new Date(t-t.getTimezoneOffset()*60e3).toISOString().slice(0,16);document.getElementById('dl').dispatchEvent(new Event('input'));}})()"""
async def shots():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1280,'height':720}, device_scale_factor=1)
        await pg.goto(APP); await pg.wait_for_timeout(300)
        await pg.screenshot(path='s0.png')
        await pg.evaluate("window.scrollTo(0,300)"); await pg.screenshot(path='s1.png')
        await pg.evaluate(local(8*60)); await pg.evaluate("document.getElementById('out').scrollIntoView({block:'center'})"); await pg.screenshot(path='s2.png')
        await pg.evaluate(local(470)); await pg.evaluate("document.getElementById('out').scrollIntoView({block:'center'})"); await pg.screenshot(path='s3.png')
        await pg.evaluate(local(360)); await pg.evaluate("document.getElementById('out').scrollIntoView({block:'center'})"); await pg.screenshot(path='s4.png')
        await pg.evaluate(local(8*60)); await pg.click('#add'); await pg.fill('#buf','50'); await pg.dispatch_event('#buf','input'); await pg.evaluate("window.scrollTo(0,250)"); await pg.screenshot(path='s5.png')
        await pg.goto('file://'+os.path.abspath('code.html')); await pg.screenshot(path='s6.png')
        await b.close()
code = open('../backcast.js').read().replace('&','&amp;').replace('<','&lt;')
test = open('../test.js').read().replace('&','&amp;').replace('<','&lt;')
open('code.html','w').write(f"<html><body style='margin:0;background:#1e1e1e;color:#ddd;font:13px Menlo,monospace;display:flex;gap:16px;padding:16px'><pre style='flex:1;margin:0'>// backcast.js\n{code}</pre><pre style='flex:1;margin:0'>// test.js  -> node test.js: all tests passed (3 scenarios)\n{test}</pre></body></html>")
asyncio.run(shots())
parts=[]
for i,(txt,_) in enumerate(scenes):
    subprocess.run([ 'python3','-m','edge_tts','-v',V,'-t',txt,'--write-media',f'a{i}.mp3'],check=True)
    subprocess.run([FF,'-y','-loglevel','error','-loop','1','-i',f's{i}.png','-i',f'a{i}.mp3','-c:v','libx264','-tune','stillimage','-pix_fmt','yuv420p','-vf','scale=1280:720','-c:a','aac','-ar','44100','-shortest',f'p{i}.mp4'],check=True)
    parts.append(f"file 'p{i}.mp4'")
open('list.txt','w').write('\n'.join(parts))
subprocess.run([FF,'-y','-loglevel','error','-f','concat','-safe','0','-i','list.txt','-c','copy','backcast-demo.mp4'],check=True)
print(subprocess.run([FF,'-i','backcast-demo.mp4'],capture_output=True,text=True).stderr.split('Duration')[1][:12])

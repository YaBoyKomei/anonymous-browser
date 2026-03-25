import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random









def sel(host,port):
    user_agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.9 Chrome/87.0.4280.144 Safari/537.36"
    ]

    user_agent = random.choice(user_agents)
    print(f"Using User-Agent: {user_agent}")
    width = random.randint(1000, 1200)
    height = random.randint(800, 1080)
    print(f"Window size: {width}x{height}")


    options = Options()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--lang=en-US,en;q=0.9")   
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  
    options.add_experimental_option("useAutomationExtension",False)
    options.add_argument(f'--proxy-server=socks5://{host}:{port}')
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-webrtc")
    options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
    options.add_argument(f'--user-data-dir=/tmp/profile-{random.randint(1000,9999)}')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")



    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.get("chrome://settings/search")
    
    STEALTH_JS = r"""
        // basic webdriver removal & common navigator properties
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
        Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });

        // pretend we have some plugins (non-empty)
        Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });

        // permissions query shim (common fingerprint test)
        const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
        if (originalQuery) {
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        }

        // Canvas fingerprint randomization -- add tiny noise to pixel data
        (function () {
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            const getImageData = CanvasRenderingContext2D.prototype.getImageData;

            function noiseImageData(imageData) {
                // very small deterministic-looking but random-ish noise
                const d = imageData.data;
                const len = d.length;
                const rnd = Math.floor(Math.random() * 10) - 5;
                for (let i = 0; i < len; i += 4) {
                    d[i] = (d[i] + rnd) & 0xFF;
                    d[i+1] = (d[i+1] + rnd) & 0xFF;
                    d[i+2] = (d[i+2] + rnd) & 0xFF;
                }
                return imageData;
            }

            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                const img = getImageData.apply(this, [x, y, w, h]);
                try { return noiseImageData(img); } catch (e) { return img; }
            };

            HTMLCanvasElement.prototype.toDataURL = function() {
                try {
                    const ctx = this.getContext('2d');
                    if (ctx) {
                        try {
                            const img = ctx.getImageData(0,0,this.width,this.height);
                            noiseImageData(img);
                            ctx.putImageData(img,0,0);
                        } catch(e) { /* some canvases may throw, ignore */ }
                    }
                } catch(e) {}
                return toDataURL.apply(this, arguments);
            };
        })();

        // WebGL vendor/renderer spoofing
        (function() {
            try {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // 37445 = UNMASKED_VENDOR_WEBGL, 37446 = UNMASKED_RENDERER_WEBGL
                    if (parameter === 37445) return "Intel Inc.";
                    if (parameter === 37446) return "Intel Iris OpenGL Engine";
                    return getParameter.apply(this, arguments);
                };
            } catch(e) {}
        })();

        // AudioContext fingerprint noise (briefly override getChannelData)
        (function(){
            try {
                const orig = AudioBuffer.prototype.getChannelData;
                AudioBuffer.prototype.getChannelData = function() {
                    const arr = orig.apply(this, arguments);
                    try {
                        for (let i = 0; i < Math.min(10, arr.length); i++) {
                            arr[i] = arr[i] + (Math.random() - 0.5) * 1e-6;
                        }
                    } catch(e) {}
                    return arr;
                };
            } catch(e) {}
        })();
        """




    js='''
document.querySelector('settings-ui').shadowRoot

  .querySelector('#main').shadowRoot.querySelector('#switcher').querySelector('settings-search-page-index').shadowRoot.querySelector('cr-view-manager').querySelector('settings-search-page').shadowRoot.querySelector('settings-section').querySelector('div').querySelector('.cr-row.first').querySelector('.default-search-engine').querySelector('.cr-row').querySelector('#openDialogButton').click();'''
    eng='''document.querySelector('settings-ui').shadowRoot.querySelector('#main').shadowRoot.querySelector('#switcher').querySelector('settings-search-page-index').shadowRoot.querySelector('cr-view-manager').querySelector('settings-search-page').shadowRoot.querySelector('settings-section').querySelector('div').querySelector('.cr-row.first').querySelector('settings-search-engine-list-dialog').shadowRoot.querySelector('cr-dialog').querySelector('.dialog-body').querySelector('cr-radio-group').querySelector('[name="5"]').click();'''   
    setter='''document.querySelector('settings-ui').shadowRoot.querySelector('#main').shadowRoot.querySelector('#switcher').querySelector('settings-search-page-index').shadowRoot.querySelector('cr-view-manager').querySelector('settings-search-page').shadowRoot.querySelector('settings-section').querySelector('div').querySelector('.cr-row.first').querySelector('settings-search-engine-list-dialog').shadowRoot.querySelector('cr-dialog').querySelector('[slot="button-container"]').querySelector('#setAsDefaultButton').click();
'''
    driver.execute_script(js)
    driver.execute_script(eng)
    driver.execute_script(setter)
    # # driver.get("chrome://newtab")
    driver.get("https://duckduckgo.com/")
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": STEALTH_JS})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"Accept-Language": "en-US,en;q=0.9"}})
    driver.execute_cdp_cmd("Network.clearBrowserCache", {})
    driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
    
        
    def clean_session(driver):
            try:
                driver.delete_all_cookies()
                driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear(); indexedDB.databases().then(dbs => dbs.forEach(db => indexedDB.deleteDatabase(db.name)));")
                print("session cleared")
            except Exception:
                pass
    clean_session()
    


    print(driver.title)


if __name__ == "__main__":
    
    sel(None,None,None)
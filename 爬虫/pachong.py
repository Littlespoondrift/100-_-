from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import time

# ======================
# 1. 初始化
# ======================
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

driver.get("https://www.cnki.net/")

print("请手动登录CNKI（20秒）")
time.sleep(20)

# ======================
# 2. 搜索关键词
# ======================
keyword = "智能交通"

search = wait.until(
    EC.presence_of_element_located((By.ID, "txt_SearchText"))
)
search.clear()
search.send_keys(keyword)
search.send_keys(Keys.ENTER)

time.sleep(5)

# ======================
# 3. Excel初始化
# ======================
wb = Workbook()
ws = wb.active
ws.title = "CNKI数据"

ws.append(["标题", "摘要"])

data_count = 0

# ======================
# 4. 开始爬取
# ======================
for page in range(3):   # ← 这里控制页数
    print(f"正在爬第 {page+1} 页")

    titles = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fz14"))
    )

    for i in range(len(titles)):
        try:
            titles = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fz14"))
            )

            title_elem = titles[i]
            title_text = title_elem.text

            # 点击进入详情页
            driver.execute_script("arguments[0].click();", title_elem)
            driver.switch_to.window(driver.window_handles[-1])

            abstract_text = ""

            try:
                abs_elem = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "abstract-text"))
                )
                abstract_text = abs_elem.text
            except:
                abstract_text = "无摘要"

            print(f"{data_count+1} - {title_text}")

            ws.append([title_text, abstract_text])
            data_count += 1

            # 关闭详情页
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print("出错：", e)

            # 保证窗口不乱
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
            continue

    # 下一页
    try:
        next_btn = driver.find_element(By.LINK_TEXT, "下一页")
        next_btn.click()
        time.sleep(3)
    except:
        break

# ======================
# 5. 保存Excel
# ======================
file_name = "智能交通_摘要数据.xlsx"
wb.save(file_name)

driver.quit()

print(f"完成！已保存：{file_name}")
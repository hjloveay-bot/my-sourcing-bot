import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import datetime

async def scrape_coupang():
    async with async_playwright() as p:
        # 1. 브라우저 실행 (차단 방지를 위한 인자 추가)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        # 2. 쿠팡 카테고리 접속 (주방용품)
        url = "https://www.coupang.com/np/categories/185669"
        print(f"[{datetime.datetime.now()}] 쿠팡 접속 시도 중...")
        
        try:
            # 60초 대기 (네트워크 상황 고려)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) 

            # 3. 데이터 추출 (더 유연한 선택자 사용)
            items = await page.query_selector_all("li.category-product-item")
            print(f"찾은 상품 수: {len(items)}개")

            data = []
            for item in items[:30]:
                try:
                    name_el = await item.query_selector(".name")
                    price_el = await item.query_selector(".price-value")
                    
                    if name_el and price_el:
                        name = (await name_el.inner_text()).strip()
                        price = (await price_el.inner_text()).replace(",", "").strip()
                        data.append({
                            "상품명": name,
                            "가격": price,
                            "수집일": datetime.datetime.now().strftime("%Y-%m-%d")
                        })
                except:
                    continue

            # 4. 결과 저장
            if data:
                df = pd.DataFrame(data)
                df.to_csv("coupang_items.csv", index=False, encoding="utf-8-sig")
                print(f"🎉 성공: {len(data)}개의 아이템을 수집하여 저장했습니다.")
            else:
                print("⚠️ 데이터를 찾지 못했습니다. 쿠팡 구조가 바뀌었을 수 있습니다.")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_coupang())

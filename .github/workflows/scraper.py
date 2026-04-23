import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import pandas as pd
import datetime

async def scrape_coupang():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 차단 방지를 위한 설정 강화
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # [핵심] 스텔스 모드 실제 적용
        await stealth_async(page)
        
        # 쿠팡 주방용품 카테고리
        url = "https://www.coupang.com/np/categories/185669" 
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) # 사람처럼 기다리기

            items = await page.query_selector_all(".category-product-item")
            data = []

            for item in items[:30]: # 안정성을 위해 우선 30개만
                name = await item.query_selector(".name")
                price = await item.query_selector(".price-value")
                
                if name and price:
                    data.append({
                        "상품명": (await name.inner_text()).strip(),
                        "가격": (await price.inner_text()).replace(",", ""),
                        "수집일": datetime.datetime.now().strftime("%Y-%m-%d")
                    })

            if data:
                df = pd.DataFrame(data)
                df.to_csv("coupang_items.csv", index=False, encoding="utf-8-sig")
                print(f"성공: {len(data)}개의 상품을 수집했습니다.")
            else:
                print("데이터를 찾지 못했습니다. 구조가 변경되었을 수 있습니다.")

        except Exception as e:
            print(f"에러 발생: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_coupang())

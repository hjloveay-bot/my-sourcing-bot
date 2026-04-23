import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import pandas as pd
import datetime
import os

async def scrape_coupang():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        # 주방용품 카테고리
        url = "https://www.coupang.com/np/categories/185669" 
        print(f"접속 시도 중: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5) 

            # 상품 리스트 찾기 (클래스명이 변경되었을 경우를 대비)
            items = await page.query_selector_all("li.category-product-item")
            print(f"찾은 상품 수: {len(items)}개")

            data = []
            for item in items[:30]:
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

            if data:
                df = pd.DataFrame(data)
                df.to_csv("coupang_items.csv", index=False, encoding="utf-8-sig")
                print("데이터 저장 성공: coupang_items.csv")
            else:
                print("데이터를 추출하지 못했습니다. 쿠팡이 화면 구조를 바꿨거나 차단했을 수 있습니다.")

        except Exception as e:
            print(f"실행 중 에러 발생: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_coupang())

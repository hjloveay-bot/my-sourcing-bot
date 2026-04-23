import asyncio
from playwright.async_api import async_playwright
from python_stealth import stealth_async
import pandas as pd
import datetime

async def scrape_coupang():
    async with async_playwright() as p:
        # 브라우저 실행 (차단 방지를 위해 Stealth 모드 적용)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 쿠팡 주방용품 베스트 카테고리 예시
        url = "https://www.coupang.com/np/categories/185669" 
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # 데이터 추출 로직
        items = await page.query_selector_all(".category-product-item")
        data = []

        for item in items[:50]: # 상위 50개만
            try:
                name = await item.query_selector(".name")
                price = await item.query_selector(".price-value")
                rating = await item.query_selector(".rating")
                reviews = await item.query_selector(".rating-total-count")
                
                data.append({
                    "상품명": await name.inner_text() if name else "N/A",
                    "가격": await price.inner_text() if price else "0",
                    "별점": await rating.inner_text() if rating else "0",
                    "리뷰수": await reviews.inner_text() if reviews else "(0)",
                    "수집일": datetime.datetime.now().strftime("%Y-%m-%d")
                })
            except Exception as e:
                continue

        # CSV 저장
        df = pd.DataFrame(data)
        df.to_csv("coupang_items.csv", index=False, encoding="utf-8-sig")
        print("수집 완료: coupang_items.csv 저장됨")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_coupang())

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import datetime

async def scrape_coupang():
    async with async_playwright() as p:
        # 브라우저 설정을 더 '사람'처럼 강화
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # 쿠팡 주방용품 카테고리
        url = "https://www.coupang.com/np/categories/185669"
        print(f"[{datetime.datetime.now()}] 쿠팡 서버에 접속 시도...")

        try:
            # 접속 시 헤더 추가 (쿠팡의 보안 통과용)
            await page.set_extra_http_headers({
                "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/"
            })
            
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 페이지 제목 출력 (차단 여부 확인용)
            title = await page.title()
            print(f"페이지 제목: {title}")
            
            # 사람이 읽는 것처럼 천천히 스크롤 (데이터 로딩 유도)
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(3)

            # 상품 리스트 찾기 (더 유연한 선택자들로 시도)
            items = await page.query_selector_all("li[class*='product-item'], .category-product-item, #productList li")
            print(f"검색된 상품 후보군: {len(items)}개")

            data = []
            for item in items[:30]:
                # 이름과 가격을 더 넓은 범위에서 찾음
                name_el = await item.query_selector(".name, .title, [class*='name']")
                price_el = await item.query_selector(".price-value, [class*='price']")
                
                if name_el:
                    name = (await name_el.inner_text()).strip()
                    # 가격이 없으면 '품절'이나 '확인불가'로 처리해서라도 데이터를 가져옴
                    price = (await price_el.inner_text()).replace(",", "").strip() if price_el else "0"
                    
                    data.append({
                        "상품명": name,
                        "가격": price,
                        "수집일": datetime.datetime.now().strftime("%Y-%m-%d")
                    })

            if data:
                df = pd.DataFrame(data)
                df.to_csv("coupang_items.csv", index=False, encoding="utf-8-sig")
                print(f"✅ 성공: {len(data)}개의 아이템을 수집했습니다.")
            else:
                print("❌ 여전히 데이터를 찾지 못했습니다. 쿠팡이 접속을 강력히 차단 중입니다.")

        except Exception as e:
            print(f"❌ 실행 에러: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_coupang())

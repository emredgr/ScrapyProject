from scrapy import Spider, Request, Selector
from scrapy.http import HtmlResponse

class ZingatSpider(Spider):
    name = 'zingat'
    allowed_domains = ['www.zingat.com']

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        # "USER_AGENT": 'zingat_crawler (+http://www.yourdomain.com)',
    }
    modes_and_xpaths: dict = {"office_name": ".//a[@class='zo-card-name-link']/@title",
                              "office_detail_url": ".//figure[@class='zo-card-image']/a/@href",
                              "location": ".//div[@class='zo-card-location']/text()",
                              "Sales": ".//div[@class='zo-card-metrics']/a[1]/span[@class='metric-value']/text()",
                              "Rent": "//div[@class='zo-card-metrics']/a[2]/span[@class='metric-value']/text()",
                              "Phone_Number": ".//div[@class='zoc-phone-label']//text()"}

    pagination_counter = 1
    total_page_count = 0
    def start_requests(self):
        yield Request(url="https://www.zingat.com/en/real-estate-offices",
                      callback=self.getOfficeInformations,
                      method="GET")

    def getOfficeInformations(self, response:HtmlResponse)->dict:
        scraped_data:dict = {}
        if self.pagination_counter == 1:
            self.total_page_count = response.xpath("//nav[@class='zng-pagination']/@data-total").get()
            if self.total_page_count is not None:
                self.total_page_count = int(self.total_page_count)
        self.pagination_counter += 1

        office_cards = response.xpath("//section[@class='item-list']//ul/div")
        output_columns = ["office_name","office_detail_url","location","Sales","Rent","Phone Number"]

        for each_card in office_cards:
            for col in self.modes_and_xpaths.keys():
                scraped_data[col] = self.getInformations(each_card,col)
            yield scraped_data

        # recursive situation created
        next_page_url = f"https://www.zingat.com/en/real-estate-offices?page={self.pagination_counter}"

        if self.pagination_counter <= self.total_page_count:
            yield Request(next_page_url, callback=self.getOfficeInformations, method="GET")
        else:
            print("Last page scraping...")

    def getInformations(self,office_card:Selector,mode:str)->str:

        item = office_card.xpath(self.modes_and_xpaths[mode]).get()

        if item is not None:
            item = item.strip()
        else:
            item = ""
        if mode == "office_detail_url":
            item = "https://www.zingat.com/"+item

        return item





    def parse(self, response):
        pass

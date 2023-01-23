from selenium import webdriver
from selenium.webdriver.common.by import By

from config import OLX_URL


class OLXParser:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def _parse_detailed_page(self, apartment_url: str) -> tuple:
        self.driver.get(apartment_url)

        info_elements = [
            element.text
            for element in self.driver.find_elements(By.CLASS_NAME, "css-b5m1rv")
        ]

        name = self.driver.find_element(By.CLASS_NAME, "css-1soizd2").text
        price = self.driver.find_element(By.CLASS_NAME, "css-dcwlyx").text.split("\n")[0]

        apartment_floor = [element for element in info_elements if element.startswith("Поверх:")]
        apartment_floor = apartment_floor[0].split(": ")[-1]
        number_of_floors = [element for element in info_elements if element.startswith("Поверховість:")]
        number_of_floors = number_of_floors[0].split(": ")[-1]

        floor = f"{apartment_floor} of {number_of_floors}"

        area = [
            element
            for element in info_elements
            if element.startswith("Загальна площа:")
        ]
        area = area[0].split(": ")[-1]

        location_city = self.driver.find_element(By.CLASS_NAME, "css-1cju8pu").text
        location_region = info_elements[-1]
        location = location_city + location_region

        return name, price, floor, area, location

    def _parse_apartments_page(self, page_link: str) -> list[tuple]:
        self.driver.get(page_link)
        output_data_from_page = []

        link_elements = self.driver.find_elements(By.CLASS_NAME, "css-rc5s2u")
        links = [element.get_attribute("href") for element in link_elements]

        for link in links:
            apartment_data = self._parse_detailed_page(link)
            output_data_from_page.append(apartment_data)

        return output_data_from_page

    def parse_pages(self, number_of_pages: int) -> list[tuple]:
        assert number_of_pages > 0, "Number of pages should be 1 or more"

        self.driver.get(OLX_URL)

        data_from_pages = []

        for i in range(1, number_of_pages + 1):
            page_url = OLX_URL + "?page=" + str(i)
            data_from_page = self._parse_apartments_page(page_url)
            data_from_pages.extend(data_from_page)

        return data_from_pages

    def __del__(self):
        self.driver.quit()

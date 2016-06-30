#from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import unittest

class NewVisitorTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
        super().setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)
		
    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
		
        self.browser.get(self.server_url)
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('작업', header_text)
		
		
        # 그녀는 바로 작업을 추가하기로 한다
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
	        inputbox.get_attribute('placeholder'),
	        '작업 아이템 입력'
        )
        # "공작깃털 사기" 라고 텍스트 상자에 입력한다
        # (에디스의 취미는 날치 잡이용 그물을 만드는 것이다)
        inputbox.send_keys('공작깃털 사기')
		
        # 엔터키를 치면 페이지가 갱신되고 작업 목록에
        # "1: 공작깃털 사기" 아이템이 추가된다
        inputbox.send_keys(Keys.ENTER)
		
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: 공작깃털 사기')
		
		# 추가 아이템을 입력할 수 있는 여분의 텍스트 상자가 존재한다
		# 다시 "공작깃털을 이용해서 그물 만들기"라고 입력한다
		
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('공작깃털을 이용해서 그물 만들기')
        inputbox.send_keys(Keys.ENTER)

        # 페이지는 다시 갱신되고, 두 개 아이템이 목록에 보인다
        self.check_for_row_in_list_table('2: 공작깃털을 이용해서 그물 만들기')
        self.check_for_row_in_list_table('1: 공작깃털 사기')
		
        #######################################
        # 새로운 사용자인 프란시스가 사이트에 접속한다
		
        # 새로운 브라우저 세션을 이용하여 에디스의 정보가 쿠키를 통해 유입되는것을 방지함
        self.browser.quit()
        self.browser = webdriver.Chrome()
        #self.browser.implicitly_wait( 3 )
        # 프란시스가 홈페이지에 접속한다. 에디스의 리스트는 안보인다
        self.browser.get(self.server_url)
        #page_text = self.browser.find_element_by_tag_name('table').text
        #self.assertIn('공작깃털', page_text)
        #self.browser.find_element_by_tag_name('table')
		
        # 프란시스가 새로운 작업 아이템을 입력한다
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('우유 사기')
        inputbox.send_keys(Keys.ENTER)
		
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/(\d+)')
        self.assertNotEqual(francis_list_url, edith_list_url)
		
        # 에디스가 입력한 흔적이 없다는 것을 다시 확인한다
        self.assertNotIn('공작깃털', self.browser.find_element_by_tag_name('table').text)
		
        # 둘 다 만족하고 잠자리에 든다
        self.fail('Finish the test!')
		
    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_layout_and_style(self):
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024,768)

        inputbox = self.browser.find_element_by_tag_name('input')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] /2, 512, delta=10)
		
if __name__ == '__main__':
    unittest.main(warnings='ignore')

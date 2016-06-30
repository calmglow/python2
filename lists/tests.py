from django.test import TestCase
from django.core.urlresolvers import resolve
from lists.views import home_page, view_list
from lists.models import Item, List
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.models import List, Item
class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % (list_.id,))
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text ='a item', list = correct_list)
        Item.objects.create(text = 'b item', list = correct_list)
        other_list = List.objects.create()
        Item.objects.create(text = 'c item', list = other_list)
        Item.objects.create(text = 'd item', list = other_list)

        response = self.client.get('/lists/%d/' % (correct_list.id,))

        self.assertContains(response, 'a item')
        self.assertContains(response, 'b item')
        self.assertNotContains(response, 'c item')
        
        
    def test_display_all_items(self):
        list_ = List.objects.create()
        Item.objects.create(text='a item', list=list_)
        Item.objects.create(text='b item', list=list_)
		# request = HttpRequest()
		# response = home_page(request)
        response = self.client.get('/lists/%d/' % (list_.id,))
        
        self.assertIn('a item', response.content.decode())
        self.assertIn('b item', response.content.decode())

    def test_correct_list_to_template(self):
        correct_list = List.objects.create()
        other_list = List.objects.create()
        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertEqual(response.context['list'], correct_list)
        

class HomepageTest(TestCase):
    def test_root_to_resolve_homepage(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)
        
    def test_homepage_return_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('home.html', request=request)
        self.assertEqual(response.content.decode(), expected_html)
        #self.assertIn(b'<title>To-Do Lists</title>', response.content)
        #self.assertTrue(response.content.strip().endswith(b'</html>'))

class NewListTest(TestCase):
    def test_saving_a_POST(self):
        self.client.post('/lists/new', data={'item_text': '신규 작업 아이템'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '신규 작업 아이템')

    def test_redirects_after_POST(self):
        response  = self.client.post('/lists/new', data={'item_text': '신규 작업 아이템'})
        #self.assertEqual(response.status_code, 302)
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % (new_list.id,))


class ListAndItemModelsTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text= "첫번째 아이템"
        first_item.list = list_
        first_item.save()
        
        second_item = Item()
        second_item.text = "두번째 아이템"
        second_item.list = list_
        second_item.save()
        
        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)
        
        first_item_saved = saved_items[0]
        second_item_saved = saved_items[1]
        self.assertEqual(first_item_saved.text, "첫번째 아이템")
        self.assertEqual(first_item_saved.list, list_)
        self.assertEqual(second_item_saved.text, "두번째 아이템")
        self.assertEqual(second_item_saved.list, list_)

class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/%d/add_item' % (correct_list.id,),
            data = {'item_text': '기존 목록에 신규 아이템'}
            )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '기존 목록에 신규 아이템')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/%d/add_item' % (correct_list.id,),
            data = {'item_text': '기존 목록에 신규 아이템'}
            )
        self.assertRedirects(response,'/lists/%d/' % (correct_list.id,))

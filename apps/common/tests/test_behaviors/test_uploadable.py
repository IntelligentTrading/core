import json

from .test_mixins import BehaviorTestCaseMixin


class UploadableTest(BehaviorTestCaseMixin):
    def test_should_return_type_when_get_file_type_property(self):
        meta_data = json.dumps({'type': 'image'})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.file_type, 'image')

    def test_should_return_empty_string_when_get_file_type_but_not_have_one(
            self):
        meta_data = json.dumps({})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.file_type, '')

    def test_should_return_name_when_get_name_property(self):
        meta_data = json.dumps({'name': 'myphoto.jpg'})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.name, 'myphoto.jpg')

    def test_should_return_empty_string_when_get_name_but_not_have_one(self):
        meta_data = json.dumps({})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.name, '')

    def test_should_return_file_ext_when_get_fileextension_property(self):
        meta_data = json.dumps({'ext': 'jpg'})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.file_extension, 'jpg')

    def test_should_return_empty_str_when_get_file_extension_but_no_have_one(
            self):
        meta_data = json.dumps({})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.file_extension, '')

    def test_return_name_when_get_link_title_if_have_name_etc_and_type(self):
        meta_data = json.dumps({
            'name': 'myphoto.jpg',
            'etc': 'etc',
            'type': 'image'
        })
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.link_title, 'myphoto.jpg')

    def test_return_etc_when_get_link_title_if_have_only_etc_ane_type_data(
            self):
        meta_data = json.dumps({'etc': 'etc', 'type': 'image'})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.link_title, 'ETC')

    def test_return_type_when_get_link_title_if_have_only_type_data(self):
        meta_data = json.dumps({'type': 'image'})
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.link_title, 'IMAGE')

    def test_return_ext_concad_with_title_if_have_ext_in_meta_data(self):
        meta_data = json.dumps({
            'name': 'myphoto.jpg',
            'etc': 'etc',
            'type': 'image',
            'ext': 'jpg'
        })
        obj = self.create_instance(meta_data=meta_data)
        self.assertEqual(obj.link_title, 'myphoto.jpg .JPG')

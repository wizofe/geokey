from django.test import TestCase

from geokey.contributions.models import (
    ImageFile, VideoFile,
    post_save_media_file_update
)
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.users.tests.model_factories import UserF

from .model_factories import get_image


class TestImageFilePostSave(TestCase):
    def test_post_image_file_save(self):
        observation = ObservationFactory()
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserF.create(),
            image=get_image()
        )
        ImageFile.objects.create(
            status='deleted',
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserF.create(),
            image=get_image()
        )

        post_save_media_file_update(ImageFile, instance=image_file)
        self.assertEqual(image_file.contribution.num_media, 1)
        self.assertEqual(image_file.contribution.num_comments, 0)


class ImageFileTest(TestCase):
    def test_get_type_name(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            image=get_image()
        )
        self.assertEqual(image_file.type_name, 'ImageFile')

    def test_delete_file(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            image=get_image()
        )
        image_file.delete()
        self.assertEquals(image_file.status, 'deleted')


class TestVideoFilePostSave(TestCase):
    def test_post_image_file_save(self):
        observation = ObservationFactory()
        video_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserF.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        VideoFile.objects.create(
            status='deleted',
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserF.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )

        post_save_media_file_update(VideoFile, instance=video_file)
        self.assertEqual(video_file.contribution.num_media, 1)
        self.assertEqual(video_file.contribution.num_comments, 0)


class VideoFileTest(TestCase):
    def test_get_type_name(self):
        video_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserF.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        self.assertEqual(video_file.type_name, 'VideoFile')

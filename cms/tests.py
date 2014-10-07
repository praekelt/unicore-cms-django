from django.test import TestCase
from django.core.management import call_command

from cms.models import Post, Category
from cms.git.models import GitPage, GitCategory
from cms import utils


class PostTestCase(TestCase):

    def clean_repo(self):
        for p in GitPage.all():
            GitPage.delete(p.uuid, True)
        for c in GitCategory.all():
            GitCategory.delete(c.uuid, True)

    def setUp(self):
        self.clean_repo()

    def tearDown(self):
        self.clean_repo()

    def create_categories(
            self, names=[u'Diarrhoea', u'Hygiene'], locale='eng_UK',
            featured_in_navbar=False):
        categories = []
        for name in names:
            category = GitCategory(title=name, language=locale)
            category.featured_in_navbar = featured_in_navbar
            category.slug = category.slugify(name)
            category.save(True, message=u'added %s Category' % (name,))
            categories.append(GitCategory.get(category.uuid))

        return categories

    def create_pages(self, count=2, locale='eng_UK'):
        pages = []
        for i in range(count):
            page = GitPage(
                title=u'Test Page %s' % (i,),
                content=u'this is sample content for pg %s' % (i,),
                language=locale)
            page.save(True, message=u'added page %s' % (i,))
            pages.append(GitPage.get(page.uuid))

        return pages

    def test_create_post(self):
        p = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content')
        p.save()
        self.assertEquals(p.featured_in_category, False)
        self.assertEquals(Post.objects.all().count(), 1)
        self.assertEquals(len(list(GitPage.all())), 1)

        p = Post.objects.get(pk=p.pk)
        p.title = 'changed title'
        p.save()

        self.assertEquals(len(list(GitPage.all())), 1)
        git_page = GitPage.all()[0]
        self.assertEquals(git_page.title, 'changed title')
        self.assertEquals(git_page.uuid, p.uuid)
        self.assertEquals(git_page.subtitle, 'subtitle')
        self.assertEquals(git_page.description, 'description')
        self.assertEquals(git_page.featured_in_category, False)
        self.assertTrue(git_page.created_at is not None)
        self.assertTrue(git_page.modified_at is not None)

        p.delete()
        self.assertEquals(Post.objects.all().count(), 0)
        self.assertEquals(len(list(GitPage.all())), 0)

    def test_create_category(self):
        c = Category(
            title='sample title',
            subtitle='subtitle',
            slug='sample-title')
        c.save()
        self.assertEquals(Category.objects.all().count(), 1)
        self.assertEquals(len(list(GitCategory.all())), 1)

        c = Category.objects.get(pk=c.pk)
        c.title = 'changed title'
        c.save()

        self.assertEquals(len(list(GitCategory.all())), 1)
        git_cat = GitCategory.all()[0]
        self.assertEquals(git_cat.title, 'changed title')
        self.assertEquals(git_cat.uuid, c.uuid)
        self.assertEquals(git_cat.subtitle, 'subtitle')

        c.delete()
        self.assertEquals(Category.objects.all().count(), 0)
        self.assertEquals(len(list(GitCategory.all())), 0)

    def test_page_with_primary_category(self):
        c = Category(
            title='guides',
            slug='guides')
        c.save()
        c = Category.objects.get(pk=c.pk)

        p = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content')
        p.primary_category = c
        p.save()

        p = Post.objects.get(pk=p.pk)

        git_p = GitPage.get(p.uuid)
        self.assertEquals(git_p.primary_category.slug, 'guides')

    def test_page_recreated_if_not_in_git(self):
        p = Post(
            title='sample test title',
            description='description',
            subtitle='subtitle',
            content='sample content')
        p.save()
        p = Post.objects.get(pk=p.pk)
        GitPage.delete(p.uuid, True)
        utils.sync_repo()

        p.title = 'new title'
        p.save()

        p = Post.objects.get(pk=p.pk)
        git_p = GitPage.get(p.uuid)

        self.assertEquals(git_p.title, 'new title')

    def test_category_recreated_if_not_in_git(self):
        c = Category(
            title='sample test title',
            slug='slug')
        c.save()
        c = Category.objects.get(pk=c.pk)
        GitCategory.delete(c.uuid, True)
        utils.sync_repo()

        c.title = 'new title'
        c.save()

        c = Category.objects.get(pk=c.pk)
        git_c = GitCategory.get(c.uuid)

        self.assertEquals(git_c.title, 'new title')

    def test_page_with_source(self):
        c = Category(
            title='guides',
            slug='guides')
        c.save()
        c = Category.objects.get(pk=c.pk)

        p = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content',
            language='eng-UK')
        p.save()
        p = Post.objects.get(pk=p.pk)

        p2 = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content',
            language='eng-US')
        p2.primary_category = c
        p2.source = p
        p2.save()
        p2 = Post.objects.get(pk=p2.pk)

        git_p2 = GitPage.get(p2.uuid)
        self.assertEquals(git_p2.language, 'eng-US')
        self.assertEquals(git_p2.source.language, 'eng-UK')

    def test_page_featured_in_category(self):
        p = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content',
            language='eng-UK',
            featured_in_category=True)
        p.save()

        p = Post.objects.get(pk=p.pk)
        git_p = GitPage.get(p.uuid)
        self.assertTrue(git_p.featured_in_category)

    def test_page_get_featured(self):
        post = Post(
            title='sample title',
            description='description',
            subtitle='subtitle',
            content='sample content',
            language='eng-UK')
        post.save()

        featured_post = Post(
            title='featured sample title',
            description='featured description',
            subtitle='featured subtitle',
            content='featured sample content',
            language='eng-UK',
            featured=True)
        featured_post.save()

        post = Post.objects.get(pk=post.pk)
        git_post = GitPage.get(post.uuid)

        featured_post = Post.objects.get(pk=featured_post.pk)
        featured_git_post = GitPage.get(featured_post.uuid)

        self.assertEqual(post.featured, False)
        self.assertEquals(git_post.featured, False)

        self.assertEqual(featured_post.featured, True)
        self.assertEquals(featured_git_post.featured, True)

    def test_category_with_source(self):
        c = Category(
            title='sample title',
            subtitle='subtitle',
            language='afr-ZA')
        c.save()
        c2 = Category(
            title='sample title',
            subtitle='subtitle',
            language='eng-UK')
        c2.save()

        c = Category.objects.get(pk=c.pk)
        c2 = Category.objects.get(pk=c2.pk)
        c2.source = c
        c2.save()

        c = GitCategory.get(c.uuid)
        c2 = GitCategory.get(c2.uuid)
        self.assertEquals(c2.language, 'eng-UK')
        self.assertEquals(c2.source.language, 'afr-ZA')

    def test_category_with_featured_in_navbar(self):
        c = Category(
            title='sample title',
            subtitle='subtitle',
            language='afr-ZA',
            featured_in_navbar=True)
        c.save()

        c = Category.objects.get(pk=c.pk)
        git_c = GitCategory.get(c.uuid)
        self.assertTrue(git_c.featured_in_navbar)

    def test_import_from_git_command(self):
        cat1, cat2 = self.create_categories()
        cat1.source = cat2
        cat1.save(True, message='Added source to category.')
        pages = self.create_pages(count=10)

        for page in pages[:8]:
            page.primary_category = cat1
            page.save(True, message='Added category.')

        page0 = pages[0]
        page0.linked_pages = [pages[1].uuid, pages[2].uuid, pages[3].uuid]
        page0.source = pages[4]
        page0.save(True, message='Added related fields.')

        self.assertEquals(Category.objects.all().count(), 0)
        self.assertEquals(Post.objects.all().count(), 0)
        call_command('import_from_git', quiet=True)

        self.assertEquals(Category.objects.all().count(), 2)
        self.assertEquals(Post.objects.all().count(), 10)

        c = Category.objects.get(uuid=cat1.uuid)
        self.assertEquals(c.source.uuid, cat2.uuid)

        p = Post.objects.get(uuid=page0.uuid)
        self.assertEquals(p.related_posts.count(), 3)
        self.assertEquals(p.primary_category.uuid, cat1.uuid)
        self.assertEquals(p.source.uuid, pages[4].uuid)

from abc import abstractmethod
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
import fregat.utils
import hashlib
from io import BytesIO, StringIO
import json
from markdown import markdown
from PIL import Image
import random
from urllib.request import urlopen


class Pricelist(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название прайслиста',
        help_text='Используется только в админке.'

    )
    is_default = models.BooleanField(
        db_index=True,
        blank=True,
        default=False,
        verbose_name='Прайс-лист по умолчанию',
        help_text='''
            <p>
                Эта настройка необходима для быстрого создания позиций
                прайсл-листов.
            </p>
            <p>
                При создании позиции прайс-листа необходимо выбрать к
                какому прайс-листу она относится. Однако если имеется
                прайс-лист по умолчанию, то это поле можно оставлять
                пустым, будет использован прайс-лист по умолчанию.
            </p>
            <p>
                В других механиках это поле не используется.
            </p>
        '''
    )
    PRICELIST_VIEWS = [
        ('grid', 'Таблица'),
        ('tile', 'Плитка'),
    ]
    view = models.CharField(
        max_length=8,
        choices=PRICELIST_VIEWS,
        default='grid',
        verbose_name='Вид прайслиста'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменен')

    class Meta:
        verbose_name = 'Прайслист'
        verbose_name_plural = 'Прайслисты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Pricelist, self).save(*args, **kwargs)
        if self.is_default:
            Pricelist.objects.all().exclude(pk=self.pk).update(
                is_default=False
            )


class PageMixin(models.Model):
    is_published = models.BooleanField(
        blank=True,
        default=True,
        db_index=True,
        verbose_name='Опубликован',
        help_text='''
            Если флажок снят, то материал не будет присутствовать на сайте.
        '''
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    heading = models.CharField(max_length=512, verbose_name='Заголовок')
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='Ключ ЧПУ'
    )
    content = models.TextField(
        blank=True,
        default='',
        verbose_name='Основное содержимое'
    )
    pricelist = models.ForeignKey(
        Pricelist,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Прайслист',
        help_text='''
            Это поле добавляет после основного содержимого страницы выбранный
            прайслист.
        '''
    )
    title = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name='Title',
        help_text='''
            <p>
                Подставляется в качестве переменной __V__ в общий шаблон
                метатега title страницы.
            </p>
            <p>
                Если значение не задано, то в шаблон подставляется
                заголовок страницы.
            </p>
        '''
    )
    keywords = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name='Keywords',
        help_text='''
            <p>
                Подставляется в качестве переменной __V__ в общий шаблон
                метатега keywords страницы.
            </p>
            <p>
                Если значение не задано, то в шаблон подставляется
                заголовок страницы.
            </p>
        '''
    )
    description = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name='Description',
        help_text='''
            <p>
                Подставляется в качестве переменной __V__ в общий шаблон
                метатега description страницы.
            </p>
            <p>
                Если значение не задано, то в шаблон подставляется
                заголовок страницы.
            </p>
        '''
    )
    use_metatags_as_is = models.BooleanField(
        default=False,
        blank=True,
        verbose_name='Отключить шаблонизацию метатегов',
        help_text='''
            <p>
                Если флажок установлен, то в качестве метатегов для данной
                страницы будут использованы значения соответствующих полей,
                а при их отсутствии будет использован заголовок страницы.
            </p>
            <p>
                Если же флажок снят, то в метатегах будет результат
                шаблонизации (шаблон создается в настройках сайта), куда
                в качестве переменных будут переданы значения соответствующих
                полей.
            </p>
        '''
    )
    class Meta:
        abstract = True

    def __str__(self):
        return self.heading

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug' : self.slug})

    def clean(self):
        if not self.pricelist and not self.content:
            raise ValidationError({
                'content': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Основное содержимое" или "Прайслист"
                ''',
                'pricelist': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Основное содержимое" или "Прайслист"
                '''
            })

    def set_slug(self, source):
        if not self.slug:
            slug = fregat.utils.transliterate(source)
            is_unique = False

            while not is_unique:
                is_unique = self.__class__.objects.filter(
                    slug=slug).count() == 0

                if is_unique:
                    self.slug = slug
                else:
                    slug = fregat.utils.transliterate(
                        '%s-%s' % (source, random.randint(1000, 9999))
                    )

    @property
    def html_content(self):
        content = getattr(
            self,
            '__html_content',
            ''.join(markdown(self.content).splitlines())
        )
        setattr(self, '__html_content', content)
        return content or ''

    @property
    def without_media_header(self):
        len(self.html_content) < 20

    def save(self, *args, **kwargs):
        self.set_slug(source=self.heading)
        super(PageMixin, self).save(*args, **kwargs)


class OrderMixin(models.Model):
    order_no = models.IntegerField(
        blank=True,
        default=500,
        db_index=True,
        verbose_name="Порядок сортировки",
        help_text='''
            <p>
                Сортировка элементов идет от меньшего числа к большему.
                100, 200, 300, 400 и т.д.
            </p>
            <p>
                По умолчанию значение сортировки равно 500.
            </p>
        '''
    )

    class Meta:
        abstract = True


class ThumbnailProcessor():
    @property
    @abstractmethod
    def image_field_for_thumb(self):
        pass

    def _resize_image(self, origin, ratio):
        desired_size = (
            round(origin.size[0] * ratio),
            round(origin.size[1] * ratio)
        )

        return origin.resize(desired_size, Image.ANTIALIAS)

    def _get_resized_image_url(self, desired_height=None,
                               desired_width=None, desired_max_side=None):
        if not self.image_field_for_thumb.name:
            return None

        desired_height = desired_height
        desired_width = desired_width
        desired_max_side = desired_max_side

        prefix = '%s%s%s' % (
            '%s' % ('h' + str(desired_height)) if desired_height else '',
            '%s' % ('w' + str(desired_width)) if desired_width else '',
            '%s' % ('s' + str(desired_max_side)) if desired_max_side else '',
        ) or 'p'

        origin_path = settings.MEDIA_ROOT.joinpath(self.image_field_for_thumb.name)
        file_name = '%s-%s%s' % (prefix, origin_path.stem, '.jpg')
        result_path = origin_path.parent.joinpath(file_name)

        if not result_path.is_file():
            origin = Image.open(self.image_field_for_thumb)
            origin = origin.convert(mode='RGB')
            width, height = origin.size[0], origin.size[1]

            result = origin
            if desired_height:
                ratio = desired_height / height
                result = self._resize_image(origin, ratio)
            elif desired_width:
                ratio = desired_width / width
                result = self._resize_image(origin, ratio)
            elif desired_max_side:
                if width > desired_max_side or height > desired_max_side:
                    ratio = desired_max_side / max(width, height)
                else:
                    ratio = 1

                result = self._resize_image(origin, ratio)

            result.save(result_path, **{
                'quality': 90,
                'optimize': True,
                'format': 'JPEG',
                'progressive': True,
            })

        return str(result_path).replace(
            str(settings.MEDIA_ROOT), settings.MEDIA_URL).replace('//', '/')


class PricelistCategory(OrderMixin):
    name = models.CharField(max_length=128, unique=True, verbose_name='Категория')

    class Meta:
        verbose_name = 'Категория прайслиста'
        verbose_name_plural = 'Категории прайслистов'
        ordering = ('order_no', 'pk', )

    def __str__(self):
        return self.name


class PriceItem(OrderMixin, ThumbnailProcessor):
    pricelist = models.ForeignKey(
        Pricelist,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Прайсл-лист',
        help_text='''
            <p>
                Если поле оставить пустым и в системе имеется прайс-лист
                по умолчанию, то именно он будет использован при сохранении.
            </p>
            <p>
                Если же прайс-листа по умолчанию нет, то это поле обязтельно
                для заполнения.
            </p>
        '''
    )
    category = models.ForeignKey(
        PricelistCategory,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        help_text='Например, "Напитки"'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название позиции',
        help_text='Например, "Аренда бильярда"'

    )
    common_price = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        help_text='''
            Если цена позиции одинакова во все дни, то нужно использовать
            это поле. В противном случае стоит использовать соответствующие
            поля.
        '''
    )
    price_on_weekdays = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена с ПН-ЧТ'
    )
    price_on_weekend = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена ПТ-ВС '
    )
    price_on_holydays = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена по праздникам'
    )
    unit = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Единица измерения'
    )
    image = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        blank=True,
        null=True,
        verbose_name='Фото',
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменен')

    class Meta:
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'
        ordering = ('category__order_no', 'order_no', 'pk', )

    def __str__(self):
        return self.name

    @property
    def image_field_for_thumb(self):
        return self.image

    @property
    def thumbnail(self):
        return self._get_resized_image_url(desired_width=350)

    @property
    def admin_thumbnail(self):
        return self._get_resized_image_url(desired_max_side=150)

    @property
    def has_detailed_price(self):
        prices = (
            self.price_on_weekdays,
            self.price_on_weekend,
            self.price_on_holydays,
        )
        return None not in prices and 0 not in prices

    @property
    def has_completed_price(self):
        return self.common_price or self.has_detailed_price

    def clean(self):
        default_pricelist = Pricelist.objects.filter(is_default=True).first()
        self.pricelist = self.pricelist or default_pricelist

        if not self.pricelist:
            raise ValidationError({
                'pricelist': '''
                    Вы должны выбрать прайс-лист или же
                    создать прайс-лист по умолчанию
                ''',
            })

        if not self.has_completed_price:
            raise ValidationError({
                'common_price': '''
                    Вы должны заполнить цену
                ''',
                'price_on_weekdays': '''
                    Вы должны заполнить цену
                ''',
                'price_on_weekend': '''
                    Вы должны заполнить цену
                ''',
                'price_on_holydays': '''
                    Вы должны заполнить цену
                ''',
            })

    @property
    def html_content(self):
        content = getattr(
            self,
            '__html_content',
            ''.join(markdown(self.text).splitlines())
        )
        setattr(self, '__html_content', content)
        return content

    def save(self, *args, **kwargs):
        super(PriceItem, self).save(*args, **kwargs)
        self.thumbnail


class Page(PageMixin):
    class Meta:
        verbose_name = "Страница сайта"
        verbose_name_plural = "Страницы сайта"


class MenuItem(OrderMixin):
    name = models.CharField(max_length=128, verbose_name='Пункт меню')
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Родительский пункт меню',
    )
    href = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name="URL ссылки",
        help_text='''
            <p>
                Если значение задано, то пункт меню будет ссылкой, указывающей
                на введенный URL.
            </p>
            <p>
                Этот параметр является взаимоисключающим с параметром
                "Страница сайта", но если заданы оба, то "URL ссылки"
                будет проигнорирован.
            </p>
            <p>
                Если же не задан ни один из параметров, то
                пункт меню не будет являться ссылкой (это может быть
                необходимо для группирующих разделов меню).
            </p>
        '''
    )
    page = models.ForeignKey(
        Page,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Страница сайта',
        help_text='''
            <p>
                Если значение задано, то пункт меню будет ссылкой, указывающей
                на выбранную страницу.
            </p>
            <p>
                Этот параметр является взаимоисключающим с параметром
                "URL ссылки", но если заданы оба, то "URL ссылки"
                будет проигнорирован.
            </p>
            <p>
                Если же не задан ни один из параметров, то
                пункт меню не будет являться ссылкой (это может быть
                необходимо для группирующих разделов меню).
            </p>
        '''
    )
    thread_id = models.ImageField(db_index=True, blank=True, null=True)
    is_child = models.IntegerField(db_index=True, blank=True, default=0)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ('thread_id', 'is_child', 'order_no', 'pk', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.parent is not None and self.parent.parent:
            self.parent = None
            self.thread_id = None
            self.is_child = 0

        if self.parent is not None:
            self.thread_id = self.parent.thread_id

        self.is_child = 1 if self.parent is not None else 0

        super(MenuItem, self).save(*args, **kwargs)

    @staticmethod
    def check_tree():
        '''
            Поля thread_id и is_child нужны только для логичной
            сортировки айтемов в админке по аналогии с MPTT.

            Метод check_tree валидирует эти поля и, если надо,
            инициирует их пересчет.

        '''
        MenuItem._limit_nesting()

        root = MenuItem.objects.filter(parent__isnull=True)
        current_root = root.order_by('thread_id')
        desired_root = root.order_by('order_no')

        can_refresh = False

        if (i.pk for i in desired_root) != (i.pk for i in current_root):
            can_refresh = True

        thread_ids = [r.thread_id for r in current_root]
        if None in thread_ids:
            can_refresh = True

        if len(thread_ids) != len(set(thread_ids)):
            can_refresh = True

        root_map = {r.pk: r.thread_id for r in current_root}

        root_child_status = set([r.is_child for r in current_root])
        if 0 not in root_child_status or len(root_child_status) != 1:
            can_refresh = True

        for child in MenuItem.objects.filter(parent_id__in=root_map.keys()):
            if child.thread_id != root_map.get(child.parent_id):
                can_refresh = True

            if child.is_child != 1:
                can_refresh = True

        if can_refresh:
            MenuItem._refresh_tree(desired_root=desired_root)

    @staticmethod
    def _limit_nesting():
        root = MenuItem.objects.filter(parent__isnull=True).only('pk')
        children = MenuItem.objects.filter(
            parent_id__in=[r.pk for r in root]
        ).only('pk')

        MenuItem.objects.all().exclude(
            pk__in=[r.pk for r in root] + [c.pk for c in children]
        ).update(
            parent=None, thread_id=None, is_child=0
        )

    @staticmethod
    def _refresh_tree(desired_root):
        thread_id_map = {}
        is_child_map = {}

        for child in MenuItem.objects.filter(parent__isnull=True):
            if child.parent_id not in thread_id_map:
                thread_id_map[child.parent_id] = []
            thread_id_map[child.parent_id].append(child.thread_id)

            if child.parent_id not in is_child_map:
                is_child_map[child.parent_id] = []
            is_child_map[child.parent_id].append(child.is_child)

        for thread_id, parent in enumerate(desired_root):
            can_update = False

            if thread_id != parent.thread_id:
                can_update = True

            children_thread_ids = set(thread_id_map.get(parent.pk, []))
            if children_thread_ids and thread_id not in children_thread_ids:
                can_update = True

            if len(children_thread_ids) > 1:
                can_update = True

            if parent.is_child != 0:
                can_update = True

            children_is_child = set(is_child_map.get(parent.pk, []))
            if children_is_child and 1 not in children_is_child:
                can_update = True

            if len(children_is_child) > 1:
                can_update = True

            if can_update:
                MenuItem.objects.filter(parent_id=parent.pk).update(
                    thread_id=thread_id,
                    is_child=1,
                )
                MenuItem.objects.filter(pk=parent.pk).update(
                    thread_id=thread_id,
                    is_child=0,
                )


class Settings(models.Model):
    is_active = models.BooleanField(
        blank=True,
        default=True,
        db_index=True,
        verbose_name='Активные настройки',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменен')
    phone = models.CharField(
        max_length=128,
        verbose_name='Телефон',
        help_text='''
            В человекопонятном виде. Используется в шапке сайта, подвале,
            мобильном меню и на странице контактов.
        '''
    )
    address = models.CharField(
        max_length=256,
        verbose_name='Адрес',
        help_text='''
            В человекопонятном виде. Используется в шапке сайта, подвале,
            мобильном меню и странице контактов.
        '''
    )
    latitude = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Широта',
        help_text='''
            Координаты можно взять в сервисе интерактивных карт.
            Учавствует в микроразметке, а также в построении контактов.
        '''
    )
    longitude = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Долгота',
        help_text='''
            Координаты можно взять в сервисе интерактивных карт.
            Учавствует в микроразметке, а также в построении контактов.
        '''
    )
    organization_name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Название организации',
        help_text='Название организации. Учавствует в микроразметке.',
    )
    organization_description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='Описание организации',
        help_text='Описание организации. Учавствует в микроразметке.',
    )
    postal_code = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name='Почтовый индекс',
        help_text='Учавствует в микроразметке.',
    )
    region = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Название региона или области',
        help_text='Учавствует в микроразметке.',
    )
    city = models.CharField(
        max_length=256,
        verbose_name='Город',
        blank=True,
        null=True,
        help_text='''
            Используется в шапке сайта, подвале,
            мобильном меню, на странице контактов, а также в микроразметке.
        '''
    )
    street_address = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Адрес в населенном пункте',
        help_text='Учавствует в микроразметке.',
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Адрес электронной почты',
        help_text='Учавствует в микроразметке.',
    )
    homepage_title_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Title',
        help_text='''
            Определяет метатег title для главной страницы.
        '''
    )
    homepage_keywords_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Keywords',
        help_text='''
            Определяет шаблон метатега keywords для главной страницы.
        '''
    )
    homepage_description_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Description',
        help_text='''
            Определяет шаблон метатега description для главной страницы.
        '''
    )
    news_title_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Title',
        help_text='''
            Определяет метатег title для страницы новостей.
        '''
    )
    news_keywords_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Keywords',
        help_text='''
            Определяет шаблон метатега keywords для страницы новостей.
        '''
    )
    news_description_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Description',
        help_text='''
            Определяет шаблон метатега description для страницы новостей.
        '''
    )
    actions_title_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Title',
        help_text='''
            Определяет метатег title для страницы с акциями.
        '''
    )
    actions_keywords_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Keywords',
        help_text='''
            Определяет шаблон метатега keywords для страницы с акциями.
        '''
    )
    actions_description_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Description',
        help_text='''
            Определяет шаблон метатега description для страницы с акциями.
        '''
    )
    flatpage_title_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Title контентных страниц',
        help_text='''
            Определяет шаблон метатега title.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной страницы.
        '''
    )
    flatpage_keywords_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Keywords контентных страниц',
        help_text='''
            Определяет шаблон метатега keywords.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной страницы.
        '''
    )
    flatpage_description_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Description контентных страниц',
        help_text='''
            Определяет шаблон метатега description.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной страницы.
        '''
    )
    default_title_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Title по умолчанию',
        help_text='''
            Определяет шаблон метатега title.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной сущности.
        '''
    )
    default_keywords_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Keywords по умолчанию',
        help_text='''
            Определяет шаблон метатега keywords.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной сущности.
        '''
    )
    default_description_pattern = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Шаблон Description по умолчанию',
        help_text='''
            Определяет шаблон метатега description.
            Если в шаблоне присутствует переменная __V__, то
            в метатеге эта переменная будет замена значением
            соответствующего поля конкретной сущности.
        '''
    )

    robots_txt = models.TextField(
        blank=True,
        default='',
        verbose_name='Содержимое файла robots.txt',
    )
    head_injection = models.TextField(
        blank=True,
        default='',
        verbose_name='Вставка в конец секции HEAD',
        help_text='''
            Содержимое поля будет "как есть" добавлено в конец
            секции HEAD для любой html-страницы сайта.
        '''
    )
    body_injection = models.TextField(
        blank=True,
        default='',
        verbose_name='Вставка в конец секции BODY',
        help_text='''
            Содержимое поля будет "как есть" добавлено в конец
            секции HEAD для любой html-страницы сайта.
        '''
    )
    add_yandex_reviews = models.BooleanField(
        blank=True,
        default=False,
        verbose_name='Добавить Яндекс-отзывы'
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super(Settings, self).save(*args, **kwargs)
        if self.is_active:
            Settings.objects.all().exclude(pk=self.pk).update(is_active=False)


class Redirect(models.Model):
    source = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Откуда',
        help_text='Относительный адрес'
    )
    destination = models.CharField(
        max_length=255,
        verbose_name='Куда',
        help_text='Относительный адрес'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Редирект'
        verbose_name_plural = 'Редиректы'

    def __str__(self):
        return '%s...' % self.source[:31] if len(self.source) > 32 else self.source


class Homepage(models.Model):
    is_published = models.BooleanField(
        blank=True,
        default=True,
        db_index=True,
        verbose_name='Опубликована',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменена')
    text_content = models.TextField(
        blank=True,
        default='',
        verbose_name='Текстовое содержимое'
    )

    hero_desktop = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        blank=True,
        null=True,
        verbose_name='Главное изображение (hero) для десктопов',
        help_text='''
            <p>
                Фото шириной 2420px. Высота может быть разной,
                рекомендуется 746px.
            </p>
            <p>
                <strong>Очень важно!</strong> Это фото будет размещено на
                сайте без какой-либо обработки и оптимизации размера,
                поэтому оно должно быть подготовлено оператором.
                Рекомендуется использовать прогрессивный jpeg размером не
                более 200-400kb.
            </p>
            <p>
                Рекомендуется сжать фото с помощью
                <a href="https://imagecompressor.com/ru/">этого сервиса</a>.
            </p>
        '''
    )
    hero_desktop_size = models.CharField(max_length=128, null=True, blank=True)
    hero_tablet = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        blank=True,
        null=True,
        verbose_name='Главное изображение (hero) для планшетов',
        help_text='''
            <p>Фото шириной 1024px.</p>
            <p>
                <strong>Очень важно!</strong> Это фото будет размещено на
                сайте без какой-либо обработки и оптимизации размера,
                поэтому оно должно быть подготовлено оператором.
                Рекомендуется использовать прогрессивный jpeg размером не
                более 100-300kb.
            </p>
            <p>
                Рекомендуется сжать фото с помощью
                <a href="https://imagecompressor.com/ru/">этого сервиса</a>.
            </p>
        '''
    )
    hero_tablet_size = models.CharField(max_length=128, null=True, blank=True)

    hero_mobile = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        blank=True,
        null=True,
        verbose_name='Главное изображение (hero) мобильных телефонов',
        help_text='''
            <p>Фото шириной 480px.</p>
            <p>
                <strong>Очень важно!</strong> Это фото будет размещено на
                сайте без какой-либо обработки и оптимизации размера,
                поэтому оно должно быть подготовлено оператором.
                Рекомендуется использовать прогрессивный jpeg размером не
                более 100-200kb.
            </p>
            <p>
                Рекомендуется сжать фото с помощью
                <a href="https://imagecompressor.com/ru/">этого сервиса</a>.
            </p>
        '''
    )
    hero_mobile_size = models.CharField(max_length=128, null=True, blank=True)
    class Meta:
        verbose_name = "Главная страница"
        verbose_name_plural = "Главные страницы"

    def __str__(self):
        return str(self.pk)

    @property
    def html_content(self):
        content = getattr(
            self,
            '__html_content',
            ''.join(markdown(self.text_content).splitlines())
        )
        setattr(self, '__html_content', content)
        return content

    @property
    def has_hero(self):
        return self.hero_desktop.name and self.hero_mobile.name and \
                self.hero_tablet.name

    def get_hero_size(self, field_name):
        cache_name = '__c_%s' % field_name
        size = getattr(self, cache_name, None)

        if size is None:
            try:
                size = json.loads(getattr(self, field_name))
            except Exception:
                size = {'width': 0, 'height': 0, 'ratio': 0}
        setattr(self, cache_name, size)
        return size

    @property
    def hero_desktop_height(self):
        return self.get_hero_size('hero_desktop_size')['height']

    @property
    def hero_desktop_width(self):
        return self.get_hero_size('hero_desktop_size')['width']

    @property
    def hero_tablet_ratio(self):
        return self.get_hero_size('hero_tablet_size')['ratio']

    @property
    def hero_mobile_ratio(self):
        return self.get_hero_size('hero_mobile_size')['ratio']

    def set_image_geometry(self, image, size_field):
        setattr(
            self,
            size_field,
            json.dumps({
                'width': image.width if image else 0,
                'height': image.height if image else 0,
                'ratio': (image.height / image.width) * 100 if image else 0,
            })
        )

    def save(self, *args, **kwargs):
        self.set_image_geometry(self.hero_desktop, 'hero_desktop_size')
        self.set_image_geometry(self.hero_tablet, 'hero_tablet_size')
        self.set_image_geometry(self.hero_mobile, 'hero_mobile_size')

        super(Homepage, self).save(*args, **kwargs)
        if self.is_published:
            Homepage.objects.all().exclude(pk=self.pk).update(is_published=False)


class Teaser(OrderMixin, ThumbnailProcessor):
    is_published = models.BooleanField(
        blank=True,
        default=True,
        db_index=True,
        verbose_name='Опубликован',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    publish_date = models.DateField(
        db_index=True,
        blank=True,
        null=True,
        verbose_name="Дата публикации",
        help_text='''
            <p>
                Эта дата будет использована в тизере как дата его публикации.
            </p>
            <p>
                По умолчанию (если поле пустое) будет использован день,
                когда был установлен флажок "Опубликован".
            </p>
            <p>
                На сайте публикуются тизеры с датой публикации равной или
                меньшей чем текущая.
            </p>
        '''
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Изменен')
    href = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name="URL ссылки",
        help_text='''
            <p>
                Если значение задано, то ссылка тизера будет указывать на
                введенный URL. Если URL внутрисайтовый, то он должен быть
                относительным.</p>
            <p>
                Этот параметр является взаимоисключающим с параметром
                "Страница сайта", но если заданы оба, то "URL ссылки"
                будет проигнорирован.
            </p>
        '''
    )
    page = models.ForeignKey(
        Page,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Страница сайта',
        help_text='''
            <p>
                Если значение задано, то ссылка тизера будет указывать на
                выбранную страницу.
            </p>
            <p>
                Этот параметр является взаимоисключающим с параметром
                "URL ссылки", но если заданы оба, то "URL ссылки"
                будет проигнорирован.
            </p>
        '''
    )
    image = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        verbose_name='Фото',
        help_text='''
            <p>Фото шириной не менее 350px.</p>
            <p>
                Для мобильной версии желательно, чтобы изображения у всех
                тизеров имели одинаковые пропорции сторон. Идеальный вариант
                &nbash; 16х9.
            </p>
        '''
    )
    heading = models.CharField(max_length=512, verbose_name='Заголовок')
    add_to_actions = models.BooleanField(
        db_index=True,
        blank=True,
        default=False,
        verbose_name='Добавить в раздел акции',
        help_text='''
            Если флажок установлен, то тизер будет присутствовать в
            правом сайдбаре всех страниц сайта в разделе "Акции".
        '''
    )
    add_to_news = models.BooleanField(
        db_index=True,
        blank=True,
        default=False,
        verbose_name='Добавить в новости',
        help_text='''
            Если флажок установлен, то тизер будет присутствовать в
            правом сайдбаре главной страницы.
        '''
    )

    class Meta:
        verbose_name = 'Тизер'
        verbose_name_plural = 'Тизеры'
        ordering = ('order_no', '-publish_date', 'pk', )

    def __str__(self):
        return self.heading

    def clean(self):
        if not self.page and not self.href:
            raise ValidationError({
                'page': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Страница сайта" или "URL ссылки"
                ''',
                'href': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Страница сайта" или "URL ссылки"
                '''
            })

    @property
    def image_field_for_thumb(self):
        return self.image

    @property
    def thumbnail(self):
        return self._get_resized_image_url(desired_width=350)

    @property
    def admin_thumbnail(self):
        return self._get_resized_image_url(desired_max_side=150)

    def save(self, *args, **kwargs):
        if self.publish_date is None and self.is_published:
            self.publish_date = timezone.now().date()

        super(Teaser, self).save(*args, **kwargs)
        self.thumbnail

    def get_absolute_url(self):
        return self.page.get_absolute_url() if self.page else self.href or '#'


class Media(OrderMixin, ThumbnailProcessor):
    image = models.ImageField(
        upload_to=fregat.utils.get_upload_path_without_name_keeping,
        blank=True,
        null=True,
        verbose_name='Фото',
        help_text='''
            <p>
                Если "<strong>Адрес видео на Youtube</strong>" не заполнен,
                то данный материал обрабатывается как обычная фотография.
            </p>
            <p>
                В противном случае фото из этого поля выступает в роли
                превью-изображения для видеоролика. Если оно не было загружено
                вручную, то при сохранении превью будет скачано с Youtube.
            </p>
        '''
    )
    youtube_url = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='Адрес видео на Youtube',
    )
    youtube_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Код видео'
    )
    caption = models.CharField(
        max_length=512,
        blank=True,
        default='',
        verbose_name='Подпись'
    )
    text = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание'
    )
    page = models.ForeignKey(
        Page,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Страница'
    )
    price_item = models.ForeignKey(
        PriceItem,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Страница'
    )
    homepage = models.ForeignKey(
        Homepage,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Главная страница'
    )

    class Meta:
        verbose_name = "Медиа"
        verbose_name_plural = "Медиа"
        ordering = ('order_no', 'pk', )

    def __str__(self):
        return self.caption or str(self.pk)

    def clean(self):
        if not self.image and not self.youtube_url:
            raise ValidationError({
                'image': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Фото" или "Адрес видео на Youtube"
                ''',
                'youtube_url': '''
                    Должно быть заполнено как минимум одно из двух
                    полей: "Фото" или "Адрес видео на Youtube"
                '''
            })

    @property
    def image_field_for_thumb(self):
        return self.image

    @property
    def thumbnail(self):
        return self._get_resized_image_url(desired_height=200)

    @property
    def big_photo(self):
        return self._get_resized_image_url(desired_max_side=1600)

    @property
    def media_type(self):
        return 'video' if self.youtube_url else 'photo'

    def _get_youtube_code_from_url(self, url):
        code = ''
        stoppers = ('#', '&')

        if '&v=' in url:
            url_parts = url.split('&v=')
            if len(url_parts) > 1:
                code = url_parts[1]

                for s in stoppers:
                    if s in code:
                        code = code.split(s)[0]

        else:
            for s in stoppers:
                if s in url:
                    url = url[:url.find(s)]

            if '=' in url:
                url_parts = url.split('=')
                if len(url_parts) > 1:
                    code = url_parts[1]
            elif '/' in url:
                for url_part in url.split('/'):
                    if len(url_part) > 1:
                        if 'http' not in url_part and '.' not in url_part:
                            code = url_part

        return code

    def save(self, *args, **kwargs):
        if not self.youtube_url:
            self.youtube_id = ''

        if self.youtube_url and not self.youtube_id:
            yt_id = self._get_youtube_code_from_url(url=self.youtube_url)
            self.youtube_id = yt_id

        if self.youtube_id and not self.image:
            try:
                url = 'https://img.youtube.com/vi/%s/0.jpg' % self.youtube_id
                content = urlopen(url).read()
                self.image.save('tmp_yt.jpg', ContentFile(content), save=True)
            except Exception:
                self.image = ''

        super(Media, self).save(*args, **kwargs)
        self.thumbnail
        self.big_photo

        if self.page:
            Page.objects.filter(pk=self.pk).update(updated_at=timezone.now())



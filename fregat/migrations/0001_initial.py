# Generated by Django 3.2.9 on 2021-12-04 07:07

from django.db import migrations, models
import django.db.models.deletion
import fregat.models
import fregat.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Homepage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_published', models.BooleanField(blank=True, db_index=True, default=True, verbose_name='Опубликована')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Изменена')),
                ('text_content', models.TextField(blank=True, default='', verbose_name='Текстовое содержимое')),
                ('hero_desktop', models.ImageField(blank=True, help_text='\n            <p>Фото шириной 2420px.</p>\n            <p>\n                <strong>Очень важно!</strong> Это фото будет размещено на\n                сайте без какой-либо обработки и оптимизации размера,\n                поэтому оно должно быть подготовлено оператором.\n                Рекомендуется использовать прогрессивный jpeg размером не\n                более 200-400kb.\n            </p>\n        ', null=True, upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Главное изображение (hero) для десктопов')),
                ('hero_desktop_size', models.CharField(blank=True, max_length=128, null=True)),
                ('hero_tablet', models.ImageField(blank=True, help_text='\n            <p>Фото шириной 1024px.</p>\n            <p>\n                <strong>Очень важно!</strong> Это фото будет размещено на\n                сайте без какой-либо обработки и оптимизации размера,\n                поэтому оно должно быть подготовлено оператором.\n                Рекомендуется использовать прогрессивный jpeg размером не\n                более 100-300kb.\n            </p>\n        ', null=True, upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Главное изображение (hero) для планшетов')),
                ('hero_tablet_size', models.CharField(blank=True, max_length=128, null=True)),
                ('hero_mobile', models.ImageField(blank=True, help_text='\n            <p>Фото шириной 480px.</p>\n            <p>\n                <strong>Очень важно!</strong> Это фото будет размещено на\n                сайте без какой-либо обработки и оптимизации размера,\n                поэтому оно должно быть подготовлено оператором.\n                Рекомендуется использовать прогрессивный jpeg размером не\n                более 100-200kb.\n            </p>\n        ', null=True, upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Главное изображение (hero) мобильных телефонов')),
                ('hero_mobile_size', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'verbose_name': 'Главная страница',
                'verbose_name_plural': 'Главные страницы',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_published', models.BooleanField(blank=True, db_index=True, default=True, help_text='\n            Если флажок снят, то материал не будет присутствовать на сайте.\n        ', verbose_name='Опубликован')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('heading', models.CharField(max_length=512, verbose_name='Заголовок')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Ключ ЧПУ')),
                ('content', models.TextField(verbose_name='Основное содержимое')),
                ('title', models.CharField(blank=True, default='', help_text='\n            <p>\n                Подставляется в качестве переменной __V__ в общий шаблон\n                метатега title страницы.\n            </p>\n            <p>\n                Если значение не задано, то в шаблон подставляется\n                заголовок страницы.\n            </p>\n        ', max_length=255, verbose_name='Title')),
                ('keywords', models.CharField(blank=True, default='', help_text='\n            <p>\n                Подставляется в качестве переменной __V__ в общий шаблон\n                метатега keywords страницы.\n            </p>\n            <p>\n                Если значение не задано, то в шаблон подставляется\n                заголовок страницы.\n            </p>\n        ', max_length=255, verbose_name='Keywords')),
                ('description', models.CharField(blank=True, default='', help_text='\n            <p>\n                Подставляется в качестве переменной __V__ в общий шаблон\n                метатега description страницы.\n            </p>\n            <p>\n                Если значение не задано, то в шаблон подставляется\n                заголовок страницы.\n            </p>\n        ', max_length=255, verbose_name='Description')),
                ('use_metatags_as_is', models.BooleanField(blank=True, default=False, help_text='\n            <p>\n                Если флажок установлен, то в качестве метатегов для данной\n                страницы будут использованы значения соответствующих полей,\n                а при их отсутствии будет использован заголовок страницы.\n            </p>\n            <p>\n                Если же флажок снят, то в метатегах будет результат\n                шаблонизации (шаблон создается в настройках сайта), куда\n                в качестве переменных будут переданы значения соответствующих\n                полей.\n            </p>\n        ', verbose_name='Отключить шаблонизацию метатегов')),
            ],
            options={
                'verbose_name': 'Страница сайта',
                'verbose_name_plural': 'Страницы сайта',
            },
        ),
        migrations.CreateModel(
            name='Pricelist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Используется только в админке.', max_length=255, verbose_name='Название прайслиста')),
                ('is_default', models.BooleanField(blank=True, db_index=True, default=False, help_text='\n            <p>\n                Эта настройка необходима для быстрого создания позиций\n                прайсл-листов.\n            </p>\n            <p>\n                При создании позиции прайс-листа необходимо выбрать к\n                какому прайс-листу она относится. Однако если имеется\n                прайс-лист по умолчанию, то это поле можно оставлять\n                пустым, будет использован прайс-лист по умолчанию.\n            </p>\n            <p>\n                В других механиках это поле не используется.\n            </p>\n        ', verbose_name='Прайс-лист по умолчанию')),
                ('view', models.CharField(choices=[('grid', 'Таблица'), ('tile', 'Плитка')], default='grid', max_length=8, verbose_name='Вид прайслиста')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Изменен')),
            ],
            options={
                'verbose_name': 'Прайслист',
                'verbose_name_plural': 'Прайслисты',
            },
        ),
        migrations.CreateModel(
            name='PricelistCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(blank=True, db_index=True, default=500, help_text='\n            <p>\n                Сортировка элементов идет от меньшего числа к большему.\n                100, 200, 300, 400 и т.д.\n            </p>\n            <p>\n                По умолчанию значение сортировки равно 500.\n            </p>\n        ', verbose_name='Порядок сортировки')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Категория прайслиста',
                'verbose_name_plural': 'Категории прайслистов',
                'ordering': ('order_no',),
            },
        ),
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(help_text='Относительный адрес', max_length=255, unique=True, verbose_name='Откуда')),
                ('destination', models.CharField(help_text='Относительный адрес', max_length=255, verbose_name='Куда')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
            ],
            options={
                'verbose_name': 'Редирект',
                'verbose_name_plural': 'Редиректы',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(blank=True, db_index=True, default=True, verbose_name='Активные настройки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Изменен')),
                ('phone', models.CharField(help_text='\n            В человекопонятном виде. Используется в шапке сайта, подвале,\n            мобильном меню и на странице контактов.\n        ', max_length=128, verbose_name='Телефон')),
                ('address', models.CharField(help_text='\n            В человекопонятном виде. Используется в шапке сайта, подвале,\n            мобильном меню и странице контактов.\n        ', max_length=256, verbose_name='Адрес')),
                ('latitude', models.CharField(blank=True, help_text='\n            Координаты можно взять в сервисе интерактивных карт.\n            Учавствует в микроразметке, а также в построении контактов.\n        ', max_length=32, null=True, verbose_name='Широта')),
                ('longitude', models.CharField(blank=True, help_text='\n            Координаты можно взять в сервисе интерактивных карт.\n            Учавствует в микроразметке, а также в построении контактов.\n        ', max_length=32, null=True, verbose_name='Долгота')),
                ('organization_name', models.CharField(blank=True, help_text='Название организации. Учавствует в микроразметке.', max_length=64, null=True, verbose_name='Название организации')),
                ('organization_description', models.CharField(blank=True, help_text='Описание организации. Учавствует в микроразметке.', max_length=512, null=True, verbose_name='Описание организации')),
                ('postal_code', models.CharField(blank=True, help_text='Учавствует в микроразметке.', max_length=16, null=True, verbose_name='Почтовый индекс')),
                ('region', models.CharField(blank=True, help_text='Учавствует в микроразметке.', max_length=128, null=True, verbose_name='Название региона или области')),
                ('city', models.CharField(blank=True, help_text='\n            Используется в шапке сайта, подвале,\n            мобильном меню, на странице контактов, а также в микроразметке.\n        ', max_length=256, null=True, verbose_name='Город')),
                ('street_address', models.CharField(blank=True, help_text='Учавствует в микроразметке.', max_length=128, null=True, verbose_name='Адрес в населенном пункте')),
                ('email', models.EmailField(blank=True, help_text='Учавствует в микроразметке.', max_length=254, null=True, verbose_name='Адрес электронной почты')),
                ('homepage_title_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет метатег title для главной страницы.\n        ', max_length=512, verbose_name='Title')),
                ('homepage_keywords_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега keywords для главной страницы.\n        ', max_length=512, verbose_name='Keywords')),
                ('homepage_description_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега description для главной страницы.\n        ', max_length=512, verbose_name='Description')),
                ('news_title_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет метатег title для страницы новостей.\n        ', max_length=512, verbose_name='Title')),
                ('news_keywords_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега keywords для страницы новостей.\n        ', max_length=512, verbose_name='Keywords')),
                ('news_description_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега description для страницы новостей.\n        ', max_length=512, verbose_name='Description')),
                ('actions_title_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет метатег title для страницы с акциями.\n        ', max_length=512, verbose_name='Title')),
                ('actions_keywords_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега keywords для страницы с акциями.\n        ', max_length=512, verbose_name='Keywords')),
                ('actions_description_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега description для страницы с акциями.\n        ', max_length=512, verbose_name='Description')),
                ('flatpage_title_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега title.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной страницы.\n        ', max_length=512, verbose_name='Шаблон Title контентных страниц')),
                ('flatpage_keywords_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега keywords.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной страницы.\n        ', max_length=512, verbose_name='Шаблон Keywords контентных страниц')),
                ('flatpage_description_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега description.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной страницы.\n        ', max_length=512, verbose_name='Шаблон Description контентных страниц')),
                ('default_title_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега title.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной сущности.\n        ', max_length=512, verbose_name='Шаблон Title по умолчанию')),
                ('default_keywords_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега keywords.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной сущности.\n        ', max_length=512, verbose_name='Шаблон Keywords по умолчанию')),
                ('default_description_pattern', models.CharField(blank=True, default='', help_text='\n            Определяет шаблон метатега description.\n            Если в шаблоне присутствует переменная __V__, то\n            в метатеге эта переменная будет замена значением\n            соответствующего поля конкретной сущности.\n        ', max_length=512, verbose_name='Шаблон Description по умолчанию')),
                ('robots_txt', models.TextField(blank=True, default='', verbose_name='Содержимое файла robots.txt')),
                ('head_injection', models.TextField(blank=True, default='', help_text='\n            Содержимое поля будет "как есть" добавлено в конец\n            секции HEAD для любой html-страницы сайта.\n        ', verbose_name='Вставка в конец секции HEAD')),
                ('body_injection', models.TextField(blank=True, default='', help_text='\n            Содержимое поля будет "как есть" добавлено в конец\n            секции HEAD для любой html-страницы сайта.\n        ', verbose_name='Вставка в конец секции BODY')),
                ('add_yandex_reviews', models.BooleanField(blank=True, default=False, verbose_name='Добавить Яндекс-отзывы')),
            ],
            options={
                'verbose_name': 'Настройки сайта',
                'verbose_name_plural': 'Настройки сайта',
            },
        ),
        migrations.CreateModel(
            name='Teaser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(blank=True, db_index=True, default=500, help_text='\n            <p>\n                Сортировка элементов идет от меньшего числа к большему.\n                100, 200, 300, 400 и т.д.\n            </p>\n            <p>\n                По умолчанию значение сортировки равно 500.\n            </p>\n        ', verbose_name='Порядок сортировки')),
                ('is_published', models.BooleanField(blank=True, db_index=True, default=True, verbose_name='Опубликован')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('publish_date', models.DateField(blank=True, db_index=True, help_text='\n            <p>\n                Эта дата будет использована в тизере как дата его публикации.\n            </p>\n            <p>\n                По умолчанию (если поле пустое) будет использован день,\n                когда был установлен флажок "Опубликован".\n            </p>\n            <p>\n                На сайте публикуются тизеры с датой публикации равной или\n                меньшей чем текущая.\n            </p>\n        ', null=True, verbose_name='Дата публикации')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Изменен')),
                ('href', models.CharField(blank=True, help_text='\n            <p>\n                Если значение задано, то ссылка тизера будет указывать на\n                введенный URL. Если URL внутрисайтовый, то он должен быть\n                относительным.</p>\n            <p>\n                Этот параметр является взаимоисключающим с параметром\n                "Страница сайта", но если заданы оба, то "URL ссылки"\n                будет проигнорирован.\n            </p>\n        ', max_length=512, null=True, verbose_name='URL ссылки')),
                ('image', models.ImageField(help_text='\n            <p>Фото шириной не менее 350px.</p>\n            <p>\n                Для мобильной версии желательно, чтобы изображения у всех\n                тизеров имели одинаковые пропорции сторон. Идеальный вариант\n                &nbash; 16х9.\n            </p>\n        ', upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Фото')),
                ('heading', models.CharField(max_length=512, verbose_name='Заголовок')),
                ('add_to_actions', models.BooleanField(blank=True, db_index=True, default=False, help_text='\n            Если флажок установлен, то тизер будет присутствовать в\n            правом сайдбаре всех страниц сайта в разделе "Акции".\n        ', verbose_name='Добавить в раздел акции')),
                ('add_to_news', models.BooleanField(blank=True, db_index=True, default=False, help_text='\n            Если флажок установлен, то тизер будет присутствовать в\n            правом сайдбаре главной страницы.\n        ', verbose_name='Добавить в новости')),
                ('page', models.ForeignKey(blank=True, help_text='\n            <p>\n                Если значение задано, то ссылка тизера будет указывать на\n                выбранную страницу.\n            </p>\n            <p>\n                Этот параметр является взаимоисключающим с параметром\n                "URL ссылки", но если заданы оба, то "URL ссылки"\n                будет проигнорирован.\n            </p>\n        ', null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.page', verbose_name='Страница сайта')),
            ],
            options={
                'verbose_name': 'Тизер',
                'verbose_name_plural': 'Тизеры',
                'ordering': ('order_no', '-publish_date'),
            },
            bases=(models.Model, fregat.models.ThumbnailProcessor),
        ),
        migrations.CreateModel(
            name='PriceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(blank=True, db_index=True, default=500, help_text='\n            <p>\n                Сортировка элементов идет от меньшего числа к большему.\n                100, 200, 300, 400 и т.д.\n            </p>\n            <p>\n                По умолчанию значение сортировки равно 500.\n            </p>\n        ', verbose_name='Порядок сортировки')),
                ('name', models.CharField(help_text='Например, "Аренда бильярда"', max_length=255, verbose_name='Название позиции')),
                ('common_price', models.DecimalField(blank=True, decimal_places=2, help_text='\n            Если цена позиции одинакова во все дни, то нужно использовать\n            это поле. В противном случае стоит использовать соответствующие\n            поля.\n        ', max_digits=10, null=True, verbose_name='Цена')),
                ('price_on_weekdays', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена с ПН-ЧТ')),
                ('price_on_weekend', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена ПТ-ВС ')),
                ('price_on_holydays', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена по праздникам')),
                ('unit', models.CharField(blank=True, max_length=32, null=True, verbose_name='Единица измерения')),
                ('image', models.ImageField(blank=True, null=True, upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Фото')),
                ('text', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Изменен')),
                ('category', models.ForeignKey(blank=True, help_text='Например, "Напитки"', null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.pricelistcategory', verbose_name='Категория')),
                ('pricelist', models.ForeignKey(blank=True, help_text='\n            <p>\n                Если поле оставить пустым и в системе имеется прайс-лист\n                по умолчанию, то именно он будет использован при сохранении.\n            </p>\n            <p>\n                Если же прайс-листа по умолчанию нет, то это поле обязтельно\n                для заполнения.\n            </p>\n        ', null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.pricelist', verbose_name='Прайсл-лист')),
            ],
            options={
                'verbose_name': 'Цена',
                'verbose_name_plural': 'Цены',
                'ordering': ('category__order_no', 'order_no'),
            },
            bases=(models.Model, fregat.models.ThumbnailProcessor),
        ),
        migrations.AddField(
            model_name='page',
            name='pricelist',
            field=models.ForeignKey(blank=True, help_text='\n            Это поле добавляет после основного содержимого страницы выбранный\n            прайслист.\n        ', null=True, on_delete=django.db.models.deletion.SET_NULL, to='fregat.pricelist', verbose_name='Прайслист'),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(blank=True, db_index=True, default=500, help_text='\n            <p>\n                Сортировка элементов идет от меньшего числа к большему.\n                100, 200, 300, 400 и т.д.\n            </p>\n            <p>\n                По умолчанию значение сортировки равно 500.\n            </p>\n        ', verbose_name='Порядок сортировки')),
                ('name', models.CharField(max_length=128, verbose_name='Пункт меню')),
                ('href', models.CharField(blank=True, help_text='\n            <p>\n                Если значение задано, то пункт меню будет ссылкой, указывающей\n                на введенный URL.\n            </p>\n            <p>\n                Этот параметр является взаимоисключающим с параметром\n                "Страница сайта", но если заданы оба, то "URL ссылки"\n                будет проигнорирован.\n            </p>\n            <p>\n                Если же не задан ни один из параметров, то\n                пункт меню не будет являться ссылкой (это может быть\n                необходимо для группирующих разделов меню).\n            </p>\n        ', max_length=512, null=True, verbose_name='URL ссылки')),
                ('thread_id', models.ImageField(blank=True, db_index=True, null=True, upload_to='')),
                ('is_child', models.IntegerField(blank=True, db_index=True, default=0)),
                ('page', models.ForeignKey(blank=True, help_text='\n            <p>\n                Если значение задано, то пункт меню будет ссылкой, указывающей\n                на выбранную страницу.\n            </p>\n            <p>\n                Этот параметр является взаимоисключающим с параметром\n                "URL ссылки", но если заданы оба, то "URL ссылки"\n                будет проигнорирован.\n            </p>\n            <p>\n                Если же не задан ни один из параметров, то\n                пункт меню не будет являться ссылкой (это может быть\n                необходимо для группирующих разделов меню).\n            </p>\n        ', null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.page', verbose_name='Страница сайта')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fregat.menuitem', verbose_name='Родительский пункт меню')),
            ],
            options={
                'verbose_name': 'Пункт меню',
                'verbose_name_plural': 'Пункты меню',
                'ordering': ('thread_id', 'is_child', 'order_no'),
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField(blank=True, db_index=True, default=500, help_text='\n            <p>\n                Сортировка элементов идет от меньшего числа к большему.\n                100, 200, 300, 400 и т.д.\n            </p>\n            <p>\n                По умолчанию значение сортировки равно 500.\n            </p>\n        ', verbose_name='Порядок сортировки')),
                ('image', models.ImageField(blank=True, help_text='\n            <p>\n                Если "<strong>Адрес видео на Youtube</strong>" не заполнен,\n                то данный материал обрабатывается как обычная фотография.\n            </p>\n            <p>\n                В противном случае фото из этого поля выступает в роли\n                превью-изображения для видеоролика. Если оно не было загружено\n                вручную, то при сохранении превью будет скачано с Youtube.\n            </p>\n        ', null=True, upload_to=fregat.utils.get_upload_path_without_name_keeping, verbose_name='Фото')),
                ('youtube_url', models.CharField(blank=True, max_length=512, null=True, verbose_name='Адрес видео на Youtube')),
                ('youtube_id', models.CharField(blank=True, default='', max_length=255, verbose_name='Код видео')),
                ('caption', models.CharField(blank=True, default='', max_length=512, verbose_name='Подпись')),
                ('text', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('homepage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.homepage', verbose_name='Главная страница')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.page', verbose_name='Страница')),
                ('price_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fregat.priceitem', verbose_name='Страница')),
            ],
            options={
                'verbose_name': 'Медиа',
                'verbose_name_plural': 'Медиа',
                'ordering': ('order_no',),
            },
            bases=(models.Model, fregat.models.ThumbnailProcessor),
        ),
    ]
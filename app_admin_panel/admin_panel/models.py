from django.db import models


class User(models.Model):
    class Meta:
        db_table = 'users'
        ordering = ['created_at']
        verbose_name = 'Пользователи'
        verbose_name_plural = verbose_name

    user_id = models.BigIntegerField(primary_key=True, db_index=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    is_registered = models.BooleanField(default=False, verbose_name='Зарегистрирован')
    fio = models.CharField(max_length=64, null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)
    payment_amount = models.FloatField(default=0, verbose_name='Сумма заправок')
    refills_amount = models.IntegerField(default=0, verbose_name='Кол-во заправок')

    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        result = self.username
        if not result:
            result = str(self.user_id)
        return result


class Station(models.Model):
    class Meta:
        db_table = 'stations'
        ordering = ['id']
        verbose_name = 'АЗС'
        verbose_name_plural = verbose_name

    id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=128, null=True)
    number = models.CharField(max_length=64, null=True)
    region_name = models.CharField(max_length=128, null=True)
    federal_district = models.CharField(max_length=128, null=True)
    address = models.CharField(max_length=256, null=True)
    status = models.CharField(max_length=64, null=True)
    longitude = models.CharField(max_length=32, null=True)
    latitude = models.CharField(max_length=32, null=True)
    updated_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.id}'


class FavouriteStation(models.Model):
    class Meta:
        db_table = 'favourite_stations'
        ordering = ['id']
        verbose_name = 'Избранное пользователей'
        verbose_name_plural = verbose_name

    id = models.IntegerField(primary_key=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)


class Product(models.Model):
    class Meta:
        db_table = 'products'
        ordering = ['id']
        verbose_name = 'Товары АЗС'
        verbose_name_plural = verbose_name

    id = models.IntegerField(primary_key=True, db_index=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    code = models.CharField(max_length=32, null=True)
    name = models.CharField(max_length=32, null=True)
    price = models.FloatField(null=True)
    date = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.id}'


class Order(models.Model):
    class Meta:
        db_table = 'orders'
        ordering = ['created_at']
        verbose_name = 'Заказы'
        verbose_name_plural = verbose_name

    id = models.UUIDField(primary_key=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()
    total_price = models.FloatField()
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'


class SupportRequest(models.Model):
    class Meta:
        db_table = 'support_requests'
        ordering = ['id']
        verbose_name = 'Запросы в поддержку'
        verbose_name_plural = verbose_name

    id = models.IntegerField(primary_key=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        result = self.user.username
        if not result:
            result = str(self.user.user_id)
        return result


class Dispatcher(models.Model):
    class Meta:
        db_table = 'mailings'
        ordering = ['id']
        verbose_name = 'Рассылки'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Post', to_field='id', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    send_at = models.DateTimeField()

    def __str__(self):
        return f'{self.id}'


class Post(models.Model):
    class Meta:
        db_table = 'static_content'
        ordering = ['id']
        verbose_name = 'Контент для рассылок'
        verbose_name_plural = verbose_name

    id = models.BigIntegerField(primary_key=True)
    text = models.TextField(blank=True, null=True)
    photo_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_file_id = models.CharField(max_length=256, blank=True, null=True)
    video_note_id = models.CharField(max_length=256, blank=True, null=True)
    document_file_id = models.CharField(max_length=256, blank=True, null=True)
    sticker_file_id = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'


class MailingLog(models.Model):
    class Meta:
        db_table = 'mailings_logs'
        ordering = ['created_at']
        verbose_name = 'Итоги последней рассылки'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_sent = models.BooleanField(verbose_name='Рассылку получил?')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'


class Settings(models.Model):
    class Meta:
        db_table = 'settings'
        ordering = ['id']
        verbose_name = 'Настройки'
        verbose_name_plural = verbose_name

    id = models.AutoField(primary_key=True, db_index=True)
    card_data = models.TextField(max_length=256, verbose_name='Реквизиты карты')
    discount_percent = models.FloatField(default=0, verbose_name='Процент скидки')

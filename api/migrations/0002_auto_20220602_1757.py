# Generated by Django 3.2.6 on 2022-06-02 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('file', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members', models.TextField()),
                ('attachments', models.TextField()),
                ('messages', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='IngredientCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='RecipeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TextMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('text', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='Dialog',
        ),
        migrations.RenameField(
            model_name='forum',
            old_name='file',
            new_name='messages',
        ),
        migrations.AddField(
            model_name='recipe',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recipe',
            name='fats',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, upload_to="['D:\\\\????????????\\\\CookHelper\\\\cookhelper\\\\static']/images"),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='carbs',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='comments',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='proteins',
            field=models.IntegerField(default=None),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='userId',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='api.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(upload_to='D:\\????????????\\CookHelper\\cookhelper\\media//media'),
        ),
        migrations.AlterField(
            model_name='user',
            name='bannedIngredients',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='bannedRecipes',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='forums',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='fridge',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='starredIngredients',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='starredRecipes',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='textmessages',
            name='userId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.user'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.ingredientcategory'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.recipecategory'),
        ),
    ]

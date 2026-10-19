
# 数据填充

-   [简介](#introduction)
-   [编写 Seeder](#writing-seeders)
    -   [使用模型工厂](#using-model-factories)
    -   [调用其他 Seeder](#calling-additional-seeders)
    -   [静音模型事件](#muting-model-events)
-   [运行 Seeder](#running-seeders)

## 简介

Laravel 提供了使用 Seeder 类向数据库填充数据的功能。所有 Seeder 类都存放在 `database/seeders` 目录下。默认情况下，会为你生成一个 `DatabaseSeeder` 类。通过这个类，你可以使用 `call` 方法运行其他 Seeder 类，从而控制填充的顺序。

> [!注意]
> 在数据库填充期间，[批量赋值保护](/docs/laravel/12.x/eloquent#mass-assignment) 会自动被禁用。

## 编写 Seeder

要生成一个 Seeder，可以执行 `make:seeder` [Artisan 命令](/docs/laravel/12.x/artisan)。框架生成的所有 Seeder 都会放置在 `database/seeders` 目录下：

```shell
php artisan make:seeder UserSeeder
```

默认情况下，一个 Seeder 类只包含一个方法：`run`。当执行 `db:seed` [Artisan 命令](/docs/laravel/12.x/artisan) 时，这个方法会被调用。在 `run` 方法中，你可以按照自己的方式向数据库插入数据。可以使用 [查询构建器](/docs/laravel/12.x/queries) 手动插入数据，也可以使用 [Eloquent 模型工厂](/docs/laravel/12.x/eloquent-factories)。

例如，我们修改默认的 `DatabaseSeeder` 类，并在 `run` 方法中添加一个数据库插入语句：

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class DatabaseSeeder extends Seeder
{
    /**
     * 运行数据库填充器
     */
    public function run(): void
    {
        DB::table('users')->insert([
            'name' => Str::random(10),
            'email' => Str::random(10).'@example.com',
            'password' => Hash::make('password'),
        ]);
    }
}
```

> [!注意]
> 你可以在 `run` 方法的参数中声明任何依赖，它们会通过 Laravel 的 [服务容器](/docs/laravel/12.x/container) 自动解析。



### 使用模型工厂

当然，为每个模型手动指定属性来填充数据很麻烦。相反，你可以使用 [模型工厂](/docs/laravel/12.x/eloquent-factories) 来方便地生成大量数据库记录。首先，请查看 [模型工厂文档](/docs/laravel/12.x/eloquent-factories) 学习如何定义工厂。

例如，我们创建 50 个用户，并且每个用户都有一篇关联的文章：

```php
use App\Models\User;

/**
 * 运行数据库填充器
 */
public function run(): void
{
    User::factory()
        ->count(50)
        ->hasPosts(1)
        ->create();
}
```

### 调用其他 Seeder

在 `DatabaseSeeder` 类中，你可以使用 `call` 方法执行其他 Seeder 类。使用 `call` 方法可以将数据库填充拆分成多个文件，避免单个 Seeder 类过大。`call` 方法接受一个包含要执行的 Seeder 类的数组：

```php
/**
 * 运行数据库填充器
 */
public function run(): void
{
    $this->call([
        UserSeeder::class,
        PostSeeder::class,
        CommentSeeder::class,
    ]);
}
```

### 静音模型事件

在运行 Seeder 时，你可能希望阻止模型触发事件。可以通过使用 `WithoutModelEvents` trait 来实现。使用该 trait 后，即使通过 `call` 方法执行其他 Seeder 类，也不会触发任何模型事件：

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * 运行数据库填充器
     */
    public function run(): void
    {
        $this->call([
            UserSeeder::class,
        ]);
    }
}
```

## 运行 Seeder

你可以执行 `db:seed` Artisan 命令来填充数据库。默认情况下，`db:seed` 命令会运行 `Database\Seeders\DatabaseSeeder` 类，该类又可以调用其他 Seeder 类。不过，你也可以使用 `--class` 选项指定单独的 Seeder 类来运行：

```shell
php artisan db:seed

php artisan db:seed --class=UserSeeder
```



你也可以使用 `migrate:fresh` 命令结合 `--seed` 选项来填充数据库，这会删除所有表并重新执行所有迁移。此命令适合用来彻底重建数据库。`--seeder` 选项可用于指定要运行的特定 Seeder：

```shell
php artisan migrate:fresh --seed

php artisan migrate:fresh --seed --seeder=UserSeeder
```

#### 在生产环境中强制运行 Seeder

某些填充操作可能会修改或丢失数据。为了保护你的生产数据库，Laravel 会在 `production` 环境中运行 Seeder 前提示确认。若想在生产环境中无需提示直接运行 Seeder，可以使用 `--force` 参数：

```shell
php artisan db:seed --force
```

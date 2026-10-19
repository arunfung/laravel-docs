# 数据库：数据填充

- [简介](#introduction)
- [编写 Seeder](#writing-seeders)
    - [使用模型工厂](#using-model-factories)
    - [调用其他 Seeder](#calling-additional-seeders)
    - [禁用模型事件](#muting-model-events)
- [运行 Seeder](#running-seeders)

<a name="introduction"></a>
## 简介

Laravel 支持通过 Seeder 类向数据库填充数据。所有 Seeder 类都存放在 `database/seeders` 目录中。默认情况下，框架会为你定义一个 `DatabaseSeeder` 类。你可以在该类中使用 `call` 方法运行其他 Seeder 类，从而控制数据填充的顺序。

> [!NOTE]
> 数据库填充期间会自动禁用[批量赋值保护](/docs/{{version}}/eloquent#mass-assignment)。

<a name="writing-seeders"></a>
## 编写 Seeder

要生成 Seeder，请执行 `make:seeder` [Artisan 命令](/docs/{{version}}/artisan)。框架生成的所有 Seeder 都会放在 `database/seeders` 目录中：

```shell
php artisan make:seeder UserSeeder
```

默认情况下，Seeder 类只包含一个 `run` 方法。执行 `db:seed` [Artisan 命令](/docs/{{version}}/artisan)时会调用该方法。在 `run` 方法中，你可以按需向数据库插入数据：既可以使用[查询构造器](/docs/{{version}}/queries)手动插入，也可以使用 [Eloquent 模型工厂](/docs/{{version}}/eloquent-factories)。

例如，我们可以修改默认的 `DatabaseSeeder` 类，在 `run` 方法中添加一条数据库插入语句：

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
     * 运行数据库填充器。
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

> [!NOTE]
> 你可以在 `run` 方法的签名中通过类型提示声明所需的依赖，Laravel 的[服务容器](/docs/{{version}}/container)会自动解析它们。

<a name="using-model-factories"></a>
### 使用模型工厂

为每个待填充的模型手动指定属性很繁琐。你可以使用[模型工厂](/docs/{{version}}/eloquent-factories)方便地生成大量数据库记录。首先，请参阅[模型工厂文档](/docs/{{version}}/eloquent-factories)，了解如何定义工厂。

例如，我们创建 50 个用户，每个用户都有一篇关联的文章：

```php
use App\Models\User;

/**
 * 运行数据库填充器。
 */
public function run(): void
{
    User::factory()
        ->count(50)
        ->hasPosts(1)
        ->create();
}
```

<a name="calling-additional-seeders"></a>
### 调用其他 Seeder

在 `DatabaseSeeder` 类中，你可以使用 `call` 方法执行其他 Seeder 类。这样可以将数据库填充分散到多个文件中，避免单个 Seeder 类过于庞大。`call` 方法接受一个数组，其中包含要执行的 Seeder 类：

```php
/**
 * 运行数据库填充器。
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

<a name="muting-model-events"></a>
### 禁用模型事件

运行 Seeder 时，你可能希望阻止模型派发事件。可以使用 `WithoutModelEvents` trait 来实现。使用该 trait 后，即使通过 `call` 方法执行其他 Seeder 类，也不会派发任何模型事件：

```php
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * 运行数据库填充器。
     */
    public function run(): void
    {
        $this->call([
            UserSeeder::class,
        ]);
    }
}
```

<a name="running-seeders"></a>
## 运行 Seeder

你可以执行 `db:seed` Artisan 命令来填充数据库。默认情况下，该命令会运行 `Database\Seeders\DatabaseSeeder` 类，该类又可以调用其他 Seeder 类。你也可以使用 `--class` 选项，指定一个 Seeder 类单独运行：

```shell
php artisan db:seed

php artisan db:seed --class=UserSeeder
```

你也可以结合 `migrate:fresh` 命令和 `--seed` 选项来填充数据库。这会删除所有表并重新运行所有迁移，适用于彻底重建数据库的场景。你还可以使用 `--seeder` 选项，指定要运行的 Seeder：

```shell
php artisan migrate:fresh --seed

php artisan migrate:fresh --seed --seeder=UserSeeder
```

<a name="forcing-seeding-production"></a>
#### 在生产环境中强制运行 Seeder

某些数据填充操作可能导致数据被修改或丢失。为防止误操作生产数据库，在 `production` 环境中执行 Seeder 前，Laravel 会要求确认。要跳过提示并强制运行 Seeder，可以使用 `--force` 标志：

```shell
php artisan db:seed --force
```

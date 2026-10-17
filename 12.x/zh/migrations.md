# 数据库：迁移

-   [简介](#introduction)
-   [生成迁移](#generating-migrations)
    -   [合并迁移](#squashing-migrations)
-   [迁移结构](#migration-structure)
-   [运行迁移](#running-migrations)
    -   [回滚迁移](#rolling-back-migrations)
-   [表](#tables)
    -   [创建表](#creating-tables)
    -   [更新表](#updating-tables)
    -   [重命名 / 删除表](#renaming-and-dropping-tables)
-   [列](#columns)
    -   [创建列](#creating-columns)
    -   [可用列类型](#available-column-types)
    -   [列修饰符](#column-modifiers)
    -   [修改列](#modifying-columns)
    -   [重命名列](#renaming-columns)
    -   [删除列](#dropping-columns)
-   [索引](#indexes)
    -   [创建索引](#creating-indexes)
    -   [重命名索引](#renaming-indexes)
    -   [删除索引](#dropping-indexes)
    -   [外键约束](#foreign-key-constraints)
-   [事件](#events)

## 简介

迁移就像数据库的版本控制，允许团队定义并共享应用程序的数据库结构定义。
如果你曾经在拉取源码后，需要告诉队友手动在本地数据库中添加一个列，那么你就遇到了迁移要解决的问题。

Laravel 的 `Schema` [facade](/docs/laravel/12.x/facades) 提供了数据库无关的支持，
可以在 Laravel 支持的所有数据库系统中创建和操作表。
通常，迁移会使用这个 facade 来创建和修改数据库表和列。

## 生成迁移

你可以使用 `make:migration` [Artisan 命令](/docs/laravel/12.x/artisan) 来生成数据库迁移。
新的迁移文件会被放置在 `database/migrations` 目录下。
每个迁移文件名包含时间戳，这使 Laravel 能够确定迁移的执行顺序：


```shell
php artisan make:migration create_flights_table
```

Laravel 会根据迁移的名称尝试猜测表名，以及迁移是否是创建新表。
如果 Laravel 能够从迁移名称中确定表名，它会在生成的迁移文件中预填指定的表名。
否则，你可以在迁移文件中手动指定表名。


如果你想为生成的迁移指定自定义路径，可以在执行 `make:migration` 命令时使用 `--path` 选项。
指定的路径应相对于应用程序的基础路径（base path）。

> [!注意]
> 迁移模板（migration stubs）可以通过 [stub 发布](/docs/laravel/12.x/artisan#stub-customization) 进行自定义。

### 合并迁移

随着应用程序的发展，你可能会随着时间积累越来越多的迁移。
这可能导致 `database/migrations` 目录膨胀，可能包含上百个迁移文件。

如果需要，你可以将这些迁移“合并”为一个单独的 SQL 文件。
要开始操作，可以执行 `schema:dump` 命令：

```shell
php artisan schema:dump

# 导出当前数据库结构，并修剪所有已有迁移...
php artisan schema:dump --prune
```

执行该命令时，Laravel 会将一个“schema”文件写入应用的 `database/schema` 目录。
该 schema 文件的名称将对应于数据库连接名称。

现在，当你尝试迁移数据库且没有其他迁移已执行时，
Laravel 会首先执行你正在使用的数据库连接的 schema 文件中的 SQL 语句。
在执行完 schema 文件中的 SQL 语句后，Laravel 会执行任何未包含在 schema dump 中的剩余迁移。

如果你的应用测试使用的数据库连接与本地开发时通常使用的不同，
你应确保已经使用该测试数据库连接导出过 schema 文件，这样测试才能构建数据库。
你可能希望在导出本地开发使用的数据库连接后执行：

```shell
php artisan schema:dump
php artisan schema:dump --database=testing --prune
```



你应该将数据库 schema 文件提交到版本控制，这样团队中新的开发者就可以快速创建应用程序的初始数据库结构。

> [!警告]
> 迁移合并（Migration Squashing）仅适用于 MariaDB、MySQL、PostgreSQL 和 SQLite 数据库，并使用数据库的命令行客户端。

## 迁移结构

一个迁移类包含两个方法：`up` 和 `down`。
-   `up` 方法用于向数据库添加新的表、列或索引
-   `down` 方法应当撤销 `up` 方法执行的操作

在这两个方法中，你可以使用 Laravel 的 schema 构建器（Schema Builder）以可读的方式创建和修改表。
要了解 schema 构建器的所有可用方法，[请查看其文档](#creating-tables)。

例如，下面的迁移创建了一个 `flights` 表：

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * 运行迁移
     */
    public function up(): void
    {
        Schema::create('flights', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('airline');
            $table->timestamps();
        });
    }

    /**
     * 回滚迁移
     */
    public function down(): void
    {
        Schema::drop('flights');
    }
};
```

#### 设置迁移连接（Setting the Migration Connection）

如果迁移将与应用默认数据库连接以外的数据库连接交互，
你应该在迁移中设置 `$connection` 属性：

```php
/**
 * 此迁移应使用的数据库连接
 *
 * @var string
 */
protected $connection = 'pgsql';

/**
 * 运行迁移
 */
public function up(): void
{
    // ...
}
```

#### 跳过迁移



有时一个迁移可能是为了支持尚未激活的功能，而你不希望它立即执行。
在这种情况下，你可以在迁移中定义一个 `shouldRun` 方法。
如果 `shouldRun` 方法返回 `false`，该迁移将会被跳过：

```php
use App\Models\Flights;
use Laravel\Pennant\Feature;

/**
 * 判断此迁移是否应该执行
 */
public function shouldRun(): bool
{
    return Feature::active(Flights::class);
}
```

## 运行迁移

要运行所有待执行的迁移，请执行 `migrate` Artisan 命令：

```shell
php artisan migrate
```

如果你想查看哪些迁移已经执行过，可以使用 `migrate:status` Artisan 命令：

```shell
php artisan migrate:status
```

如果你想查看迁移将要执行的 SQL 语句，但不实际运行迁移，可以为 `migrate` 命令提供 `--pretend` 标志：

```shell
php artisan migrate --pretend
```

#### 隔离迁移执行

如果你在多个服务器上部署应用，并在部署过程中运行迁移，
你很可能不希望两个服务器同时尝试迁移数据库。

为避免这种情况，你可以在执行 `migrate` 命令时使用 `--isolated` 选项。

当提供 `isolated` 选项时，Laravel 会使用应用的缓存驱动获取一个原子锁（atomic lock），然后再尝试运行迁移。
在锁被持有期间，其他尝试运行 `migrate` 命令的操作不会执行；
不过命令仍会以成功退出状态码结束：

```shell
php artisan migrate --isolated
```

> [!警告]
> 使用此功能时，你的应用必须使用 `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array` 作为默认缓存驱动。
并且，所有服务器必须与同一个中央缓存服务器通信。



#### 在生产环境强制运行迁移

某些迁移操作是破坏性的（destructive），这意味着它们可能导致数据丢失。
为了保护你在生产数据库上执行这些命令，执行前会提示确认。
如果想在不提示确认的情况下强制执行命令，可以使用 `--force` 标志：

```shell
php artisan migrate --force
```

### 回滚迁移

要回滚最近的一次迁移操作，可以使用 `rollback` Artisan 命令。
此命令会回滚最后一个“批次（batch）”的迁移，这个批次可能包含多个迁移文件：

```shell
php artisan migrate:rollback
```

你可以通过为 `rollback` 命令提供 `--step` 选项来回滚有限数量的迁移。
例如，以下命令将回滚最近五个迁移：

```shell
php artisan migrate:rollback --step=5
```

你也可以通过提供 `--batch` 选项回滚特定批次的迁移，其中 `batch` 选项对应于应用 `migrations` 数据表中的批次值。
例如，以下命令将回滚第 3 批次的所有迁移：

```shell
php artisan migrate:rollback --batch=3
```

如果你想查看回滚迁移将执行的 SQL 语句，但不实际执行，可以为 `migrate:rollback` 命令提供 `--pretend` 标志：

```shell
php artisan migrate:rollback --pretend
```

`migrate:reset` 命令会回滚应用的所有迁移：

```shell
php artisan migrate:reset
```


#### 使用单条命令回滚并迁移

`migrate:refresh` 命令会回滚所有迁移，然后再执行 `migrate` 命令。
此命令实际上会重新创建整个数据库：

```shell
php artisan migrate:refresh

# 刷新数据库并运行所有数据库填充（seed）...
php artisan migrate:refresh --seed
```

你可以通过为 `refresh` 命令提供 `--step` 选项回滚并重新迁移有限数量的迁移。
例如，以下命令将回滚并重新迁移最近五个迁移：

```shell
php artisan migrate:refresh --step=5
```

`migrate:fresh` 命令会删除数据库中的所有表，然后再执行 `migrate` 命令：

```shell
php artisan migrate:fresh

php artisan migrate:fresh --seed
```

默认情况下，`migrate:fresh` 命令仅删除默认数据库连接中的表。
但是，你可以使用 `--database` 选项指定应迁移的数据库连接。
数据库连接名称应对应应用 `database` [配置文件](/docs/laravel/12.x/configuration)中定义的连接：

```shell
php artisan migrate:fresh --database=admin
```

> [!警告]
> `migrate:fresh` 命令会删除数据库中所有表，无论表前缀是什么。
在开发共享数据库的应用时应谨慎使用此命令。

## 表

### 创建表

要创建一个新的数据库表，使用 `Schema` facade 的 `create` 方法。
`create` 方法接受两个参数：
-   第一个参数是表名
-   第二个参数是一个闭包（closure），接收一个 `Blueprint` 对象，可用于定义新表：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email');
    $table->timestamps();
});
```



在创建表时，你可以使用模式构建器（schema builder）的任意 [列方法](#creating-columns) 来定义表的列。

#### 判断表 / 列是否存在

你可以使用 `hasTable`、`hasColumn` 和 `hasIndex` 方法来判断表、列或索引是否存在：

```php
if (Schema::hasTable('users')) {
    // "users" 表存在...
}

if (Schema::hasColumn('users', 'email')) {
    // "users" 表存在并且有 "email" 列...
}

if (Schema::hasIndex('users', ['email'], 'unique')) {
    // "users" 表存在并且 "email" 列上有唯一索引...
}
```

#### 数据库连接和表选项

如果你希望在非应用默认数据库连接上执行模式操作，可使用 `connection` 方法：

```php
Schema::connection('sqlite')->create('users', function (Blueprint $table) {
    $table->id();
});
```

此外，还可以使用其他一些属性和方法来定义表的其他方面。
-   `engine` 属性可用于在 MariaDB 或 MySQL 中指定表的存储引擎：

```php
Schema::create('users', function (Blueprint $table) {
    $table->engine('InnoDB');

    // ...
});
```

`charset` 和 `collation` 属性可用于在 MariaDB 或 MySQL 中指定创建表的字符集和排序规则：

```php
Schema::create('users', function (Blueprint $table) {
    $table->charset('utf8mb4');
    $table->collation('utf8mb4_unicode_ci');

    // ...
});
```

-   `temporary` 方法可用于指示表为“临时表”。
    临时表只在当前连接的数据库会话中可见，并且在连接关闭时会自动删除：

```php
Schema::create('calculations', function (Blueprint $table) {
    $table->temporary();

    // ...
});
```



如果你希望为数据库表添加“注释”，可以调用表实例的 `comment` 方法。
表注释目前仅支持 MariaDB、MySQL 和 PostgreSQL：

```php
Schema::create('calculations', function (Blueprint $table) {
    $table->comment('Business calculations');

    // ...
});
```

### 更新表

`Schema` facade 的 `table` 方法可用于更新现有表。
和 `create` 方法一样，`table` 方法接受两个参数：表名以及一个闭包（closure），闭包接收一个 `Blueprint` 实例，可用于向表中添加列或索引：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```

### 重命名 / 删除表

要重命名现有数据库表，使用 `rename` 方法：

```php
use Illuminate\Support\Facades\Schema;

Schema::rename($from, $to);
```

要删除现有表，可使用 `drop` 或 `dropIfExists` 方法：

```php
Schema::drop('users');

Schema::dropIfExists('users');
```

#### 带外键的表重命名

在重命名表之前，你应该确认表上的外键约束在迁移文件中有明确的名称，而不是让 Laravel 使用约定生成的名称。
否则，外键约束名称将引用旧的表名。

## 列

### 创建列

`Schema` facade 的 `table` 方法可用于更新现有表。
和 `create` 方法一样，`table` 方法接受两个参数：表名以及一个闭包（closure），闭包接收一个 `Illuminate\Database\Schema\Blueprint` 实例，可用于向表中添加列：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```



### 可用的列类型

Schema 构建器的 Blueprint 提供了多种方法，对应于你可以向数据库表中添加的不同列类型。
下面的表格列出了所有可用的方法：

<style>
    .collection-method-list > p {
        columns: 10.8em 3; -moz-columns: 10.8em 3; -webkit-columns: 10.8em 3;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .collection-method code {
        font-size: 14px;
    }

    .collection-method:not(.first-collection-method) {
        margin-top: 50px;
    }
</style>

#### 布尔类型（Boolean Types）

<div class="collection-method-list" markdown="1">

[boolean](#column-method-boolean)

</div>

#### 字符串与文本类型（String & Text Types）

<div class="collection-method-list" markdown="1">

[char](#column-method-char)
[longText](#column-method-longText)
[mediumText](#column-method-mediumText)
[string](#column-method-string)
[text](#column-method-text)
[tinyText](#column-method-tinyText)

</div>

#### 数值类型（Numeric Types）

<div class="collection-method-list" markdown="1">

[bigIncrements](#column-method-bigIncrements)
[bigInteger](#column-method-bigInteger)
[decimal](#column-method-decimal)
[double](#column-method-double)
[float](#column-method-float)
[id](#column-method-id)
[increments](#column-method-increments)
[integer](#column-method-integer)
[mediumIncrements](#column-method-mediumIncrements)
[mediumInteger](#column-method-mediumInteger)
[smallIncrements](#column-method-smallIncrements)
[smallInteger](#column-method-smallInteger)
[tinyIncrements](#column-method-tinyIncrements)
[tinyInteger](#column-method-tinyInteger)
[unsignedBigInteger](#column-method-unsignedBigInteger)
[unsignedInteger](#column-method-unsignedInteger)
[unsignedMediumInteger](#column-method-unsignedMediumInteger)
[unsignedSmallInteger](#column-method-unsignedSmallInteger)
[unsignedTinyInteger](#column-method-unsignedTinyInteger)

</div>

#### 日期与时间类型（Date & Time Types）

<div class="collection-method-list" markdown="1">

[dateTime](#column-method-dateTime)
[dateTimeTz](#column-method-dateTimeTz)
[date](#column-method-date)
[time](#column-method-time)
[timeTz](#column-method-timeTz)
[timestamp](#column-method-timestamp)
[timestamps](#column-method-timestamps)
[timestampsTz](#column-method-timestampsTz)
[softDeletes](#column-method-softDeletes)
[softDeletesTz](#column-method-softDeletesTz)
[year](#column-method-year)

</div>

#### 二进制类型（Binary Types）

<div class="collection-method-list" markdown="1">

[binary](#column-method-binary)

</div>

#### 对象与 JSON 类型（Object & Json Types）

<div class="collection-method-list" markdown="1">

[json](#column-method-json)
[jsonb](#column-method-jsonb)

</div>

#### UUID 与 ULID 类型（UUID & ULID Types）

<div class="collection-method-list" markdown="1">

[ulid](#column-method-ulid)
[ulidMorphs](#column-method-ulidMorphs)
[uuid](#column-method-uuid)
[uuidMorphs](#column-method-uuidMorphs)
[nullableUlidMorphs](#column-method-nullableUlidMorphs)
[nullableUuidMorphs](#column-method-nullableUuidMorphs)

</div>

#### 空间类型（Spatial Types）

<div class="collection-method-list" markdown="1">

[geography](#column-method-geography)
[geometry](#column-method-geometry)

</div>



#### 关系类型（Relationship Types）

<div class="collection-method-list" markdown="1">

[foreignId](#column-method-foreignId)
[foreignIdFor](#column-method-foreignIdFor)
[foreignUlid](#column-method-foreignUlid)
[foreignUuid](#column-method-foreignUuid)
[morphs](#column-method-morphs)
[nullableMorphs](#column-method-nullableMorphs)

</div>

#### 特殊类型（Specialty Types）

<div class="collection-method-list" markdown="1">

[enum](#column-method-enum)
[set](#column-method-set)
[macAddress](#column-method-macAddress)
[ipAddress](#column-method-ipAddress)
[rememberToken](#column-method-rememberToken)
[vector](#column-method-vector)

</div>

#### `bigIncrements()` {.collection-method .first-collection-method}

`bigIncrements` 方法创建一个自增的 `UNSIGNED BIGINT`（主键）等效列：

```php
$table->bigIncrements('id');
```

#### `bigInteger()` {.collection-method}

`bigInteger` 方法创建一个 `BIGINT` 等效列：

```php
$table->bigInteger('votes');
```

#### `binary()` {.collection-method}

`binary` 方法创建一个 `BLOB` 等效列：

```php
$table->binary('photo');
```

在使用 MySQL、MariaDB 或 SQL Server 时，你可以传入 `length` 和 `fixed` 参数来创建 `VARBINARY` 或 `BINARY` 等效列：

```php
$table->binary('data', length: 16); // VARBINARY(16)

$table->binary('data', length: 16, fixed: true); // BINARY(16)
```

#### `boolean()` {.collection-method}

`boolean` 方法创建一个 `BOOLEAN` 等效列：

```php
$table->boolean('confirmed');
```

#### `char()` {.collection-method}

`char` 方法创建一个固定长度的 `CHAR` 等效列：

```php
$table->char('name', length: 100);
```

#### `dateTimeTz()` {.collection-method}

`dateTimeTz` 方法创建一个带时区的 `DATETIME` 等效列，可选精度为小数秒：

```php
$table->dateTimeTz('created_at', precision: 0);
```

#### `dateTime()` {.collection-method}

`dateTime` 方法创建一个 `DATETIME` 等效列，可选精度为小数秒：

```php
$table->dateTime('created_at', precision: 0);
```

#### `date()` {.collection-method}

`date` 方法创建一个 `DATE` 等效列：

```php
$table->date('created_at');
```



#### `decimal()` {.collection-method}

`decimal` 方法创建一个 `DECIMAL` 等效列，指定精度（总位数）和小数位数（小数位）：

```php
$table->decimal('amount', total: 8, places: 2);
```

#### `double()` {.collection-method}

`double` 方法创建一个 `DOUBLE` 等效列：

```php
$table->double('amount');
```

#### `enum()` {.collection-method}

`enum` 方法创建一个 `ENUM` 等效列，指定允许的有效值：

```php
$table->enum('difficulty', ['easy', 'hard']);
```

#### `float()` {.collection-method}

`float` 方法创建一个 `FLOAT` 等效列，指定精度

```php
$table->float('amount', precision: 53);
```

#### `foreignId()` {.collection-method}

`foreignId` 方法创建一个 `UNSIGNED BIGINT` 等效列：

```php
$table->foreignId('user_id');
```

#### `foreignIdFor()` {.collection-method}

`foreignIdFor` 方法为指定模型类添加一个 `{column}_id` 等效列。列类型将根据模型主键类型分别为 `UNSIGNED BIGINT`、`CHAR(36)` 或 `CHAR(26)`：

```php
$table->foreignIdFor(User::class);
```

#### `foreignUlid()` {.collection-method}

`foreignUlid` 方法创建一个 `ULID` 等效列：

```php
$table->foreignUlid('user_id');
```

#### `foreignUuid()` {.collection-method}

`foreignUuid` 方法创建一个 `UUID` 等效列：

```php
$table->foreignUuid('user_id');
```

#### `geography()` {.collection-method}

`geography` 方法创建一个 `GEOGRAPHY` 等效列，指定空间类型和 SRID（空间参考系统标识符）：

```php
$table->geography('coordinates', subtype: 'point', srid: 4326);
```

> [!注意]
> 空间类型支持取决于你的数据库驱动。如果你的应用使用 PostgreSQL 数据库，必须先安装 [PostGIS](https://postgis.net) 扩展，才能使用 `geography` 方法。



#### `geometry()` {.collection-method}

`geometry` 方法创建一个 `GEOMETRY` 等效列，指定空间类型和 SRID（空间参考系统标识符）：

```php
$table->geometry('positions', subtype: 'point', srid: 0);
```

> [!注意]
> 空间类型支持取决于你的数据库驱动。请参考数据库文档。如果你的应用使用 PostgreSQL 数据库，必须先安装 [PostGIS](https://postgis.net) 扩展，才能使用 `geometry` 方法。

#### `id()` {.collection-method}

`id` 方法是 `bigIncrements` 方法的别名。默认情况下，会创建一个 `id` 列；如果希望给列指定不同名称，也可以传入列名：

```php
$table->id();
```

#### `increments()` {.collection-method}

`increments` 方法创建一个自动递增的 `UNSIGNED INTEGER` 等效列，作为主键：

```php
$table->increments('id');
```

#### `integer()` {.collection-method}

`integer` 方法创建一个 `INTEGER` 等效列：

```php
$table->integer('votes');
```

#### `ipAddress()` {.collection-method}

`ipAddress` 方法创建一个 `VARCHAR` 等效列：

```php
$table->ipAddress('visitor');
```

使用 PostgreSQL 时，将创建一个 `INET` 列。

#### `json()` {.collection-method}

`json` 方法创建一个 `JSON` 等效列：

```php
$table->json('options');
```

使用 SQLite 时，将创建一个 `TEXT` 列。

#### `jsonb()` {.collection-method}

`jsonb` 方法创建一个 `JSONB` 等效列：

```php
$table->jsonb('options');
```

使用 SQLite 时，将创建一个 `TEXT` 列。

#### `longText()` {.collection-method}

`longText` 方法创建一个 `LONGTEXT` 等效列：

```php
$table->longText('description');
```



在使用 MySQL 或 MariaDB 时，可以为列应用 `binary` 字符集，以创建 `LONGBLOB` 等效列：

```php
$table->longText('data')->charset('binary'); // LONGBLOB
```

#### `macAddress()` {.collection-method}

`macAddress` 方法创建一个用于存储 MAC 地址的列。一些数据库系统（如 PostgreSQL）有专用的列类型存储此类数据，其他数据库系统会使用字符串等效列：

```php
$table->macAddress('device');
```

#### `mediumIncrements()` {.collection-method}

`mediumIncrements` 方法创建一个自动递增的 `UNSIGNED MEDIUMINT` 等效列，作为主键：

```php
$table->mediumIncrements('id');
```

#### `mediumInteger()` {.collection-method}

`mediumInteger` 方法创建一个 `MEDIUMINT` 等效列：

```php
$table->mediumInteger('votes');
```

#### `mediumText()` {.collection-method}

`mediumText` 方法创建一个 `MEDIUMTEXT` 等效列：

```php
$table->mediumText('description');
```

在使用 MySQL 或 MariaDB 时，可以为列应用 `binary` 字符集，以创建 `MEDIUMBLOB` 等效列：

```php
$table->mediumText('data')->charset('binary'); // MEDIUMBLOB
```

#### `morphs()` {.collection-method}

`morphs` 方法是一个便捷方法，会同时添加一个 `{column}_id` 等效列和一个 `{column}_type` `VARCHAR` 等效列。`{column}_id` 的列类型会根据模型主键类型为 `UNSIGNED BIGINT`、`CHAR(36)` 或 `CHAR(26)`。

此方法用于定义多态 [Eloquent 关系](/docs/laravel/12.x/eloquent-relationships) 所需的列。例如，以下示例会创建 `taggable_id` 和 `taggable_type` 列：

```php
$table->morphs('taggable');
```



#### `nullableMorphs()` {.collection-method}

此方法与 [morphs](#column-method-morphs) 方法类似，但创建的列将允许为空（nullable）：

```php
$table->nullableMorphs('taggable');
```

#### `nullableUlidMorphs()` {.collection-method}

此方法与 [ulidMorphs](#column-method-ulidMorphs) 方法类似，但创建的列将允许为空：

```php
$table->nullableUlidMorphs('taggable');
```

#### `nullableUuidMorphs()` {.collection-method}

此方法与 [uuidMorphs](#column-method-uuidMorphs) 方法类似，但创建的列将允许为空：

```php
$table->nullableUuidMorphs('taggable');
```

#### `rememberToken()` {.collection-method}

`rememberToken` 方法创建一个可为空的 `VARCHAR(100)` 等效列，用于存储当前的 “记住我” [认证令牌](/docs/laravel/12.x/authentication#remembering-users)：

```php
$table->rememberToken();
```

#### `set()` {.collection-method}

`set` 方法创建一个 `SET` 等效列，并指定可用的值列表：

```php
$table->set('flavors', ['strawberry', 'vanilla']);
```

#### `smallIncrements()` {.collection-method}

`smallIncrements` 方法创建一个自动递增的 `UNSIGNED SMALLINT` 等效列，作为主键：

```php
$table->smallIncrements('id');
```

#### `smallInteger()` {.collection-method}

`smallInteger` 方法创建一个 `SMALLINT` 等效列：

```php
$table->smallInteger('votes');
```

#### `softDeletesTz()` {.collection-method}

`softDeletesTz` 方法添加一个可为空的 `deleted_at` `TIMESTAMP`（带时区）等效列，可选择指定小数秒精度。此列用于存储 Eloquent “软删除” 功能所需的 `deleted_at` 时间戳：

```php
$table->softDeletesTz('deleted_at', precision: 0);
```

#### `softDeletes()` {.collection-method}

`softDeletes` 方法添加一个可为空的 `deleted_at` `TIMESTAMP` 等效列，可选择指定小数秒精度。此列用于存储 Eloquent “软删除” 功能所需的 `deleted_at` 时间戳：

```php
$table->softDeletes('deleted_at', precision: 0);
```



#### `string()` {.collection-method}

`string` 方法创建一个 `VARCHAR` 等效列，长度可指定：

```php
$table->string('name', length: 100);
```

#### `text()` {.collection-method}

`text` 方法创建一个 `TEXT` 等效列：

```php
$table->text('description');
```

在使用 MySQL 或 MariaDB 时，你可以将列的字符集设置为 `binary`，以创建 `BLOB` 等效列：

```php
$table->text('data')->charset('binary'); // BLOB
```

#### `timeTz()` {.collection-method}

`timeTz` 方法创建一个带时区的 `TIME` 等效列，可指定小数秒精度：

```php
$table->timeTz('sunrise', precision: 0);
```

#### `time()` {.collection-method}

`time` 方法创建一个 `TIME` 等效列，可指定小数秒精度：

```php
$table->time('sunrise', precision: 0);
```

#### `timestampTz()` {.collection-method}

`timestampTz` 方法创建一个带时区的 `TIMESTAMP` 等效列，可指定小数秒精度：

```php
$table->timestampTz('added_at', precision: 0);
```

#### `timestamp()` {.collection-method}

`timestamp` 方法创建一个 `TIMESTAMP` 等效列，可指定小数秒精度：

```php
$table->timestamp('added_at', precision: 0);
```

#### `timestampsTz()` {.collection-method}

`timestampsTz` 方法创建 `created_at` 和 `updated_at` 两个带时区的 `TIMESTAMP` 等效列，可指定小数秒精度：

```php
$table->timestampsTz(precision: 0);
```

#### `timestamps()` {.collection-method}

`timestamps` 方法创建 `created_at` 和 `updated_at` 两个 `TIMESTAMP` 等效列，可指定小数秒精度：

```php
$table->timestamps(precision: 0);
```

#### `tinyIncrements()` {.collection-method}

`tinyIncrements` 方法创建一个自动递增的 `UNSIGNED TINYINT` 等效列，作为主键：

```php
$table->tinyIncrements('id');
```



<a name="column-method-tinyInteger"></a>
#### `tinyInteger()` {.collection-method}

`tinyInteger` 方法创建一个等效于 `TINYINT` 的列：

```php
$table->tinyInteger('votes');
```

<a name="column-method-tinyText"></a>
#### `tinyText()` {.collection-method}

`tinyText` 方法创建一个等效于 `TINYTEXT` 的列：

```php
$table->tinyText('notes');
```

使用 MySQL 或 MariaDB 时，您可以对该列应用 `binary` 字符集以创建等效于 `TINYBLOB` 的列：

```php
$table->tinyText('data')->charset('binary'); // TINYBLOB
```

<a name="column-method-unsignedBigInteger"></a>
#### `unsignedBigInteger()` {.collection-method}

`unsignedBigInteger` 方法创建一个等效于 `UNSIGNED BIGINT` 的列：

```php
$table->unsignedBigInteger('votes');
```

<a name="column-method-unsignedInteger"></a>
#### `unsignedInteger()` {.collection-method}

`unsignedInteger` 方法创建一个等效于 `UNSIGNED INTEGER` 的列：

```php
$table->unsignedInteger('votes');
```

<a name="column-method-unsignedMediumInteger"></a>
#### `unsignedMediumInteger()` {.collection-method}

`unsignedMediumInteger` 方法创建一个等效于 `UNSIGNED MEDIUMINT` 的列：

```php
$table->unsignedMediumInteger('votes');
```

<a name="column-method-unsignedSmallInteger"></a>
#### `unsignedSmallInteger()` {.collection-method}

`unsignedSmallInteger` 方法创建一个等效于 `UNSIGNED SMALLINT` 的列：

```php
$table->unsignedSmallInteger('votes');
```

<a name="column-method-unsignedTinyInteger"></a>
#### `unsignedTinyInteger()` {.collection-method}

`unsignedTinyInteger` 方法创建一个等效于 `UNSIGNED TINYINT` 的列：

```php
$table->unsignedTinyInteger('votes');
```

<a name="column-method-ulidMorphs"></a>
#### `ulidMorphs()` {.collection-method}

`ulidMorphs` 方法是一个便捷方法，它会添加一个等效于 `{column}_id` `CHAR(26)` 的列和一个等效于 `{column}_type` `VARCHAR` 的列。

此方法旨在定义使用 ULID 标识符的多态 [Eloquent 关联](https://laravel.com/docs/laravel/12.x/eloquent-relationships) 所需的列时使用。 在以下示例中，将创建 `taggable_id` 和 `taggable_type` 列：

```php
$table->ulidMorphs('taggable');
```

<a name="column-method-uuidMorphs"></a>
#### `uuidMorphs()` {.collection-method}

`uuidMorphs` 方法是一个便捷方法，它会添加一个等效于 `{column}_id` `CHAR(36)` 的列和一个等效于 `{column}_type` `VARCHAR` 的列。

此方法旨在定义使用 UUID 标识符的多态 [Eloquent 关联](https://laravel.com/docs/laravel/12.x/eloquent-relationships) 所需的列时使用。 在以下示例中，将创建 `taggable_id` 和 `taggable_type` 列：

```php
$table->uuidMorphs('taggable');
```

<a name="column-method-ulid"></a>
#### `ulid()` {.collection-method}

`ulid` 方法创建一个等效于 `ULID` 的列：

```php
$table->ulid('id');
```

<a name="column-method-uuid"></a>
#### `uuid()` {.collection-method}

`uuid` 方法创建一个等效于 `UUID` 的列：

```php
$table->uuid('id');
```

<a name="column-method-vector"></a>
#### `vector()` {.collection-method}

`vector` 方法创建一个等效于 `vector` 的列：

```php
$table->vector('embedding', dimensions: 100);
```

<a name="column-method-year"></a>
#### `year()` {.collection-method}

`year` 方法创建一个等效于 `YEAR` 的列：

```php
$table->year('birth_year');
```

<a name="column-modifiers"></a>
### 列修饰符

除了上面列出的列类型之外，在向数据库表添加列时，您还可以使用几个列「修饰符」。 例如，要使列「可为空」，您可以使用 `nullable` 方法：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->string('email')->nullable();
});
```

下表包含所有可用的列修饰符。 此列表不包括 [索引修饰符](#creating-indexes)：

| 修饰符 | 描述 |
| --------------------------------------------- | ------------------------------------------------- |
| `->after('column')`  | 将列放置在另一个列「之后」（MariaDB / MySQL）。   |
| `->autoIncrement()`                 | 将 `INTEGER` 列设置为自增（主键）。|
| `->charset('utf8mb4')`              | 为列指定字符集（MariaDB / MySQL）。|
| `->collation('utf8mb4_unicode_ci')` | 为列指定排序规则。|
| `->comment('my comment')`           | 为列添加注释（MariaDB / MySQL / PostgreSQL）。 |
| `->default($value)`                 | 为列指定「默认」值。|
| `->first()`                         | 将列放置在表的「首位」（MariaDB / MySQL）。|
| `->from($integer)`                  | 设置自增字段的起始值（MariaDB / MySQL / PostgreSQL）。|
| `->invisible()`                     | 使列对 `SELECT *` 查询「不可见」（MariaDB / MySQL）。 |
| `->nullable($value = true)`         | 允许向列中插入 `NULL` 值。 |
| `->storedAs($expression)`           | 创建存储生成列（MariaDB / MySQL / PostgreSQL / SQLite）。  |
| `->unsigned()`                      | 将 `INTEGER` 列设置为 `UNSIGNED`（MariaDB / MySQL）。 |
| `->useCurrent()`                    | 将 `TIMESTAMP` 列的默认值设置为 `CURRENT_TIMESTAMP`。|
| `->useCurrentOnUpdate()`| 在记录更新时将 `TIMESTAMP` 列设置为使用 `CURRENT_TIMESTAMP`（MariaDB / MySQL）。 |
| `->virtualAs($expression)`          | 创建虚拟生成列（MariaDB / MySQL / SQLite）。 |
| `->generatedAs($expression)`        | 创建具有指定序列选项的标识列（PostgreSQL）。 |
| `->always()`                        | 定义标识列的序列值相对于输入的优先级（PostgreSQL）。 |


<a name="default-expressions"></a>
#### 默认表达式

`default` 修饰符接受值或 `Illuminate\Database\Query\Expression` 实例。 使用 `Expression` 实例将阻止 Laravel 用引号包裹值，并允许您使用数据库特定的函数。 这在需要为 JSON 列分配默认值时特别有用：

```php
<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Query\Expression;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration
{
    /**
     * 执行迁移
     */
    public function up(): void
    {
        Schema::create('flights', function (Blueprint $table) {
            $table->id();
            $table->json('movies')->default(new Expression('(JSON_ARRAY())'));
            $table->timestamps();
        });
    }
};
```

> [!警告]
> 对默认表达式的支持取决于您的数据库驱动、数据库版本和字段类型。 请参阅您的数据库文档。

<a name="column-order"></a>
#### 列顺序

使用 MariaDB 或 MySQL 数据库时，可以使用 `after` 方法在模式中的现有列之后添加列：

```php
$table->after('password', function (Blueprint $table) {
    $table->string('address_line1');
    $table->string('address_line2');
    $table->string('city');
});
```

<a name="modifying-columns"></a>
### 修改列

`change` 方法允许您修改现有列的类型和属性。 例如，您可能希望增加 `string` 列的大小。 要查看 `change` 方法的实际效果，让我们将 `name` 列的大小从 25 增加到 50。 为此，我们只需定义列的新状态，然后调用 `change` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->string('name', 50)->change();
});
```

修改列时，必须在列定义中显式包含您想要保留的所有修饰符 - 任何缺失的属性都将被移除。 例如，要保留 `unsigned` 、 `default` 和 `comment` 属性，在更改列时必须显式调用每个修饰符：

```php
Schema::table('users', function (Blueprint $table) {
    $table->integer('votes')->unsigned()->default(1)->comment('my comment')->change();
});
```

`change` 方法不会更改列的索引。 因此，您可以在修改列时使用索引修饰符来显式添加或删除索引：

```php
// 添加索引...
$table->bigIncrements('id')->primary()->change();

// 删除索引...
$table->char('postal_code', 10)->unique(false)->change();
```

<a name="renaming-columns"></a>
### 重命名列

要重命名列，您可以使用模式构建器提供的 `renameColumn` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->renameColumn('from', 'to');
});
```

<a name="dropping-columns"></a>
### 删除列

要删除列，您可以在模式构建器上使用 `dropColumn` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->dropColumn('votes');
});
```

您可以通过将列名数组传递给 `dropColumn` 方法来从表中删除多个列：

```php
Schema::table('users', function (Blueprint $table) {
    $table->dropColumn(['votes', 'avatar', 'location']);
});
```

<a name="available-command-aliases"></a>
#### 可用的命令别名

Laravel 提供了几个与删除常见类型列相关的便捷方法。 下表中描述了每种方法：

| 命令                             | 描述                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `$table->dropMorphs('morphable');`  | 删除 `morphable_id` 和 `morphable_type` 列。 |
| `$table->dropRememberToken();`      | 删除 `remember_token` 列。                     |
| `$table->dropSoftDeletes();`        | 删除 `deleted_at` 列。                         |
| `$table->dropSoftDeletesTz();`      | `dropSoftDeletes()` 方法的别名。                  |
| `$table->dropTimestamps();`         | 删除 `created_at` 和 `updated_at` 列。       |
| `$table->dropTimestampsTz();`       | `dropTimestamps()` 方法的别名。                   |

<a name="indexes"></a>
## 索引

<a name="creating-indexes"></a>
### 创建索引

Laravel 模式构建器支持多种类型的索引。 以下示例创建了一个新的 `email` 列并指定其值应该是唯一的。 要创建索引，我们可以将 `unique` 方法链式调用到列定义上：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->string('email')->unique();
});
```

或者，您也可以在定义列之后创建索引。 为此，您应该在模式构建器蓝图对象上调用 `unique` 方法。 此方法接受应该创建唯一索引的列名：

```php
$table->unique('email');
```

您甚至可以将列数组传递给索引方法以创建复合索引：

```php
$table->index(['account_id', 'created_at']);
```

创建索引时，Laravel 会根据表名、列名和索引类型自动生成索引名称，但您可以将第二个参数传递给该方法以自行指定索引名称：

```php
$table->unique('email', 'unique_email');
```

<a name="available-index-types"></a>
#### 可用的索引类型

Laravel 的模式构建器蓝图类提供了用于创建 Laravel 支持的每种索引类型的方法。 每个索引方法都接受一个可选的第二个参数来指定索引的名称。 如果省略，名称将根据用于索引的表和列的名称以及索引类型派生。 下表中描述了每种可用的索引方法：

| 命令 | 描述 |
|------|------|
| `$table->primary('id');` | 添加主键。 |
| `$table->primary(['id', 'parent_id']);` | 添加复合主键。 |
| `$table->unique('email');` | 添加唯一索引。 |
| `$table->index('state');` | 添加普通索引。 |
| `$table->fullText('body');` | 添加全文索引（MariaDB / MySQL / PostgreSQL）。 |
| `$table->fullText('body')->language('english');` | 添加指定语言的全文索引（PostgreSQL）。 |
| `$table->spatialIndex('location');` | 添加空间索引（SQLite 除外）。 |


### 重命名索引

要重命名索引，可以使用 **Schema 构建器** 提供的 `renameIndex` 方法。
此方法的第一个参数是当前索引的名称，第二个参数是期望的新名称

```php
$table->renameIndex('from', 'to')
```

### 删除索引

要删除索引，你必须指定索引的名称。
默认情况下，Laravel 会基于 **表名、被索引的列名和索引类型** 自动生成索引名称。
下面是一些示例：


| 命令 | 描述 |
| --- | --- |
| `$table->dropPrimary('users_id_primary');` | 删除 `users` 表上的主键。 |
| `$table->dropUnique('users_email_unique');` | 删除 `users` 表上的唯一索引。 |
| `$table->dropIndex('geo_state_index');` | 删除 `geo` 表上的普通索引。 |
| `$table->dropFullText('posts_body_fulltext');` | 删除 `posts` 表上的全文索引。 |
| `$table->dropSpatialIndex('geo_location_spatialindex');` | 删除 `geo` 表上的空间索引（SQLite 除外）。 |

</div>

如果你在删除索引的方法里传递的是 **列名数组**，Laravel 会根据表名、列名和索引类型自动推断出索引名：

```php
Schema::table('geo', function (Blueprint $table) {
    $table->dropIndex(['state']); // 删除索引 'geo_state_index'
});
```

### 外键约束

Laravel 也支持创建 **外键约束**，它可以在数据库层面强制 **参照完整性**。
例如，定义 `posts` 表中的 `user_id` 列，让它引用 `users` 表中的 `id` 列：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('posts', function (Blueprint $table) {
    $table->unsignedBigInteger('user_id');

    $table->foreign('user_id')->references('id')->on('users');
});
```



由于这种语法（前面的 `$table->unsignedBigInteger('user_id') ...`）比较冗长，Laravel 提供了更简洁的方法，这些方法基于约定，为开发者带来更好的体验。

当使用 `foreignId` 方法来创建列时，上面的例子可以改写为：

```php
Schema::table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained();
});
```

`foreignId` 方法会创建一个等同于 `UNSIGNED BIGINT` 的列，而 `constrained` 方法会利用约定来推断被引用的表和列。
如果你的数据表名不符合 Laravel 的约定，你可以手动将表名传给 `constrained` 方法。
此外，你也可以指定生成的索引所应当使用的名称：

```php
Schema::table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained(
        table: 'users', indexName: 'posts_user_id'
    );
});
```

你也可以为该外键约束的 **“on delete”** 和 **“on update”** 属性指定所需的操作：

```php
$table->foreignId('user_id')
    ->constrained()
    ->onUpdate('cascade')
    ->onDelete('cascade');
```

同时，Laravel 也为这些操作提供了一种更具表现力的替代语法：

<div class="overflow-auto">

| 方法 | 描述 |
| --- | --- |
| `$table->cascadeOnUpdate();` | 更新时应当级联。 |
| `$table->restrictOnUpdate();` | 更新时应当受限。 |
| `$table->nullOnUpdate();` | 更新时应将外键值设为 null。 |
| `$table->noActionOnUpdate();` | 更新时不采取任何动作。 |
| `$table->cascadeOnDelete();` | 删除时应当级联。 |
| `$table->restrictOnDelete();` | 删除时应当受限。 |
| `$table->nullOnDelete();` | 删除时应将外键值设为 null。 |
| `$table->noActionOnDelete();` | 如果存在子记录，则阻止删除。 |

</div>

任何额外的 [列修饰符](#column-modifiers) 都必须在 `constrained` 方法之前调用：

```php
$table->foreignId('user_id')
    ->nullable()
    ->constrained();
```



#### 删除外键

要删除一个外键，可以使用 `dropForeign` 方法，并将要删除的外键约束的名称作为参数传递。
外键约束的命名规则与索引相同。换句话说，外键约束的名称是基于**表名**和**约束中涉及的列名**，然后加上一个 `_foreign` 后缀：

```php
$table->dropForeign('posts_user_id_foreign');
```

另外，你也可以传递一个包含外键列名的数组给 `dropForeign` 方法。该数组会根据 Laravel 的约束命名约定被转换为外键约束名称：

```php
$table->dropForeign(['user_id']);
```

#### 切换外键约束

你可以在迁移（migrations）中通过以下方法启用或禁用外键约束：

```php
Schema::enableForeignKeyConstraints();

Schema::disableForeignKeyConstraints();

Schema::withoutForeignKeyConstraints(function () {
    // 在这个闭包中，外键约束被禁用...
});
```

> [!警告]
> SQLite 默认禁用外键约束。
当使用 SQLite 时，请确保在数据库配置中 [启用外键支持](/docs/laravel/12.x/database#configuration)，然后再尝试在迁移中创建它们。

## 事件

为了方便起见，每个迁移操作都会派发一个 [事件](/docs/laravel/12.x/events)。
下面所有事件类都继承自基类 `Illuminate\Database\Events\MigrationEvent`：

<div class="overflow-auto">

| 类名 | 描述 |
| --- | --- |
| `Illuminate\Database\Events\MigrationsStarted` | 一批迁移即将被执行。 |
| `Illuminate\Database\Events\MigrationsEnded` | 一批迁移已经执行完毕。 |
| `Illuminate\Database\Events\MigrationStarted` | 单个迁移即将被执行。 |
| `Illuminate\Database\Events\MigrationEnded` | 单个迁移已经执行完毕。 |
| `Illuminate\Database\Events\NoPendingMigrations` | 迁移命令未发现任何待执行的迁移。 |
| `Illuminate\Database\Events\SchemaDumped` | 数据库结构（schema）导出已完成。 |
| `Illuminate\Database\Events\SchemaLoaded` | 已加载了一个现有的数据库结构（schema）导出。 |

</div>

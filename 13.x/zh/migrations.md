# 数据库：迁移

- [简介](#introduction)
- [生成迁移](#generating-migrations)
    - [合并迁移](#squashing-migrations)
- [迁移结构](#migration-structure)
- [运行迁移](#running-migrations)
    - [回滚迁移](#rolling-back-migrations)
- [表](#tables)
    - [创建表](#creating-tables)
    - [更新表](#updating-tables)
    - [重命名与删除表](#renaming-and-dropping-tables)
- [列](#columns)
    - [创建列](#creating-columns)
    - [可用列类型](#available-column-types)
    - [列修饰符](#column-modifiers)
    - [修改列](#modifying-columns)
    - [重命名列](#renaming-columns)
    - [删除列](#dropping-columns)
- [索引](#indexes)
    - [创建索引](#creating-indexes)
    - [重命名索引](#renaming-indexes)
    - [删除索引](#dropping-indexes)
    - [外键约束](#foreign-key-constraints)
- [事件](#events)

<a name="introduction"></a>
## 简介

迁移就像数据库的版本控制，让团队能够定义和共享应用的数据库结构。如果你曾经需要告诉队友，在拉取代码更改后手动向本地数据库添加一列，那么你就遇到了数据库迁移要解决的问题。

Laravel 的 `Schema` [门面](/docs/{{version}}/facades)提供了不依赖具体数据库的接口，可以在 Laravel 支持的所有数据库系统中创建和操作表。迁移通常使用此门面创建和修改数据库表及列。

<a name="generating-migrations"></a>
## 生成迁移

你可以使用 `make:migration` [Artisan 命令](/docs/{{version}}/artisan)生成数据库迁移。新迁移文件会放在 `database/migrations` 目录中。每个文件名都包含时间戳，Laravel 据此确定迁移的执行顺序：

```shell
php artisan make:migration create_flights_table
```

Laravel 会根据迁移名称推断表名，以及该迁移是否用于创建新表。如果能够确定表名，就会将其预填到生成的迁移文件中。否则，你可以在迁移文件中手动指定表名。

如果希望自定义生成迁移的路径，可以在执行 `make:migration` 时使用 `--path` 选项。该路径应相对于应用的根目录。

> [!NOTE]
> 你可以通过[发布 stub 模板](/docs/{{version}}/artisan#stub-customization)来自定义迁移模板。

<a name="squashing-migrations"></a>
### 合并迁移

随着应用不断开发，迁移文件会越来越多，`database/migrations` 目录中可能积累数百个文件。你可以将这些迁移「合并」为一个 SQL 文件。首先执行 `schema:dump` 命令：

```shell
php artisan schema:dump

# 导出当前数据库结构，并清理所有现有迁移……
php artisan schema:dump --prune
```

执行该命令后，Laravel 会将数据库结构文件写入应用的 `database/schema` 目录，文件名与数据库连接对应。此后，如果数据库尚未执行过任何迁移，Laravel 会先执行当前连接对应的结构文件中的 SQL 语句，再执行未包含在结构导出文件中的剩余迁移。

如果应用测试使用的数据库连接与本地开发时不同，应确保也为测试连接导出数据库结构文件，以便测试能够构建数据库。你可以在导出本地开发连接的结构后再执行此操作：

```shell
php artisan schema:dump
php artisan schema:dump --database=testing --prune
```

应将数据库结构文件提交到版本控制，让新加入团队的开发者能够快速创建应用的初始数据库结构。

> [!WARNING]
> 合并迁移仅适用于 MariaDB、MySQL、PostgreSQL 和 SQLite，并且需要使用数据库的命令行客户端。

<a name="migration-structure"></a>
## 迁移结构

迁移类包含 `up` 和 `down` 两个方法。`up` 用于向数据库添加表、列或索引，`down` 则应撤销 `up` 执行的操作。

在这两个方法中，你可以使用 Laravel 数据库结构构建器，以清晰的语法创建和修改表。关于 `Schema` 构建器的所有可用方法，请[参阅其文档](#creating-tables)。例如，以下迁移会创建一个 `flights` 表：

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * 运行迁移。
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
     * 回滚迁移。
     */
    public function down(): void
    {
        Schema::drop('flights');
    }
};
```

<a name="setting-the-migration-connection"></a>
#### 设置迁移使用的连接

如果迁移需要使用应用默认连接以外的数据库连接，应设置迁移的 `$connection` 属性：

```php
/**
 * 迁移应使用的数据库连接。
 *
 * @var string
 */
protected $connection = 'pgsql';

/**
 * 运行迁移。
 */
public function up(): void
{
    // ...
}
```

<a name="skipping-migrations"></a>
#### 跳过迁移

有时，迁移用于支持尚未启用的功能，你可能不希望立即运行它。这时可以在迁移中定义 `shouldRun` 方法。如果该方法返回 `false`，就会跳过此迁移：

```php
use App\Models\Flight;
use Laravel\Pennant\Feature;

/**
 * 判断是否应运行此迁移。
 */
public function shouldRun(): bool
{
    return Feature::active(Flight::class);
}
```

<a name="running-migrations"></a>
## 运行迁移

要运行所有待执行的迁移，请执行 `migrate` Artisan 命令：

```shell
php artisan migrate
```

要查看哪些迁移已执行、哪些仍待执行，可以使用 `migrate:status` Artisan 命令：

```shell
php artisan migrate:status
```

向 `migrate` 命令传入 `--step` 选项后，每个迁移都会作为独立批次执行，方便之后通过 `migrate:rollback` 命令逐个回滚：

```shell
php artisan migrate --step
```

如果希望查看迁移将执行的 SQL 语句，而不实际运行迁移，可以为 `migrate` 命令添加 `--pretend` 标志：

```shell
php artisan migrate --pretend
```

<a name="isolating-migration-execution"></a>
#### 隔离迁移执行

如果将应用部署到多台服务器，并在部署过程中运行迁移，通常应避免两台服务器同时迁移数据库。调用 `migrate` 命令时，可以使用 `isolated` 选项来避免这种情况。

使用 `isolated` 选项后，Laravel 会先通过应用的缓存驱动获取原子锁，再运行迁移。持锁期间，其他 `migrate` 命令不会执行迁移，但仍会以成功状态码退出：

```shell
php artisan migrate --isolated
```

> [!WARNING]
> 使用此功能时，应用的默认缓存驱动必须为 `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array`，并且所有服务器都必须连接到同一个中央缓存服务器。

<a name="forcing-migrations-to-run-in-production"></a>
#### 在生产环境强制运行迁移

某些迁移操作可能导致数据丢失。为防止误操作生产数据库，执行这些命令前会要求确认。如果要跳过提示并强制执行，可以使用 `--force` 标志：

```shell
php artisan migrate --force
```

<a name="rolling-back-migrations"></a>
### 回滚迁移

要回滚最近一次迁移操作，可以使用 `rollback` Artisan 命令。该命令会回滚最后一个「批次」的迁移，其中可能包含多个迁移文件：

```shell
php artisan migrate:rollback
```

你可以通过 `rollback` 命令的 `step` 选项，只回滚指定数量的迁移。例如，以下命令会回滚最近五个迁移：

```shell
php artisan migrate:rollback --step=5
```

你也可以使用 `rollback` 命令的 `batch` 选项回滚指定批次。该选项对应应用中 `migrations` 数据表的批次值。例如，以下命令会回滚第 3 批次的所有迁移：

```shell
php artisan migrate:rollback --batch=3
```

如果希望查看回滚将执行的 SQL 语句，而不实际运行，可以为 `migrate:rollback` 命令添加 `--pretend` 标志：

```shell
php artisan migrate:rollback --pretend
```

`migrate:reset` 命令会回滚应用的所有迁移：

```shell
php artisan migrate:reset
```

<a name="roll-back-migrate-using-a-single-command"></a>
#### 用一条命令回滚并重新迁移

`migrate:refresh` 命令会回滚所有迁移，再执行 `migrate` 命令，相当于重新创建整个数据库：

```shell
php artisan migrate:refresh

# 刷新数据库，并运行所有数据库填充……
php artisan migrate:refresh --seed
```

你可以通过 `refresh` 命令的 `step` 选项，只回滚并重新执行指定数量的迁移。例如，以下命令会回滚并重新执行最近五个迁移：

```shell
php artisan migrate:refresh --step=5
```

<a name="drop-all-tables-migrate"></a>
#### 删除所有表并运行迁移

`migrate:fresh` 命令会删除数据库中的所有表，再执行 `migrate` 命令：

```shell
php artisan migrate:fresh

php artisan migrate:fresh --seed
```

默认情况下，`migrate:fresh` 只删除默认数据库连接中的表。你可以通过 `--database` 选项指定要迁移的连接。连接名称应对应应用的 `database` [配置文件](/docs/{{version}}/configuration)中定义的连接：

```shell
php artisan migrate:fresh --database=admin
```

> [!WARNING]
> `migrate:fresh` 会删除数据库中的所有表，不区分表前缀。如果数据库与其他应用共用，应谨慎使用此命令。

<a name="tables"></a>
## 表

<a name="creating-tables"></a>
### 创建表

要创建数据库表，请使用 `Schema` 门面的 `create` 方法。该方法接受两个参数：第一个是表名，第二个是接收 `Blueprint` 对象的闭包，你可以在闭包中定义新表：

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

创建表时，可以使用数据库结构构建器提供的各种[列方法](#creating-columns)定义表中的列。

<a name="determining-table-column-existence"></a>
#### 判断表或列是否存在

你可以使用 `hasTable`、`hasColumn` 和 `hasIndex` 方法，判断表、列或索引是否存在：

```php
if (Schema::hasTable('users')) {
    // 「users」表存在……
}

if (Schema::hasColumn('users', 'email')) {
    // 「users」表存在，并且包含「email」列……
}

if (Schema::hasIndex('users', ['email'], 'unique')) {
    // 「users」表存在，并且「email」列有唯一索引……
}
```

<a name="database-connection-table-options"></a>
#### 数据库连接和表选项

要在应用默认连接以外的数据库连接上操作数据库结构，请使用 `connection` 方法：

```php
Schema::connection('sqlite')->create('users', function (Blueprint $table) {
    $table->id();
});
```

你还可以通过其他属性和方法设置建表选项。使用 MariaDB 或 MySQL 时，可以通过 `engine` 属性指定表的存储引擎：

```php
Schema::create('users', function (Blueprint $table) {
    $table->engine('InnoDB');

    // ...
});
```

使用 MariaDB 或 MySQL 时，可以通过 `charset` 和 `collation` 属性指定新表的字符集和排序规则：

```php
Schema::create('users', function (Blueprint $table) {
    $table->charset('utf8mb4');
    $table->collation('utf8mb4_unicode_ci');

    // ...
});
```

`temporary` 方法可以将表指定为「临时表」。临时表仅对当前连接的数据库会话可见，并在连接关闭时自动删除：

```php
Schema::create('calculations', function (Blueprint $table) {
    $table->temporary();

    // ...
});
```

要为数据库表添加「注释」，可以调用表实例的 `comment` 方法。目前仅 MariaDB、MySQL 和 PostgreSQL 支持表注释：

```php
Schema::create('calculations', function (Blueprint $table) {
    $table->comment('Business calculations');

    // ...
});
```

<a name="updating-tables"></a>
### 更新表

`Schema` 门面的 `table` 方法可以更新现有表。与 `create` 一样，该方法接受表名和闭包两个参数。闭包会接收一个 `Blueprint` 实例，你可以用它向表中添加列或索引：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```

<a name="renaming-and-dropping-tables"></a>
### 重命名与删除表

要重命名现有数据库表，请使用 `rename` 方法：

```php
use Illuminate\Support\Facades\Schema;

Schema::rename($from, $to);
```

要删除现有表，可以使用 `drop` 或 `dropIfExists` 方法：

```php
Schema::drop('users');

Schema::dropIfExists('users');
```

<a name="renaming-tables-with-foreign-keys"></a>
#### 重命名带有外键的表

重命名表之前，应确认迁移文件中已为表上的所有外键约束明确指定名称，而不是让 Laravel 按约定生成名称。否则，外键约束名称仍会引用旧表名。

<a name="columns"></a>
## 列

<a name="creating-columns"></a>
### 创建列

`Schema` 门面的 `table` 方法可以更新现有表。与 `create` 一样，该方法接受表名和闭包两个参数。闭包会接收一个 `Illuminate\Database\Schema\Blueprint` 实例，你可以用它向表中添加列：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->integer('votes');
});
```

<a name="available-column-types"></a>
### 可用列类型

数据库结构构建器的蓝图对象提供了多种方法，对应可添加到数据库表中的不同列类型。下方列出了所有可用方法：

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

<a name="booleans-method-list"></a>
#### 布尔类型

<div class="collection-method-list" markdown="1">

[boolean](#column-method-boolean)

</div>

<a name="strings-and-texts-method-list"></a>
#### 字符串与文本类型

<div class="collection-method-list" markdown="1">

[char](#column-method-char)
[longText](#column-method-longText)
[mediumText](#column-method-mediumText)
[string](#column-method-string)
[text](#column-method-text)
[tinyText](#column-method-tinyText)

</div>

<a name="numbers--method-list"></a>
#### 数值类型

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

<a name="dates-and-times-method-list"></a>
#### 日期与时间类型

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

<a name="binaries-method-list"></a>
#### 二进制类型

<div class="collection-method-list" markdown="1">

[binary](#column-method-binary)

</div>

<a name="object-and-jsons-method-list"></a>
#### 对象与 JSON 类型

<div class="collection-method-list" markdown="1">

[json](#column-method-json)
[jsonb](#column-method-jsonb)

</div>

<a name="uuids-and-ulids-method-list"></a>
#### UUID 与 ULID 类型

<div class="collection-method-list" markdown="1">

[ulid](#column-method-ulid)
[ulidMorphs](#column-method-ulidMorphs)
[uuid](#column-method-uuid)
[uuidMorphs](#column-method-uuidMorphs)
[nullableUlidMorphs](#column-method-nullableUlidMorphs)
[nullableUuidMorphs](#column-method-nullableUuidMorphs)

</div>

<a name="spatials-method-list"></a>
#### 空间类型

<div class="collection-method-list" markdown="1">

[geography](#column-method-geography)
[geometry](#column-method-geometry)

</div>

<a name="relationship-method-list"></a>
#### 关系类型

<div class="collection-method-list" markdown="1">

[foreignId](#column-method-foreignId)
[foreignIdFor](#column-method-foreignIdFor)
[foreignUlid](#column-method-foreignUlid)
[foreignUuid](#column-method-foreignUuid)
[foreignUuidFor](#column-method-foreignUuidFor)
[morphs](#column-method-morphs)
[nullableMorphs](#column-method-nullableMorphs)

</div>

<a name="specifics-method-list"></a>
#### 特殊类型

<div class="collection-method-list" markdown="1">

[enum](#column-method-enum)
[set](#column-method-set)
[macAddress](#column-method-macAddress)
[ipAddress](#column-method-ipAddress)
[rememberToken](#column-method-rememberToken)
[vector](#column-method-vector)

</div>

<a name="column-method-bigIncrements"></a>
<h4 class="collection-method first-collection-method"><code>bigIncrements()</code></h4>

`bigIncrements` 方法创建一个等效于 `UNSIGNED BIGINT` 的自增主键列：

```php
$table->bigIncrements('id');
```

<a name="column-method-bigInteger"></a>
<h4 class="collection-method"><code>bigInteger()</code></h4>

`bigInteger` 方法创建一个等效于 `BIGINT` 的列：

```php
$table->bigInteger('votes');
```

<a name="column-method-binary"></a>
<h4 class="collection-method"><code>binary()</code></h4>

`binary` 方法创建一个等效于 `BLOB` 的列：

```php
$table->binary('photo');
```

使用 MySQL、MariaDB 或 SQL Server 时，可以传入 `length` 和 `fixed` 参数，创建等效于 `VARBINARY` 或 `BINARY` 的列：

```php
$table->binary('data', length: 16); // VARBINARY(16)

$table->binary('data', length: 16, fixed: true); // BINARY(16)
```

<a name="column-method-boolean"></a>
<h4 class="collection-method"><code>boolean()</code></h4>

`boolean` 方法创建一个等效于 `BOOLEAN` 的列：

```php
$table->boolean('confirmed');
```

<a name="column-method-char"></a>
<h4 class="collection-method"><code>char()</code></h4>

`char` 方法创建一个等效于 `CHAR`、长度为指定值的列：

```php
$table->char('name', length: 100);
```

<a name="column-method-dateTimeTz"></a>
<h4 class="collection-method"><code>dateTimeTz()</code></h4>

`dateTimeTz` 方法创建一个等效于 `DATETIME`（带时区）的列，可以指定小数秒精度：

```php
$table->dateTimeTz('created_at', precision: 0);
```

<a name="column-method-dateTime"></a>
<h4 class="collection-method"><code>dateTime()</code></h4>

`dateTime` 方法创建一个等效于 `DATETIME` 的列，可以指定小数秒精度：

```php
$table->dateTime('created_at', precision: 0);
```

<a name="column-method-date"></a>
<h4 class="collection-method"><code>date()</code></h4>

`date` 方法创建一个等效于 `DATE` 的列：

```php
$table->date('created_at');
```

<a name="column-method-decimal"></a>
<h4 class="collection-method"><code>decimal()</code></h4>

`decimal` 方法创建一个等效于 `DECIMAL` 的列，并指定精度（总位数）和标度（小数位数）：

```php
$table->decimal('amount', total: 8, places: 2);
```

<a name="column-method-double"></a>
<h4 class="collection-method"><code>double()</code></h4>

`double` 方法创建一个等效于 `DOUBLE` 的列：

```php
$table->double('amount');
```

<a name="column-method-enum"></a>
<h4 class="collection-method"><code>enum()</code></h4>

`enum` 方法创建一个等效于 `ENUM` 的列，并指定允许的值：

```php
$table->enum('difficulty', ['easy', 'hard']);
```

你也可以使用 `Enum::cases()` 方法，无需手动定义允许值的数组：

```php
use App\Enums\Difficulty;

$table->enum('difficulty', Difficulty::cases());
```

<a name="column-method-float"></a>
<h4 class="collection-method"><code>float()</code></h4>

`float` 方法创建一个等效于 `FLOAT`、精度为指定值的列：

```php
$table->float('amount', precision: 53);
```

<a name="column-method-foreignId"></a>
<h4 class="collection-method"><code>foreignId()</code></h4>

`foreignId` 方法创建一个等效于 `UNSIGNED BIGINT` 的列：

```php
$table->foreignId('user_id');
```

<a name="column-method-foreignIdFor"></a>
<h4 class="collection-method"><code>foreignIdFor()</code></h4>

`foreignIdFor` 方法为指定模型类添加一个 `{column}_id` 列。根据模型主键的类型，列类型会是 `UNSIGNED BIGINT`、`CHAR(36)` 或 `CHAR(26)`：

```php
$table->foreignIdFor(User::class);
```

<a name="column-method-foreignUlid"></a>
<h4 class="collection-method"><code>foreignUlid()</code></h4>

`foreignUlid` 方法创建一个等效于 `ULID` 的列：

```php
$table->foreignUlid('user_id');
```

<a name="column-method-foreignUuid"></a>
<h4 class="collection-method"><code>foreignUuid()</code></h4>

`foreignUuid` 方法创建一个等效于 `UUID` 的列：

```php
$table->foreignUuid('user_id');
```

<a name="column-method-foreignUuidFor"></a>
<h4 class="collection-method"><code>foreignUuidFor()</code></h4>

`foreignUuidFor` 方法为指定模型类添加一个等效于 UUID 的 `{column}_id` 列：

```php
$table->foreignUuidFor(User::class);
```

<a name="column-method-geography"></a>
<h4 class="collection-method"><code>geography()</code></h4>

`geography` 方法创建一个等效于 `GEOGRAPHY` 的列，并指定空间类型和 SRID（空间参考系统标识符）：

```php
$table->geography('coordinates', subtype: 'point', srid: 4326);
```

> [!NOTE]
> 空间类型的支持取决于数据库驱动，请参阅相应数据库的文档。如果应用使用 PostgreSQL，必须先安装 [PostGIS](https://postgis.net) 扩展，才能使用 `geography` 方法。

<a name="column-method-geometry"></a>
<h4 class="collection-method"><code>geometry()</code></h4>

`geometry` 方法创建一个等效于 `GEOMETRY` 的列，并指定空间类型和 SRID（空间参考系统标识符）：

```php
$table->geometry('positions', subtype: 'point', srid: 0);
```

> [!NOTE]
> 空间类型的支持取决于数据库驱动，请参阅相应数据库的文档。如果应用使用 PostgreSQL，必须先安装 [PostGIS](https://postgis.net) 扩展，才能使用 `geometry` 方法。

<a name="column-method-id"></a>
<h4 class="collection-method"><code>id()</code></h4>

`id` 方法是 `bigIncrements` 的别名，默认创建名为 `id` 的列。你也可以传入列名，为其指定其他名称：

```php
$table->id();
```

<a name="column-method-increments"></a>
<h4 class="collection-method"><code>increments()</code></h4>

`increments` 方法创建一个等效于 `UNSIGNED INTEGER` 的自增主键列：

```php
$table->increments('id');
```

<a name="column-method-integer"></a>
<h4 class="collection-method"><code>integer()</code></h4>

`integer` 方法创建一个等效于 `INTEGER` 的列：

```php
$table->integer('votes');
```

<a name="column-method-ipAddress"></a>
<h4 class="collection-method"><code>ipAddress()</code></h4>

`ipAddress` 方法创建一个等效于 `VARCHAR` 的列：

```php
$table->ipAddress('visitor');
```

使用 PostgreSQL 时，会创建 `INET` 列。

<a name="column-method-json"></a>
<h4 class="collection-method"><code>json()</code></h4>

`json` 方法创建一个等效于 `JSON` 的列：

```php
$table->json('options');
```

使用 SQLite 时，会创建 `TEXT` 列。

<a name="column-method-jsonb"></a>
<h4 class="collection-method"><code>jsonb()</code></h4>

`jsonb` 方法创建一个等效于 `JSONB` 的列：

```php
$table->jsonb('options');
```

使用 SQLite 时，会创建 `TEXT` 列。

<a name="column-method-longText"></a>
<h4 class="collection-method"><code>longText()</code></h4>

`longText` 方法创建一个等效于 `LONGTEXT` 的列：

```php
$table->longText('description');
```

使用 MySQL 或 MariaDB 时，可以将列的字符集设为 `binary`，创建等效于 `LONGBLOB` 的列：

```php
$table->longText('data')->charset('binary'); // LONGBLOB
```

<a name="column-method-macAddress"></a>
<h4 class="collection-method"><code>macAddress()</code></h4>

`macAddress` 方法创建一个用于存储 MAC 地址的列。PostgreSQL 等数据库系统具有专门存储此类数据的列类型，其他数据库系统则使用等效的字符串列：

```php
$table->macAddress('device');
```

<a name="column-method-mediumIncrements"></a>
<h4 class="collection-method"><code>mediumIncrements()</code></h4>

`mediumIncrements` 方法创建一个等效于 `UNSIGNED MEDIUMINT` 的自增主键列：

```php
$table->mediumIncrements('id');
```

<a name="column-method-mediumInteger"></a>
<h4 class="collection-method"><code>mediumInteger()</code></h4>

`mediumInteger` 方法创建一个等效于 `MEDIUMINT` 的列：

```php
$table->mediumInteger('votes');
```

<a name="column-method-mediumText"></a>
<h4 class="collection-method"><code>mediumText()</code></h4>

`mediumText` 方法创建一个等效于 `MEDIUMTEXT` 的列：

```php
$table->mediumText('description');
```

使用 MySQL 或 MariaDB 时，可以将列的字符集设为 `binary`，创建等效于 `MEDIUMBLOB` 的列：

```php
$table->mediumText('data')->charset('binary'); // MEDIUMBLOB
```

<a name="column-method-morphs"></a>
<h4 class="collection-method"><code>morphs()</code></h4>

`morphs` 是一个便捷方法，会添加一个等效于 `VARCHAR` 的 `{column}_type` 列和一个 `{column}_id` 列。根据模型主键的类型，`{column}_id` 的列类型会是 `UNSIGNED BIGINT`、`CHAR(36)` 或 `CHAR(26)`。

该方法用于定义多态 [Eloquent 关系](/docs/{{version}}/eloquent-relationships)所需的列。以下示例会创建 `taggable_type` 和 `taggable_id` 列：

```php
$table->morphs('taggable');
```

<a name="column-method-nullableMorphs"></a>
<h4 class="collection-method"><code>nullableMorphs()</code></h4>

该方法与 [morphs](#column-method-morphs) 类似，但创建的列允许为 `null`：

```php
$table->nullableMorphs('taggable');
```

<a name="column-method-nullableUlidMorphs"></a>
<h4 class="collection-method"><code>nullableUlidMorphs()</code></h4>

该方法与 [ulidMorphs](#column-method-ulidMorphs) 类似，但创建的列允许为 `null`：

```php
$table->nullableUlidMorphs('taggable');
```

<a name="column-method-nullableUuidMorphs"></a>
<h4 class="collection-method"><code>nullableUuidMorphs()</code></h4>

该方法与 [uuidMorphs](#column-method-uuidMorphs) 类似，但创建的列允许为 `null`：

```php
$table->nullableUuidMorphs('taggable');
```

<a name="column-method-rememberToken"></a>
<h4 class="collection-method"><code>rememberToken()</code></h4>

`rememberToken` 方法创建一个允许为 `null`、等效于 `VARCHAR(100)` 的列，用于存储「记住我」功能的[认证令牌](/docs/{{version}}/authentication#remembering-users)：

```php
$table->rememberToken();
```

<a name="column-method-set"></a>
<h4 class="collection-method"><code>set()</code></h4>

`set` 方法创建一个等效于 `SET` 的列，并指定允许的值列表：

```php
$table->set('flavors', ['strawberry', 'vanilla']);
```

<a name="column-method-smallIncrements"></a>
<h4 class="collection-method"><code>smallIncrements()</code></h4>

`smallIncrements` 方法创建一个等效于 `UNSIGNED SMALLINT` 的自增主键列：

```php
$table->smallIncrements('id');
```

<a name="column-method-smallInteger"></a>
<h4 class="collection-method"><code>smallInteger()</code></h4>

`smallInteger` 方法创建一个等效于 `SMALLINT` 的列：

```php
$table->smallInteger('votes');
```

<a name="column-method-softDeletesTz"></a>
<h4 class="collection-method"><code>softDeletesTz()</code></h4>

`softDeletesTz` 方法添加一个允许为 `null`、等效于 `TIMESTAMP`（带时区）的 `deleted_at` 列，可以指定小数秒精度。该列用于存储 Eloquent「软删除」功能所需的 `deleted_at` 时间戳：

```php
$table->softDeletesTz('deleted_at', precision: 0);
```

<a name="column-method-softDeletes"></a>
<h4 class="collection-method"><code>softDeletes()</code></h4>

`softDeletes` 方法添加一个允许为 `null`、等效于 `TIMESTAMP` 的 `deleted_at` 列，可以指定小数秒精度。该列用于存储 Eloquent「软删除」功能所需的 `deleted_at` 时间戳：

```php
$table->softDeletes('deleted_at', precision: 0);
```

<a name="column-method-string"></a>
<h4 class="collection-method"><code>string()</code></h4>

`string` 方法创建一个等效于 `VARCHAR`、长度为指定值的列：

```php
$table->string('name', length: 100);
```

<a name="column-method-text"></a>
<h4 class="collection-method"><code>text()</code></h4>

`text` 方法创建一个等效于 `TEXT` 的列：

```php
$table->text('description');
```

使用 MySQL 或 MariaDB 时，可以将列的字符集设为 `binary`，创建等效于 `BLOB` 的列：

```php
$table->text('data')->charset('binary'); // BLOB
```

<a name="column-method-timeTz"></a>
<h4 class="collection-method"><code>timeTz()</code></h4>

`timeTz` 方法创建一个等效于 `TIME`（带时区）的列，可以指定小数秒精度：

```php
$table->timeTz('sunrise', precision: 0);
```

<a name="column-method-time"></a>
<h4 class="collection-method"><code>time()</code></h4>

`time` 方法创建一个等效于 `TIME` 的列，可以指定小数秒精度：

```php
$table->time('sunrise', precision: 0);
```

<a name="column-method-timestampTz"></a>
<h4 class="collection-method"><code>timestampTz()</code></h4>

`timestampTz` 方法创建一个等效于 `TIMESTAMP`（带时区）的列，可以指定小数秒精度：

```php
$table->timestampTz('added_at', precision: 0);
```

<a name="column-method-timestamp"></a>
<h4 class="collection-method"><code>timestamp()</code></h4>

`timestamp` 方法创建一个等效于 `TIMESTAMP` 的列，可以指定小数秒精度：

```php
$table->timestamp('added_at', precision: 0);
```

<a name="column-method-timestampsTz"></a>
<h4 class="collection-method"><code>timestampsTz()</code></h4>

`timestampsTz` 方法创建 `created_at` 和 `updated_at` 两个等效于 `TIMESTAMP`（带时区）的列，可以指定小数秒精度：

```php
$table->timestampsTz(precision: 0);
```

<a name="column-method-timestamps"></a>
<h4 class="collection-method"><code>timestamps()</code></h4>

`timestamps` 方法创建 `created_at` 和 `updated_at` 两个等效于 `TIMESTAMP` 的列，可以指定小数秒精度：

```php
$table->timestamps(precision: 0);
```

<a name="column-method-tinyIncrements"></a>
<h4 class="collection-method"><code>tinyIncrements()</code></h4>

`tinyIncrements` 方法创建一个等效于 `UNSIGNED TINYINT` 的自增主键列：

```php
$table->tinyIncrements('id');
```

<a name="column-method-tinyInteger"></a>
<h4 class="collection-method"><code>tinyInteger()</code></h4>

`tinyInteger` 方法创建一个等效于 `TINYINT` 的列：

```php
$table->tinyInteger('votes');
```

<a name="column-method-tinyText"></a>
<h4 class="collection-method"><code>tinyText()</code></h4>

`tinyText` 方法创建一个等效于 `TINYTEXT` 的列：

```php
$table->tinyText('notes');
```

使用 MySQL 或 MariaDB 时，可以将列的字符集设为 `binary`，创建等效于 `TINYBLOB` 的列：

```php
$table->tinyText('data')->charset('binary'); // TINYBLOB
```

<a name="column-method-unsignedBigInteger"></a>
<h4 class="collection-method"><code>unsignedBigInteger()</code></h4>

`unsignedBigInteger` 方法创建一个等效于 `UNSIGNED BIGINT` 的列：

```php
$table->unsignedBigInteger('votes');
```

<a name="column-method-unsignedInteger"></a>
<h4 class="collection-method"><code>unsignedInteger()</code></h4>

`unsignedInteger` 方法创建一个等效于 `UNSIGNED INTEGER` 的列：

```php
$table->unsignedInteger('votes');
```

<a name="column-method-unsignedMediumInteger"></a>
<h4 class="collection-method"><code>unsignedMediumInteger()</code></h4>

`unsignedMediumInteger` 方法创建一个等效于 `UNSIGNED MEDIUMINT` 的列：

```php
$table->unsignedMediumInteger('votes');
```

<a name="column-method-unsignedSmallInteger"></a>
<h4 class="collection-method"><code>unsignedSmallInteger()</code></h4>

`unsignedSmallInteger` 方法创建一个等效于 `UNSIGNED SMALLINT` 的列：

```php
$table->unsignedSmallInteger('votes');
```

<a name="column-method-unsignedTinyInteger"></a>
<h4 class="collection-method"><code>unsignedTinyInteger()</code></h4>

`unsignedTinyInteger` 方法创建一个等效于 `UNSIGNED TINYINT` 的列：

```php
$table->unsignedTinyInteger('votes');
```

<a name="column-method-ulidMorphs"></a>
<h4 class="collection-method"><code>ulidMorphs()</code></h4>

`ulidMorphs` 是一个便捷方法，会添加一个等效于 `VARCHAR` 的 `{column}_type` 列，以及一个等效于 `CHAR(26)` 的 `{column}_id` 列。

该方法用于定义使用 ULID 标识符的多态 [Eloquent 关系](/docs/{{version}}/eloquent-relationships)所需的列。以下示例会创建 `taggable_type` 和 `taggable_id` 列：

```php
$table->ulidMorphs('taggable');
```

<a name="column-method-uuidMorphs"></a>
<h4 class="collection-method"><code>uuidMorphs()</code></h4>

`uuidMorphs` 是一个便捷方法，会添加一个等效于 `VARCHAR` 的 `{column}_type` 列，以及一个等效于 `CHAR(36)` 的 `{column}_id` 列。

该方法用于定义使用 UUID 标识符的[多态 Eloquent 关系](/docs/{{version}}/eloquent-relationships#polymorphic-relationships)所需的列。以下示例会创建 `taggable_type` 和 `taggable_id` 列：

```php
$table->uuidMorphs('taggable');
```

<a name="column-method-ulid"></a>
<h4 class="collection-method"><code>ulid()</code></h4>

`ulid` 方法创建一个等效于 `ULID` 的列：

```php
$table->ulid('id');
```

<a name="column-method-uuid"></a>
<h4 class="collection-method"><code>uuid()</code></h4>

`uuid` 方法创建一个等效于 `UUID` 的列：

```php
$table->uuid('id');
```

<a name="column-method-vector"></a>
<h4 class="collection-method"><code>vector()</code></h4>

`vector` 方法创建一个等效于 `vector` 的列：

```php
$table->vector('embedding', dimensions: 1536);
```

使用 `pgvector` 扩展的 PostgreSQL 连接以及 MariaDB 11.7 及更高版本支持向量列。使用 PostgreSQL 时，必须先加载 `pgvector`，才能创建 `vector` 列：

```php
Schema::ensureVectorExtensionExists();
```

要加快[向量相似度查询](/docs/{{version}}/queries#vector-similarity-clauses)，可以为列添加向量索引。在 `vector` 列上调用 `index` 方法，会创建使用余弦距离的向量索引：

```php
$table->vector('embedding', dimensions: 1536)->index();
```

<a name="column-method-year"></a>
<h4 class="collection-method"><code>year()</code></h4>

`year` 方法创建一个等效于 `YEAR` 的列：

```php
$table->year('birth_year');
```

<a name="column-modifiers"></a>
### 列修饰符

除了上述列类型，向数据库表添加列时，还可以使用各种列「修饰符」。例如，要允许列的值为 `null`，可以使用 `nullable` 方法：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->string('email')->nullable();
});
```

下表列出了所有可用的列修饰符，不包含[索引修饰符](#creating-indexes)：

<div class="overflow-auto" markdown="1">

| 修饰符                            | 说明                                                                                    |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- |
| `->after('column')`                 | 将列放在另一列之后（MariaDB / MySQL）。                                     |
| `->autoIncrement()`                 | 将 `INTEGER` 列设为自增主键。                                      |
| `->charset('utf8mb4')`              | 指定列的字符集（MariaDB / MySQL）。                                      |
| `->collation('utf8mb4_unicode_ci')` | 指定列的排序规则。                                                            |
| `->comment('my comment')`           | 为列添加注释（MariaDB / MySQL / PostgreSQL）。                                      |
| `->default($value)`                 | 指定列的默认值。                                                      |
| `->first()`                         | 将列放在表的首位（MariaDB / MySQL）。                                       |
| `->from($integer)`                  | 设置自增字段的起始值（MariaDB / MySQL / PostgreSQL）。           |
| `->instant()`                       | 使用即时操作添加或修改列（MySQL）。                                   |
| `->invisible()`                     | 使列对 `SELECT *` 查询不可见（MariaDB / MySQL）。                           |
| `->lock($mode)`                     | 指定列操作的锁模式（MySQL）。                                          |
| `->nullable($value = true)`         | 允许向列中插入 `NULL` 值。                                            |
| `->storedAs($expression)`           | 创建存储生成列（MariaDB / MySQL / PostgreSQL / SQLite）。                      |
| `->unsigned()`                      | 将 `INTEGER` 列设为 `UNSIGNED`（MariaDB / MySQL）。                                         |
| `->using($expression)`              | 更改列类型时指定类型转换表达式（PostgreSQL）。                       |
| `->useCurrent()`                    | 将 `TIMESTAMP` 列的默认值设为 `CURRENT_TIMESTAMP`。                           |
| `->useCurrentOnUpdate()`            | 更新记录时将 `TIMESTAMP` 列设为 `CURRENT_TIMESTAMP`（MariaDB / MySQL）。 |
| `->virtualAs($expression)`          | 创建虚拟生成列（MariaDB / MySQL / SQLite）。                                  |
| `->generatedAs($expression)`        | 使用指定的序列选项创建标识列（PostgreSQL）。                        |
| `->always()`                        | 为标识列设置序列值优先于输入值（PostgreSQL）。      |

</div>

<a name="default-expressions"></a>
#### 默认值表达式

`default` 修饰符接受一个值或 `Illuminate\Database\Query\Expression` 实例。使用 `Expression` 可以避免 Laravel 给值加上引号，从而使用数据库专用函数。这在为 JSON 列设置默认值时尤其有用：

```php
<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Query\Expression;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration
{
    /**
     * 运行迁移。
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

> [!WARNING]
> 默认值表达式的支持取决于数据库驱动、数据库版本和字段类型，请参阅相应数据库的文档。

<a name="column-order"></a>
#### 列顺序

使用 MariaDB 或 MySQL 时，可以通过 `after` 方法在现有列之后添加列：

```php
$table->after('password', function (Blueprint $table) {
    $table->string('address_line1');
    $table->string('address_line2');
    $table->string('city');
});
```

<a name="instant-column-operations"></a>
#### 即时列操作

使用 MySQL 时，可以在列定义后链式调用 `instant` 修饰符，指定使用 MySQL 的「instant」算法添加或修改列。该算法允许在不重建整张表的情况下执行某些结构变更，因此无论表多大，都能近乎即时完成：

```php
$table->string('name')->nullable()->instant();
```

即时添加列只能将列追加到表的末尾，因此 `instant` 不能与 `after` 或 `first` 修饰符一起使用。此外，该算法并不支持所有列类型或操作；如果操作不兼容，MySQL 会报错。

哪些操作支持即时列修改，请参阅 [MySQL 文档](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html)。

<a name="ddl-locking"></a>
#### DDL 锁

使用 MySQL 时，可以在列、索引或外键定义后链式调用 `lock` 修饰符，控制结构操作期间的表锁。MySQL 支持多种锁模式：`none` 允许并发读写，`shared` 允许并发读取但阻止写入，`exclusive` 阻止所有并发访问，`default` 则由 MySQL 选择最合适的模式：

```php
$table->string('name')->lock('none');

$table->index('email')->lock('shared');
```

如果指定的锁模式与操作不兼容，MySQL 会报错。你可以将 `lock` 与 `instant` 修饰符结合，进一步优化结构变更：

```php
$table->string('name')->instant()->lock('none');
```

<a name="modifying-columns"></a>
### 修改列

`change` 方法可以修改现有列的类型和属性。例如，要增加一个 `string` 列的长度，可以将 `name` 列的长度从 25 改为 50：只需定义列的新状态，再调用 `change` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->string('name', 50)->change();
});
```

修改列时，必须在列定义中明确包含所有需要保留的修饰符，否则对应属性会被移除。例如，要保留 `unsigned`、`default` 和 `comment` 属性，更改列时必须逐一调用这些修饰符：

```php
Schema::table('users', function (Blueprint $table) {
    $table->integer('votes')->unsigned()->default(1)->comment('my comment')->change();
});
```

`change` 方法不会更改列的索引。因此，可以在修改列时通过索引修饰符明确添加或删除索引：

```php
// 添加索引……
$table->bigIncrements('id')->primary()->change();

// 删除索引……
$table->char('postal_code', 10)->unique(false)->change();
```

<a name="postgresql-column-modifications"></a>
#### PostgreSQL 列修改

在 PostgreSQL 中修改列类型时，可以通过 `using` 修饰符指定转换现有值所用的表达式：

```php
Schema::table('users', function (Blueprint $table) {
    $table->date('birthday')->using('birthday::date')->change();
});
```

<a name="renaming-columns"></a>
### 重命名列

要重命名列，可以使用数据库结构构建器的 `renameColumn` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->renameColumn('from', 'to');
});
```

<a name="dropping-columns"></a>
### 删除列

要删除列，可以使用数据库结构构建器的 `dropColumn` 方法：

```php
Schema::table('users', function (Blueprint $table) {
    $table->dropColumn('votes');
});
```

向 `dropColumn` 方法传入列名数组，即可一次删除多列：

```php
Schema::table('users', function (Blueprint $table) {
    $table->dropColumn(['votes', 'avatar', 'location']);
});
```

<a name="available-command-aliases"></a>
#### 可用命令别名

Laravel 提供了多种便捷方法，用于删除常见类型的列，具体如下：

<div class="overflow-auto" markdown="1">

| 命令                             | 说明                                           |
| ----------------------------------- | ----------------------------------------------------- |
| `$table->dropMorphs('morphable');`  | 删除 `morphable_type` 和 `morphable_id` 列。 |
| `$table->dropRememberToken();`      | 删除 `remember_token` 列。                     |
| `$table->dropSoftDeletes();`        | 删除 `deleted_at` 列。                         |
| `$table->dropSoftDeletesTz();`      | `dropSoftDeletes()` 方法的别名。                  |
| `$table->dropTimestamps();`         | 删除 `created_at` 和 `updated_at` 列。       |
| `$table->dropTimestampsTz();`       | `dropTimestamps()` 方法的别名。                   |

</div>

<a name="indexes"></a>
## 索引

<a name="creating-indexes"></a>
### 创建索引

Laravel 的数据库结构构建器支持多种索引。以下示例创建一个 `email` 列，并要求其值唯一。在列定义后链式调用 `unique` 方法即可创建该索引：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('users', function (Blueprint $table) {
    $table->string('email')->unique();
});
```

你也可以先定义列，再创建索引。在数据库结构构建器的蓝图对象上调用 `unique` 方法，并传入需要唯一索引的列名即可：

```php
$table->unique('email');
```

向索引方法传入列名数组，还可以创建复合索引：

```php
$table->index(['account_id', 'created_at']);
```

创建索引时，Laravel 会根据表名、列名和索引类型自动生成索引名称。你也可以通过方法的第二个参数自行指定名称：

```php
$table->unique('email', 'unique_email');
```

<a name="available-index-types"></a>
#### 可用索引类型

Laravel 数据库结构构建器的蓝图类为各种受支持的索引提供了创建方法。每个索引方法都接受可选的第二个参数，用于指定索引名称。如果省略，就会根据表名、索引列名及索引类型生成名称。可用方法如下：

<div class="overflow-auto" markdown="1">

| 命令                                          | 说明                                                    |
| ------------------------------------------------ | -------------------------------------------------------------- |
| `$table->primary('id');`                         | 添加主键。                                            |
| `$table->primary(['id', 'parent_id']);`          | 添加复合主键。                                           |
| `$table->unique('email');`                       | 添加唯一索引。                                           |
| `$table->index('state');`                        | 添加普通索引。                                                 |
| `$table->fullText('body');`                      | 添加全文索引（MariaDB / MySQL / PostgreSQL）。         |
| `$table->fullText('body')->language('english');` | 添加指定语言的全文索引（PostgreSQL）。 |
| `$table->spatialIndex('location');`              | 添加空间索引（SQLite 除外）。                          |
| `$table->vectorIndex('embedding');`              | 添加向量索引（MariaDB / PostgreSQL）。                    |

</div>

<a name="online-index-creation"></a>
#### 在线创建索引

默认情况下，在大表上创建索引可能会锁表，在构建期间阻塞读写。使用 PostgreSQL 或 SQL Server 时，可以在索引定义后链式调用 `online` 方法，在不锁表的情况下创建索引，让应用在索引创建期间继续读写数据：

```php
$table->unique('email')->online();
```

使用 PostgreSQL 时，这会为创建索引的语句添加 `CONCURRENTLY` 选项；使用 SQL Server 时，则添加 `WITH (online = on)` 选项。

使用 MySQL 时，可以在索引或外键定义后链式调用 `inplace` 修饰符，指定操作使用 `INPLACE` 算法：

```php
$table->index('email')->inplace();

$table->foreign('user_id')->references('id')->on('users')->inplace();
```

`inplace` 可以与 `lock` 修饰符结合，控制操作期间的表锁：

```php
$table->index('email')->inplace()->lock('none');
```

对外键操作使用 `inplace` 修饰符时，必须禁用外键检查。

哪些操作支持 `INPLACE` 算法及相应锁模式，请参阅 [MySQL 文档](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html)。

<a name="renaming-indexes"></a>
### 重命名索引

要重命名索引，可以使用数据库结构构建器蓝图的 `renameIndex` 方法。第一个参数是当前索引名称，第二个参数是新名称：

```php
$table->renameIndex('from', 'to');
```

<a name="dropping-indexes"></a>
### 删除索引

删除索引时，必须指定索引名称。默认情况下，Laravel 会根据表名、索引列名和索引类型自动生成名称。示例如下：

<div class="overflow-auto" markdown="1">

| 命令                                                       | 说明                                                 |
| ------------------------------------------------------------- | ----------------------------------------------------------- |
| `$table->dropPrimary('users_id_primary');`                    | 删除「users」表的主键。                  |
| `$table->dropUnique('users_email_unique');`                   | 删除「users」表的唯一索引。                 |
| `$table->dropIndex('geo_state_index');`                       | 删除「geo」表的普通索引。                    |
| `$table->dropFullText('posts_body_fulltext');`                | 删除「posts」表的全文索引。              |
| `$table->dropSpatialIndex('geo_location_spatialindex');`      | 删除「geo」表的空间索引（SQLite 除外）。 |
| `$table->dropVectorIndex('documents_embedding_vectorindex');` | 删除「documents」表的向量索引。             |

</div>

如果向删除索引的方法传入列名数组，就会根据表名、列名和索引类型，按约定生成索引名称：

```php
Schema::table('geo', function (Blueprint $table) {
    $table->dropIndex(['state']); // 删除索引 'geo_state_index'
});
```

<a name="foreign-key-constraints"></a>
### 外键约束

Laravel 也支持创建外键约束，在数据库层面强制保证引用完整性。例如，以下代码定义 `posts` 表中的 `user_id` 列，使其引用 `users` 表的 `id` 列：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('posts', function (Blueprint $table) {
    $table->unsignedBigInteger('user_id');

    $table->foreign('user_id')->references('id')->on('users');
});
```

由于这种语法比较冗长，Laravel 还提供了基于约定的简洁方法，方便开发者使用。通过 `foreignId` 创建列时，上述示例可以改写为：

```php
Schema::table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained();
});
```

`foreignId` 方法创建一个等效于 `UNSIGNED BIGINT` 的列，`constrained` 则按约定确定被引用的表和列。如果表名不符合 Laravel 的约定，可以手动将其传给 `constrained`。你还可以指定生成的索引名称：

```php
Schema::table('posts', function (Blueprint $table) {
    $table->foreignId('user_id')->constrained(
        table: 'users', indexName: 'posts_user_id'
    );
});
```

你也可以指定约束在「on delete」和「on update」时执行的操作：

```php
$table->foreignId('user_id')
    ->constrained()
    ->onUpdate('cascade')
    ->onDelete('cascade');
```

这些操作也提供了更清晰的替代语法：

<div class="overflow-auto" markdown="1">

| 方法                        | 说明                                       |
| ----------------------------- | ------------------------------------------------- |
| `$table->cascadeOnUpdate();`  | 更新时级联更新。                           |
| `$table->restrictOnUpdate();` | 限制更新。                     |
| `$table->nullOnUpdate();`     | 更新时将外键值设为 null。 |
| `$table->noActionOnUpdate();` | 更新时不执行操作。                             |
| `$table->cascadeOnDelete();`  | 删除时级联删除。                           |
| `$table->restrictOnDelete();` | 限制删除。                     |
| `$table->nullOnDelete();`     | 删除时将外键值设为 null。 |
| `$table->noActionOnDelete();` | 存在子记录时阻止删除。          |

</div>

其他[列修饰符](#column-modifiers)必须在 `constrained` 方法之前调用：

```php
$table->foreignId('user_id')
    ->nullable()
    ->constrained();
```

<a name="dropping-foreign-keys"></a>
#### 删除外键

要删除外键，可以调用 `dropForeign` 方法，并传入要删除的外键约束名称。外键约束与索引使用相同的命名约定，即根据表名和约束涉及的列名，添加「\_foreign」后缀：

```php
$table->dropForeign('posts_user_id_foreign');
```

你也可以向 `dropForeign` 传入包含外键列名的数组。Laravel 会按约定将其转换为外键约束名称：

```php
$table->dropForeign(['user_id']);
```

<a name="toggling-foreign-key-constraints"></a>
#### 启用与禁用外键约束

你可以在迁移中通过以下方法启用或禁用外键约束：

```php
Schema::enableForeignKeyConstraints();

Schema::disableForeignKeyConstraints();

Schema::withoutForeignKeyConstraints(function () {
    // 此闭包内禁用外键约束……
});
```

> [!WARNING]
> SQLite 默认禁用外键约束。使用 SQLite 时，请先在数据库配置中[启用外键支持](/docs/{{version}}/database#configuration)，再通过迁移创建外键约束。

<a name="events"></a>
## 事件

为方便使用，每个迁移操作都会派发一个[事件](/docs/{{version}}/events)。除 `SchemaDumped` 和 `SchemaLoaded` 外，下列事件都实现了 `Illuminate\Contracts\Database\Events\MigrationEvent` 接口：

<div class="overflow-auto" markdown="1">

| 类                                            | 说明                                      |
| ------------------------------------------------ | ------------------------------------------------ |
| `Illuminate\Database\Events\DatabaseRefreshed`   | `migrate:fresh` 或 `migrate:refresh` 命令已执行完毕。 |
| `Illuminate\Database\Events\MigrationsStarted`   | 一批迁移即将执行。   |
| `Illuminate\Database\Events\MigrationsEnded`     | 一批迁移已执行完毕。              |
| `Illuminate\Database\Events\MigrationStarted`    | 单个迁移即将执行。      |
| `Illuminate\Database\Events\MigrationEnded`      | 单个迁移已执行完毕。                 |
| `Illuminate\Database\Events\NoPendingMigrations` | 迁移命令未发现待执行的迁移。 |
| `Illuminate\Database\Events\SchemaDumped`        | 数据库结构导出已完成。             |
| `Illuminate\Database\Events\SchemaLoaded`        | 已加载现有的数据库结构导出文件。     |

</div>

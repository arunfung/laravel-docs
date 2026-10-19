# Eloquent：快速入门

- [简介](#introduction)
- [生成模型类](#generating-model-classes)
- [Eloquent 模型约定](#eloquent-model-conventions)
    - [表名](#table-names)
    - [主键](#primary-keys)
    - [UUID 与 ULID 键](#uuid-and-ulid-keys)
    - [时间戳](#timestamps)
    - [数据库连接](#database-connections)
    - [默认属性值](#default-attribute-values)
    - [写入后刷新属性](#refreshing-attributes-after-writes)
    - [配置 Eloquent 严格模式](#configuring-eloquent-strictness)
- [检索模型](#retrieving-models)
    - [集合](#collections)
    - [分块处理结果](#chunking-results)
    - [使用惰性集合分块](#chunking-using-lazy-collections)
    - [游标](#cursors)
    - [高级子查询](#advanced-subqueries)
- [检索单个模型与聚合结果](#retrieving-single-models)
    - [检索或创建模型](#retrieving-or-creating-models)
    - [检索聚合结果](#retrieving-aggregates)
- [插入和更新模型](#inserting-and-updating-models)
    - [插入](#inserts)
    - [更新](#updates)
    - [批量赋值](#mass-assignment)
    - [更新或插入](#upserts)
- [删除模型](#deleting-models)
    - [软删除](#soft-deleting)
    - [查询软删除的模型](#querying-soft-deleted-models)
- [修剪模型](#pruning-models)
- [复制模型](#replicating-models)
- [查询作用域](#query-scopes)
    - [全局作用域](#global-scopes)
    - [局部作用域](#local-scopes)
    - [待处理属性](#pending-attributes)
- [比较模型](#comparing-models)
- [事件](#events)
    - [使用闭包](#events-using-closures)
    - [观察者](#observers)
    - [禁用事件](#muting-events)

<a name="introduction"></a>
## 简介

Laravel 内置 Eloquent 对象关系映射器（ORM），让数据库操作更加便捷。使用 Eloquent 时，每张数据库表都有一个对应的「模型」，用于操作该表。除了检索记录，Eloquent 模型也支持向表中插入、更新和删除记录。

> [!NOTE]
> 开始之前，请先在应用的 `config/database.php` 配置文件中设置数据库连接。更多信息请参阅[数据库配置文档](/docs/{{version}}/database#configuration)。

<a name="generating-model-classes"></a>
## 生成模型类

首先创建一个 Eloquent 模型。模型通常位于 `app\Models` 目录，并继承 `Illuminate\Database\Eloquent\Model` 类。你可以使用 `make:model` [Artisan 命令](/docs/{{version}}/artisan)生成模型：

```shell
php artisan make:model Flight
```

如果希望在生成模型时同时生成[数据库迁移](/docs/{{version}}/migrations)，可以使用 `--migration` 或 `-m` 选项：

```shell
php artisan make:model Flight --migration
```

生成模型时，还可以同时生成工厂、填充器、策略、控制器和表单请求等类。这些选项也可以组合使用，一次创建多个类：

```shell
# 生成模型和 FlightFactory 类……
php artisan make:model Flight --factory
php artisan make:model Flight -f

# 生成模型和 FlightSeeder 类……
php artisan make:model Flight --seed
php artisan make:model Flight -s

# 生成模型和 FlightController 类……
php artisan make:model Flight --controller
php artisan make:model Flight -c

# 生成模型、FlightController 资源控制器和表单请求类……
php artisan make:model Flight --controller --resource --requests
php artisan make:model Flight -crR

# 生成模型和 FlightPolicy 类……
php artisan make:model Flight --policy

# 生成模型以及迁移、工厂、填充器和控制器……
php artisan make:model Flight -mfsc

# 一次生成模型、迁移、工厂、填充器、策略、控制器和表单请求……
php artisan make:model Flight --all
php artisan make:model Flight -a

# 生成中间表模型……
php artisan make:model Member --pivot
php artisan make:model Member -p
```

<a name="inspecting-models"></a>
#### 查看模型信息

仅浏览模型代码，有时很难了解它的全部属性和关系。可以使用 `model:show` Artisan 命令，查看模型所有属性和关系的概览：

```shell
php artisan model:show Flight
```

<a name="eloquent-model-conventions"></a>
## Eloquent 模型约定

`make:model` 命令生成的模型会放在 `app/Models` 目录中。下面通过一个基本模型类，介绍 Eloquent 的主要约定：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    // ...
}
```

<a name="table-names"></a>
### 表名

上面的示例没有明确指定 `Flight` 模型对应的数据库表。按照约定，除非另行指定，Eloquent 会使用类名的复数形式，并转换为下划线命名法（snake case）作为表名。因此，`Flight` 模型对应 `flights` 表，而 `AirTrafficController` 模型对应 `air_traffic_controllers` 表。

如果模型对应的数据库表不符合此约定，可以通过 `Table` 特性手动指定表名：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table('my_flights')]
class Flight extends Model
{
    // ...
}
```


<a name="primary-keys"></a>
### 主键

Eloquent 还假定每个模型对应的数据库表都有一个名为 `id` 的主键列。你可以通过 `Table` 特性的 `key` 参数，指定其他列作为模型主键：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table(key: 'flight_id')]
class Flight extends Model
{
    // ...
}
```

此外，Eloquent 假定主键是自增整数，因此会自动将主键转换为整数。如果使用非自增或非数字主键，应在 `Table` 特性中指定 `keyType` 和 `incrementing` 参数：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table(key: 'uuid', keyType: 'string', incrementing: false)]
class Flight extends Model
{
    // ...
}
```

如果只需禁用自增 ID，可以使用 `WithoutIncrementing` 特性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\WithoutIncrementing;
use Illuminate\Database\Eloquent\Model;

#[WithoutIncrementing]
class Flight extends Model
{
    // ...
}
```

<a name="composite-primary-keys"></a>
#### 「复合」主键

Eloquent 要求每个模型至少具有一个可作为主键、能唯一标识记录的「ID」。Eloquent 模型不支持「复合」主键。不过，除了这个唯一标识主键，你仍可为数据库表添加额外的多列唯一索引。

<a name="uuid-and-ulid-keys"></a>
### UUID 与 ULID 键

你可以选择 UUID 作为 Eloquent 模型主键。UUID 是长度为 36 个字符、由字母和数字组成的全局唯一标识符。

要让模型使用 UUID 主键，可以在模型中使用 `Illuminate\Database\Eloquent\Concerns\HasUuids` trait，并确保模型对应的表具有一个 [UUID 类型的主键列](/docs/{{version}}/migrations#column-method-uuid)：

```php
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class Article extends Model
{
    use HasUuids;

    // ...
}

$article = Article::create(['title' => 'Traveling to Europe']);

$article->id; // "018f2b5c-6a7f-7b12-9d6f-2f8a4e0c9c11"
```

默认情况下，`HasUuids` trait 会为模型生成 [UUIDv7](/docs/{{version}}/strings#method-str-uuid7) 标识符。这些 UUID 可以按字典顺序排序，因此在建立索引的数据库中存储时效率更高。

你可以在模型中定义 `newUniqueId` 方法，自定义 UUID 的生成方式；也可以定义 `uniqueIds` 方法，指定哪些列应填入 UUID：

```php
use Ramsey\Uuid\Uuid;

/**
 * 为模型生成一个新的 UUID。
 */
public function newUniqueId(): string
{
    return (string) Uuid::uuid4();
}

/**
 * 获取应填入唯一标识符的列。
 *
 * @return array<int, string>
 */
public function uniqueIds(): array
{
    return ['id', 'discount_code'];
}
```

你也可以选择使用 ULID。ULID 与 UUID 类似，但长度只有 26 个字符。和有序 UUID 一样，ULID 可以按字典顺序排序，便于高效建立数据库索引。要使用 ULID，请在模型中使用 `Illuminate\Database\Eloquent\Concerns\HasUlids` trait，并确保模型对应的表具有一个 [ULID 类型的主键列](/docs/{{version}}/migrations#column-method-ulid)：

```php
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Model;

class Article extends Model
{
    use HasUlids;

    // ...
}

$article = Article::create(['title' => 'Traveling to Asia']);

$article->id; // "01gd4d3tgrrfqeda94gdbtdk5c"
```

<a name="timestamps"></a>
### 时间戳

默认情况下，Eloquent 期望模型对应的数据库表中存在 `created_at` 和 `updated_at` 列，并在创建或更新模型时自动设置它们的值。如果不希望 Eloquent 自动管理这些列，可以在模型的 `Table` 特性中将 `timestamps` 设为 `false`：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table(timestamps: false)]
class Flight extends Model
{
    // ...
}
```

如果只需禁用时间戳，可以使用 `WithoutTimestamps` 特性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\WithoutTimestamps;
use Illuminate\Database\Eloquent\Model;

#[WithoutTimestamps]
class Flight extends Model
{
    // ...
}
```

要自定义模型时间戳的格式，可以使用 `Table` 特性的 `dateFormat` 参数。它决定日期属性在数据库中的存储格式：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Model;

#[Table(dateFormat: 'U')]
class Flight extends Model
{
    // ...
}
```

如果只需定义日期格式，可以使用 `DateFormat` 特性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\DateFormat;
use Illuminate\Database\Eloquent\Model;

#[DateFormat('U')]
class Flight extends Model
{
    // ...
}
```

要自定义存储时间戳的列名，可以在模型中定义 `CREATED_AT` 和 `UPDATED_AT` 常量：

```php
<?php

class Flight extends Model
{
    /**
     * 存储创建时间的列名。
     *
     * @var string|null
     */
    public const CREATED_AT = 'creation_date';

    /**
     * 存储更新时间的列名。
     *
     * @var string|null
     */
    public const UPDATED_AT = 'updated_date';
}
```

要在执行模型操作时避免修改 `updated_at` 时间戳，可以将操作放在传给 `withoutTimestamps` 方法的闭包中：

```php
Model::withoutTimestamps(fn () => $post->increment('reads'));
```

<a name="database-connections"></a>
### 数据库连接

默认情况下，所有 Eloquent 模型都使用应用配置的默认数据库连接。要为某个模型指定其他连接，可以使用 `Connection` 特性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Connection;
use Illuminate\Database\Eloquent\Model;

#[Connection('mysql')]
class Flight extends Model
{
    // ...
}
```

<a name="default-attribute-values"></a>
### 默认属性值

默认情况下，新创建的模型实例不包含任何属性值。要为某些属性定义默认值，可以在模型中定义 `$attributes` 属性。该数组中的值应使用原始的「可存储」格式，如同刚从数据库中读取一样：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 模型属性的默认值。
     *
     * @var array<string, mixed>
     */
    protected $attributes = [
        'options' => '[]',
        'delayed' => false,
    ];
}
```

<a name="refreshing-attributes-after-writes"></a>
### 写入后刷新属性

如果数据库中包含生成列，可以配置 Eloquent，在插入或更新模型后刷新指定属性。为此，请在模型上定义 `Refreshes` 特性：

```php
use Illuminate\Database\Eloquent\Attributes\Refreshes;

#[Refreshes('name')]
class User extends Model
{
    // ...
}
```

你可以通过数组指定多个属性：

```php
#[Refreshes(['name', 'slug'])]
```

模型写入数据库后，指定属性会从数据库重新加载。

<a name="configuring-eloquent-strictness"></a>
### 配置 Eloquent 严格模式

Laravel 提供了多种方法，用于配置 Eloquent 在不同场景下的行为和「严格程度」。

`preventLazyLoading` 方法接受一个可选的布尔参数，用来决定是否禁止延迟加载。例如，你可能只希望在非生产环境中禁用延迟加载，以免生产代码中意外使用了延迟加载关系时影响应用运行。通常应在应用 `AppServiceProvider` 的 `boot` 方法中调用该方法：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Model::preventLazyLoading(! $this->app->isProduction());
}
```

你还可以调用 `preventSilentlyDiscardingAttributes` 方法，让 Laravel 在尝试填充不可批量赋值的属性时抛出异常。这有助于在本地开发时发现未加入模型 `fillable` 数组的属性，避免赋值未生效却没有报错：

```php
Model::preventSilentlyDiscardingAttributes(! $this->app->isProduction());
```

<a name="retrieving-models"></a>
## 检索模型

创建模型及其[对应的数据库表](/docs/{{version}}/migrations#generating-migrations)后，就可以开始检索数据。每个 Eloquent 模型都可以视为一个强大的[查询构造器](/docs/{{version}}/queries)，用于查询模型对应的表。模型的 `all` 方法会检索该表中的所有记录：

```php
use App\Models\Flight;

foreach (Flight::all() as $flight) {
    echo $flight->name;
}
```

<a name="building-queries"></a>
#### 构建查询

Eloquent 的 `all` 方法会返回模型对应表中的所有结果。由于每个模型本身也是[查询构造器](/docs/{{version}}/queries)，你可以先添加查询约束，再调用 `get` 方法获取结果：

```php
$flights = Flight::where('active', 1)
    ->orderBy('name')
    ->limit(10)
    ->get();
```

> [!NOTE]
> Eloquent 模型也是查询构造器，因此建议了解 Laravel [查询构造器](/docs/{{version}}/queries)提供的所有方法。编写 Eloquent 查询时，这些方法都可以使用。

<a name="refreshing-models"></a>
#### 刷新模型

对于已从数据库检索的模型实例，可以使用 `fresh` 和 `refresh` 方法「刷新」数据。`fresh` 会重新查询数据库并返回一个新模型，现有实例不受影响：

```php
$flight = Flight::where('number', 'FR 900')->first();

$freshFlight = $flight->fresh();
```

`refresh` 方法则会用数据库中的最新数据重新填充现有模型，同时刷新该模型已经加载的所有关系：

```php
$flight = Flight::where('number', 'FR 900')->first();

$flight->number = 'FR 456';

$flight->refresh();

$flight->number; // "FR 900"
```

如果需要在事务中刷新模型并获取悲观锁，可以使用 `refreshForUpdate` 方法。它会使用 `FOR UPDATE` 锁重新加载模型：

```php
DB::transaction(function () use ($flight) {
    $flight->refreshForUpdate();

    // 更新已加锁的模型……
});
```

<a name="collections"></a>
### 集合

如前所述，`all`、`get` 等 Eloquent 方法会从数据库中检索多条记录，但返回值并非普通 PHP 数组，而是 `Illuminate\Database\Eloquent\Collection` 实例。

Eloquent 的 `Collection` 类继承 Laravel 的基础集合类 `Illuminate\Support\Collection`，提供了[多种实用方法](/docs/{{version}}/collections#available-methods)来处理集合数据。例如，可以使用 `reject` 方法，根据闭包的返回结果从集合中排除模型：

```php
$flights = Flight::where('destination', 'Paris')->get();

$flights = $flights->reject(function (Flight $flight) {
    return $flight->cancelled;
});
```

除了基础集合类的方法，Eloquent 集合类还提供了[一些额外方法](/docs/{{version}}/eloquent-collections#available-methods)，专门用于处理 Eloquent 模型集合。

Laravel 的所有集合都实现了 PHP 的可迭代接口，因此可以像数组一样遍历：

```php
foreach ($flights as $flight) {
    echo $flight->name;
}
```

<a name="chunking-results"></a>
### 分块处理结果

如果使用 `all` 或 `get` 一次加载数万条 Eloquent 记录，应用可能耗尽内存。此时可以使用 `chunk` 方法，更高效地处理大量模型。

`chunk` 方法每次检索一部分 Eloquent 模型，并将它们传给闭包处理。由于每次只加载当前分块的模型，处理大量模型时可以显著减少内存占用：

```php
use App\Models\Flight;
use Illuminate\Database\Eloquent\Collection;

Flight::chunk(200, function (Collection $flights) {
    foreach ($flights as $flight) {
        // ...
    }
});
```

`chunk` 的第一个参数指定每个「分块」的记录数，第二个参数是处理各分块的闭包。每获取一个分块，都会执行一次数据库查询，再将结果传给闭包。

如果查询筛选条件涉及某一列，而你在遍历结果时也会更新该列，应使用 `chunkById`。这种情况下使用 `chunk` 可能导致意外或不一致的结果。`chunkById` 在内部始终查询 `id` 大于上一分块最后一个模型的记录：

```php
Flight::where('departed', true)
    ->chunkById(200, function (Collection $flights) {
        $flights->each->update(['departed' => false]);
    }, column: 'id');
```

`chunkById` 和 `lazyById` 会自行向查询添加 `where` 条件，因此通常应将你自己的条件放在闭包中进行[逻辑分组](/docs/{{version}}/queries#logical-grouping)：

```php
Flight::where(function ($query) {
    $query->where('delayed', true)->orWhere('cancelled', true);
})->chunkById(200, function (Collection $flights) {
    $flights->each->update([
        'departed' => false,
        'cancelled' => true
    ]);
}, column: 'id');
```

<a name="chunking-using-lazy-collections"></a>
### 使用惰性集合分块

`lazy` 与 [`chunk` 方法](#chunking-results)类似，内部也会分块执行查询。但它不会将各分块直接传给回调，而是返回一个已展平的 Eloquent 模型[惰性集合（LazyCollection）](/docs/{{version}}/collections#lazy-collections)，让你将结果作为连续的数据流处理：

```php
use App\Models\Flight;

foreach (Flight::lazy() as $flight) {
    // ...
}
```

如果 `lazy` 的查询筛选条件涉及某一列，而你在遍历结果时也会更新该列，应使用 `lazyById`。它在内部始终检索 `id` 大于上一分块最后一个模型的记录：

```php
Flight::where('departed', true)
    ->lazyById(200, column: 'id')
    ->each->update(['departed' => false]);
```

你也可以使用 `lazyByIdDesc`，按 `id` 降序检索结果。

<a name="cursors"></a>
### 游标

与 `lazy` 类似，`cursor` 方法可以在遍历数万条 Eloquent 模型记录时显著降低内存消耗。

`cursor` 只执行一次数据库查询，但只有遍历到某条记录时才会将其填充为 Eloquent 模型。因此，遍历游标时，内存中始终只保留一个模型。

> [!WARNING]
> `cursor` 每次只在内存中保留一个 Eloquent 模型，因此不能预加载关系。如果需要预加载关系，请考虑使用 [`lazy` 方法](#chunking-using-lazy-collections)。

`cursor` 在内部通过 PHP [生成器](https://www.php.net/manual/en/language.generators.overview.php)实现此功能：

```php
use App\Models\Flight;

foreach (Flight::where('destination', 'Zurich')->cursor() as $flight) {
    // ...
}
```

`cursor` 返回一个 `Illuminate\Support\LazyCollection` 实例。[惰性集合](/docs/{{version}}/collections#lazy-collections)支持普通 Laravel 集合的许多方法，同时每次只将一个模型加载到内存中：

```php
use App\Models\User;

$users = User::cursor()->filter(function (User $user) {
    return $user->id > 500;
});

foreach ($users as $user) {
    echo $user->id;
}
```

虽然 `cursor` 每次只保留一个模型，比普通查询节省许多内存，但数据量足够大时仍会耗尽内存。这是[因为 PHP 的 PDO 驱动会在内部缓冲区缓存所有原始查询结果](https://www.php.net/manual/en/mysqlinfo.concepts.buffering.php)。如果需要处理海量 Eloquent 记录，请考虑使用 [`lazy` 方法](#chunking-using-lazy-collections)。

<a name="advanced-subqueries"></a>
### 高级子查询

<a name="subquery-selects"></a>
#### 子查询选择

Eloquent 支持高级子查询，可在一次查询中获取关联表的信息。例如，假设有一张航班目的地表 `destinations` 和一张飞往各目的地的航班表 `flights`。`flights` 表中的 `arrived_at` 列记录航班到达目的地的时间。

通过查询构造器 `select` 和 `addSelect` 方法的子查询功能，可以用一次查询获取所有目的地，以及最近到达各目的地的航班名称：

```php
use App\Models\Destination;
use App\Models\Flight;

return Destination::addSelect(['last_flight' => Flight::select('name')
    ->whereColumn('destination_id', 'destinations.id')
    ->orderByDesc('arrived_at')
    ->limit(1)
])->get();
```

<a name="subquery-ordering"></a>
#### 子查询排序

查询构造器的 `orderBy` 也支持子查询。继续使用航班示例，可以根据最近一班航班到达的时间对所有目的地排序，同样只需执行一次数据库查询：

```php
return Destination::orderByDesc(
    Flight::select('arrived_at')
        ->whereColumn('destination_id', 'destinations.id')
        ->orderByDesc('arrived_at')
        ->limit(1)
)->get();
```

<a name="retrieving-single-models"></a>
## 检索单个模型与聚合结果

除了检索查询匹配的所有记录，也可以使用 `find`、`first` 或 `firstWhere` 获取单条记录。这些方法返回单个模型实例：

```php
use App\Models\Flight;

// 根据主键检索模型……
$flight = Flight::find(1);

// 检索符合查询条件的第一个模型……
$flight = Flight::where('active', 1)->first();

// 检索符合查询条件的第一个模型的另一种写法……
$flight = Flight::firstWhere('active', 1);
```

有时需要在未找到记录时执行其他操作。`findOr` 和 `firstOr` 会在找到记录时返回模型实例，否则执行给定闭包，并将闭包的返回值作为方法结果：

```php
$flight = Flight::findOr(1, function () {
    // ...
});

$flight = Flight::where('legs', '>', 3)->firstOr(function () {
    // ...
});
```

<a name="not-found-exceptions"></a>
#### 未找到模型时抛出异常

你也可以在未找到模型时抛出异常，这在路由或控制器中特别有用。`findOrFail` 和 `firstOrFail` 会检索查询的第一个结果；如果没有找到，则抛出 `Illuminate\Database\Eloquent\ModelNotFoundException`：

```php
$flight = Flight::findOrFail(1);

$flight = Flight::where('legs', '>', 3)->firstOrFail();
```

如果没有捕获 `ModelNotFoundException`，Laravel 会自动向客户端返回 HTTP 404 响应：

```php
use App\Models\Flight;

Route::get('/api/flights/{id}', function (string $id) {
    return Flight::findOrFail($id);
});
```

<a name="retrieving-or-creating-models"></a>
### 检索或创建模型

`firstOrCreate` 会根据给定的列和值查找数据库记录。如果找不到，就合并第一个数组参数与可选的第二个数组参数，并使用合并后的属性插入记录。

`firstOrNew` 与 `firstOrCreate` 类似，也会根据给定属性查找记录。但找不到时，它只返回一个新模型实例，不会写入数据库。你需要手动调用 `save` 保存该实例：

```php
use App\Models\Flight;

// 根据名称检索航班，不存在时创建……
$flight = Flight::firstOrCreate([
    'name' => 'London to Paris'
]);

// 根据名称检索航班，不存在时使用 name、delayed 和 arrival_time 属性创建……
$flight = Flight::firstOrCreate(
    ['name' => 'London to Paris'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);

// 根据名称检索航班，不存在时实例化一个新的 Flight……
$flight = Flight::firstOrNew([
    'name' => 'London to Paris'
]);

// 根据名称检索航班，不存在时使用 name、delayed 和 arrival_time 属性实例化……
$flight = Flight::firstOrNew(
    ['name' => 'Tokyo to Sydney'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);
```

<a name="retrieving-aggregates"></a>
### 检索聚合结果

使用 Eloquent 模型时，也可以调用 Laravel [查询构造器](/docs/{{version}}/queries)提供的 `count`、`sum`、`max` 等[聚合方法](/docs/{{version}}/queries#aggregates)。这些方法返回标量值，而非模型实例：

```php
$count = Flight::where('active', 1)->count();

$max = Flight::where('active', 1)->max('price');
```

<a name="inserting-and-updating-models"></a>
## 插入和更新模型

<a name="inserts"></a>
### 插入

Eloquent 也支持向数据库插入记录。只需创建一个模型实例、设置其属性，再调用实例的 `save` 方法：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Flight;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class FlightController extends Controller
{
    /**
     * 将新航班存入数据库。
     */
    public function store(Request $request): RedirectResponse
    {
        // 验证请求……

        $flight = new Flight;

        $flight->name = $request->name;

        $flight->save();

        return redirect('/flights');
    }
}
```

本例将 HTTP 请求的 `name` 字段赋给 `App\Models\Flight` 模型实例的 `name` 属性。调用 `save` 后，会向数据库插入记录，同时自动设置 `created_at` 和 `updated_at` 时间戳，无需手动赋值。

要在数据库事务中保存模型，可以使用 `saveOrFail`。如果保存过程中抛出异常，事务会自动回滚：

```php
$flight->saveOrFail();
```

也可以使用 `create`，通过一条 PHP 语句保存新模型。该方法会返回已插入的模型实例：

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```

不过，使用 `create` 前，需要在模型类上指定 `Fillable` 或 `Guarded` 特性，因为所有 Eloquent 模型默认都启用了批量赋值保护。详情请参阅[批量赋值文档](#mass-assignment)。

<a name="updates"></a>
### 更新

`save` 也可以更新数据库中的现有模型。先检索模型并修改所需属性，再调用 `save`。`updated_at` 时间戳同样会自动更新，无需手动设置：

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->name = 'Paris to London';

$flight->save();
```

要在数据库事务中更新模型，可以使用 `updateOrFail`。如果更新过程中抛出异常，事务会自动回滚：

```php
$flight->updateOrFail(['name' => 'Paris to London']);
```

有时需要更新现有模型，并在没有匹配模型时创建新模型。可以使用 `updateOrCreate`。它与 `firstOrCreate` 一样会直接保存模型，无需手动调用 `save`。

以下示例会查找 `departure` 为 `Oakland`、`destination` 为 `San Diego` 的航班。如果存在，就更新其 `price` 和 `discounted` 列；否则，合并两个参数数组中的属性，创建一个新航班：

```php
$flight = Flight::updateOrCreate(
    ['departure' => 'Oakland', 'destination' => 'San Diego'],
    ['price' => 99, 'discounted' => 1]
);
```

使用 `firstOrCreate` 或 `updateOrCreate` 等方法时，你可能需要区分模型是新创建的，还是已存在的。`wasRecentlyCreated` 属性表示模型是否在当前生命周期中创建：

```php
$flight = Flight::updateOrCreate(
    // ...
);

if ($flight->wasRecentlyCreated) {
    // 已插入新的航班记录……
}
```

<a name="mass-updates"></a>
#### 批量更新

你也可以更新查询所匹配的所有模型。以下示例将所有处于活动状态、且目的地为 `San Diego` 的航班标记为延误：

```php
Flight::where('active', 1)
    ->where('destination', 'San Diego')
    ->update(['delayed' => 1]);
```

`update` 接受一个由列名和值组成的数组，指定需要更新的列，并返回受影响的行数。

> [!WARNING]
> 通过 Eloquent 批量更新时，不会为受影响的模型触发 `saving`、`saved`、`updating` 和 `updated` 事件，因为批量更新并未实际检索这些模型。

<a name="examining-attribute-changes"></a>
#### 检查属性变化

Eloquent 提供 `isDirty`、`isClean` 和 `wasChanged` 方法，用于检查模型内部状态，了解属性自检索以来的变化。

`isDirty` 用于判断模型自检索以来是否有属性发生变化。你可以传入属性名或属性名数组，检查其中是否有属性「已修改」。`isClean` 则判断属性是否保持不变，也接受可选的属性参数：

```php
use App\Models\User;

$user = User::create([
    'first_name' => 'Taylor',
    'last_name' => 'Otwell',
    'title' => 'Developer',
]);

$user->title = 'Painter';

$user->isDirty(); // true
$user->isDirty('title'); // true
$user->isDirty('first_name'); // false
$user->isDirty(['first_name', 'title']); // true

$user->isClean(); // false
$user->isClean('title'); // false
$user->isClean('first_name'); // true
$user->isClean(['first_name', 'title']); // false

$user->save();

$user->isDirty(); // false
$user->isClean(); // true
```

`wasChanged` 用于判断当前请求周期内，模型最近一次保存时是否有属性发生变化。你也可以传入属性名，检查指定属性：

```php
$user = User::create([
    'first_name' => 'Taylor',
    'last_name' => 'Otwell',
    'title' => 'Developer',
]);

$user->title = 'Painter';

$user->save();

$user->wasChanged(); // true
$user->wasChanged('title'); // true
$user->wasChanged(['title', 'slug']); // true
$user->wasChanged('first_name'); // false
$user->wasChanged(['first_name', 'title']); // true
```

`getOriginal` 返回模型的原始属性数组，不受检索后的修改影响。你也可以传入属性名，获取指定属性的原始值：

```php
$user = User::find(1);

$user->name; // John
$user->email; // john@example.com

$user->name = 'Jack';
$user->name; // Jack

$user->getOriginal('name'); // John
$user->getOriginal(); // 原始属性数组……
```

`getChanges` 返回模型最近一次保存时发生变化的属性数组，`getPrevious` 则返回最近一次保存前的原始属性值数组：

```php
$user = User::find(1);

$user->name; // John
$user->email; // john@example.com

$user->update([
    'name' => 'Jack',
    'email' => 'jack@example.com',
]);

$user->getChanges();

/*
    [
        'name' => 'Jack',
        'email' => 'jack@example.com',
    ]
*/

$user->getPrevious();

/*
    [
        'name' => 'John',
        'email' => 'john@example.com',
    ]
*/
```

<a name="mass-assignment"></a>
### 批量赋值

你可以使用 `create`，通过一条 PHP 语句保存新模型。该方法返回已插入的模型实例：

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```

不过，使用 `create` 前，需要在模型类上指定 `Fillable` 或 `Guarded` 特性，因为所有 Eloquent 模型默认都启用了批量赋值保护。

如果用户在 HTTP 请求中传入了非预期字段，而该字段修改了本不应允许用户修改的数据库列，就会发生批量赋值漏洞。例如，恶意用户可能在请求中发送 `is_admin` 参数。如果该参数直接传给模型的 `create` 方法，就可能让用户将自己提升为管理员。

因此，首先应通过模型的 `Fillable` 特性，明确哪些属性允许批量赋值。例如，将 `Flight` 模型的 `name` 属性设为可批量赋值：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Model;

#[Fillable(['name'])]
class Flight extends Model
{
    // ...
}
```

指定可批量赋值的属性后，就可以使用 `create` 向数据库插入记录，并获取新创建的模型实例：

```php
$flight = Flight::create(['name' => 'London to Paris']);
```

如果已有模型实例，可以使用 `fill` 将属性数组填充到该实例中：

```php
$flight->fill(['name' => 'Amsterdam to Frankfurt']);
```

<a name="mass-assignment-json-columns"></a>
#### 批量赋值与 JSON 列

对 JSON 列批量赋值时，必须在模型的 `Fillable` 特性中明确列出允许赋值的键。出于安全考虑，使用 `Guarded` 特性时，Laravel 不支持更新嵌套 JSON 属性：

```php
use Illuminate\Database\Eloquent\Attributes\Fillable;

#[Fillable(['options->enabled'])]
class Flight extends Model
{
    // ...
}
```

<a name="allowing-mass-assignment"></a>
#### 允许所有属性批量赋值

要允许所有属性批量赋值，可以在模型上使用 `Unguarded` 特性。解除保护后，应格外谨慎，始终手动构建传给 Eloquent 的 `fill`、`create` 和 `update` 方法的数组：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Unguarded;
use Illuminate\Database\Eloquent\Model;

#[Unguarded]
class Flight extends Model
{
    // ...
}
```

<a name="mass-assignment-exceptions"></a>
#### 批量赋值异常

默认情况下，批量赋值时未包含在 `Fillable` 特性中的属性会被静默丢弃。这在生产环境中是预期行为，但本地开发时，可能让你难以察觉模型修改未生效的原因。

你可以调用 `preventSilentlyDiscardingAttributes`，让 Laravel 在尝试填充不可批量赋值的属性时抛出异常。通常应在应用 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Model::preventSilentlyDiscardingAttributes($this->app->isLocal());
}
```

<a name="upserts"></a>
### 更新或插入

Eloquent 的 `upsert` 方法可以在一次原子操作中更新或创建记录。第一个参数包含要插入或更新的值；第二个参数列出表中用于唯一标识记录的列；第三个参数指定已存在匹配记录时需要更新的列。如果模型启用了时间戳，`upsert` 会自动设置 `created_at` 和 `updated_at`：

```php
Flight::upsert([
    ['departure' => 'Oakland', 'destination' => 'San Diego', 'price' => 99],
    ['departure' => 'Chicago', 'destination' => 'New York', 'price' => 150]
], uniqueBy: ['departure', 'destination'], update: ['price']);
```

> [!WARNING]
> 除 SQL Server 外，所有数据库都要求 `upsert` 第二个参数指定的列具有主键或唯一索引。此外，MariaDB 和 MySQL 驱动会忽略第二个参数，始终使用表中已有的主键和唯一索引来判断记录是否存在。

<a name="deleting-models"></a>
## 删除模型

要删除模型，可以在模型实例上调用 `delete`：

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->delete();
```

要在数据库事务中删除模型，可以使用 `deleteOrFail`。如果删除过程中抛出异常，事务会自动回滚：

```php
$flight->deleteOrFail();
```

<a name="deleting-an-existing-model-by-its-primary-key"></a>
#### 根据主键删除现有模型

上面的示例先检索模型，再调用 `delete`。如果已知主键，可以直接调用 `destroy`，无需显式检索模型。该方法接受单个或多个主键，也接受主键数组或主键[集合](/docs/{{version}}/collections)：

```php
Flight::destroy(1);

Flight::destroy(1, 2, 3);

Flight::destroy([1, 2, 3]);

Flight::destroy(collect([1, 2, 3]));
```

对于使用[软删除](#soft-deleting)的模型，可以通过 `forceDestroy` 永久删除：

```php
Flight::forceDestroy(1);
```

> [!WARNING]
> `destroy` 会逐个加载模型并调用 `delete`，以便为每个模型正确派发 `deleting` 和 `deleted` 事件。

<a name="deleting-models-using-queries"></a>
#### 通过查询删除模型

你也可以构建 Eloquent 查询，删除所有匹配的模型。以下示例删除所有标记为非活动的航班。与批量更新一样，批量删除不会为被删除的模型派发模型事件：

```php
$deleted = Flight::where('active', 0)->delete();
```

要删除表中的所有模型，请执行不带任何条件的删除查询：

```php
$deleted = Flight::query()->delete();
```

> [!WARNING]
> 通过 Eloquent 批量删除时，不会为被删除的模型派发 `deleting` 和 `deleted` 事件，因为执行删除语句时并未实际检索这些模型。

<a name="soft-deleting"></a>
### 软删除

Eloquent 还支持对模型进行「软删除」。软删除不会真正移除数据库记录，而是设置模型的 `deleted_at` 属性，记录「删除」的日期和时间。要启用软删除，请在模型中添加 `Illuminate\Database\Eloquent\SoftDeletes` trait：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Flight extends Model
{
    use SoftDeletes;
}
```

> [!NOTE]
> `SoftDeletes` trait 会自动将 `deleted_at` 属性转换为 `DateTime` / `Carbon` 实例。

你还需要在数据库表中添加 `deleted_at` 列。Laravel [数据库结构构建器](/docs/{{version}}/migrations)提供了创建该列的辅助方法：

```php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

Schema::table('flights', function (Blueprint $table) {
    $table->softDeletes();
});

Schema::table('flights', function (Blueprint $table) {
    $table->dropSoftDeletes();
});
```

此后，调用模型的 `delete` 方法时，会将 `deleted_at` 设为当前日期和时间，但数据库记录仍保留在表中。查询启用了软删除的模型时，已软删除的模型会自动排除在所有查询结果之外。

要判断模型实例是否已被软删除，可以使用 `trashed`：

```php
if ($flight->trashed()) {
    // ...
}
```

<a name="restoring-soft-deleted-models"></a>
#### 恢复软删除的模型

要恢复软删除的模型，可以在模型实例上调用 `restore`。该方法会将模型的 `deleted_at` 列设为 `null`：

```php
$flight->restore();
```

也可以在查询中调用 `restore`，一次恢复多个模型。与其他批量操作一样，这不会为恢复的模型派发模型事件：

```php
Flight::withTrashed()
    ->where('airline_id', 1)
    ->restore();
```

构建[关系查询](/docs/{{version}}/eloquent-relationships)时，也可以使用 `restore`：

```php
$flight->history()->restore();
```

<a name="permanently-deleting-models"></a>
#### 永久删除模型

要从数据库中真正移除软删除的模型，可以使用 `forceDelete`：

```php
$flight->forceDelete();
```

构建 Eloquent 关系查询时，也可以使用 `forceDelete`：

```php
$flight->history()->forceDelete();
```

<a name="querying-soft-deleted-models"></a>
### 查询软删除的模型

<a name="including-soft-deleted-models"></a>
#### 包含软删除的模型

如前所述，查询结果默认排除软删除的模型。你可以在查询上调用 `withTrashed`，将它们也包含在结果中：

```php
use App\Models\Flight;

$flights = Flight::withTrashed()
    ->where('account_id', 1)
    ->get();
```

构建[关系查询](/docs/{{version}}/eloquent-relationships)时，也可以调用 `withTrashed`：

```php
$flight->history()->withTrashed()->get();
```

<a name="retrieving-only-soft-deleted-models"></a>
#### 仅检索软删除的模型

`onlyTrashed` 方法**只会**检索软删除的模型：

```php
$flights = Flight::onlyTrashed()
    ->where('airline_id', 1)
    ->get();
```

<a name="pruning-models"></a>
## 修剪模型

如果需要定期删除不再使用的模型，可以在模型中添加 `Illuminate\Database\Eloquent\Prunable` 或 `Illuminate\Database\Eloquent\MassPrunable` trait，再实现 `prunable` 方法，返回一个用于查询待删除模型的 Eloquent 查询构造器：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Prunable;

class Flight extends Model
{
    use Prunable;

    /**
     * 获取待修剪模型的查询。
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', now()->minus(months: 1));
    }
}
```

使用 `Prunable` 时，还可以在模型中定义 `pruning` 方法。它会在模型删除前调用，适合在永久删除数据库记录之前，清理模型关联的其他资源，例如已存储的文件：

```php
/**
 * 为修剪模型做准备。
 */
protected function pruning(): void
{
    // ...
}
```

配置好可修剪模型后，请在应用的 `routes/console.php` 中调度 `model:prune` Artisan 命令，并按需要选择运行频率：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('model:prune')->daily();
```

`model:prune` 会自动查找应用 `app/Models` 目录中的可修剪模型。如果模型位于其他目录，可以通过 `--model` 选项指定模型类名：

```php
Schedule::command('model:prune', [
    '--model' => [Address::class, Flight::class],
])->daily();
```

要排除某些模型，同时修剪检测到的其他模型，可以使用 `--except` 选项：

```php
Schedule::command('model:prune', [
    '--except' => [Address::class, Flight::class],
])->daily();
```

可以给 `model:prune` 加上 `--pretend` 选项来检查 `prunable` 查询。此时命令只报告实际运行时会修剪的记录数：

```shell
php artisan model:prune --pretend
```

> [!WARNING]
> 软删除的模型如果匹配修剪查询，将被永久删除（`forceDelete`）。

<a name="mass-pruning"></a>
#### 批量修剪

使用 `Illuminate\Database\Eloquent\MassPrunable` trait 时，会通过批量删除查询移除模型。因此不会调用 `pruning` 方法，也不会派发 `deleting` 和 `deleted` 事件，因为删除前不会实际检索这些模型。这种方式能显著提高修剪效率：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\MassPrunable;

class Flight extends Model
{
    use MassPrunable;

    /**
     * 获取待修剪模型的查询。
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', now()->minus(months: 1));
    }
}
```

<a name="replicating-models"></a>
## 复制模型

`replicate` 可以为现有模型创建一个尚未保存的副本，适用于多个模型具有许多相同属性的场景：

```php
use App\Models\Address;

$shipping = Address::create([
    'type' => 'shipping',
    'line_1' => '123 Example Street',
    'city' => 'Victorville',
    'state' => 'CA',
    'postcode' => '90001',
]);

$billing = $shipping->replicate()->fill([
    'type' => 'billing'
]);

$billing->save();
```

要在复制时排除某些属性，可以将属性名数组传给 `replicate`：

```php
$flight = Flight::create([
    'destination' => 'LAX',
    'origin' => 'LHR',
    'last_flown' => '2020-03-04 11:00:00',
    'last_pilot_id' => 747,
]);

$flight = $flight->replicate([
    'last_flown',
    'last_pilot_id'
]);
```

<a name="query-scopes"></a>
## 查询作用域

<a name="global-scopes"></a>
### 全局作用域

全局作用域允许你为某个模型的所有查询添加约束。Laravel 的[软删除](#soft-deleting)功能就利用全局作用域，只检索「未删除」的模型。你也可以编写自己的全局作用域，确保模型的每次查询都应用指定约束。

<a name="generating-scopes"></a>
#### 生成作用域

要生成全局作用域，可以调用 `make:scope` Artisan 命令。生成的类会放在应用的 `app/Models/Scopes` 目录中：

```shell
php artisan make:scope AncientScope
```

<a name="writing-global-scopes"></a>
#### 编写全局作用域

先使用 `make:scope` 生成一个实现 `Illuminate\Database\Eloquent\Scope` 接口的类。该接口要求实现 `apply` 方法，你可以在其中向查询添加 `where` 条件或其他子句：

```php
<?php

namespace App\Models\Scopes;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;

class AncientScope implements Scope
{
    /**
     * 将作用域应用于给定的 Eloquent 查询构造器。
     */
    public function apply(Builder $builder, Model $model): void
    {
        $builder->where('created_at', '<', now()->minus(years: 2000));
    }
}
```

> [!NOTE]
> 如果全局作用域需要向查询的 select 子句添加列，应使用 `addSelect`，以免意外覆盖已有的 select 子句。

<a name="applying-global-scopes"></a>
#### 应用全局作用域

要将全局作用域应用于模型，只需在模型上添加 `ScopedBy` 特性：

```php
<?php

namespace App\Models;

use App\Models\Scopes\AncientScope;
use Illuminate\Database\Eloquent\Attributes\ScopedBy;

#[ScopedBy([AncientScope::class])]
class User extends Model
{
    //
}
```

你也可以重写模型的 `booted` 方法，调用 `addGlobalScope` 手动注册全局作用域。该方法只接受一个作用域实例参数：

```php
<?php

namespace App\Models;

use App\Models\Scopes\AncientScope;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 booted 方法。
     */
    protected static function booted(): void
    {
        static::addGlobalScope(new AncientScope);
    }
}
```

为 `App\Models\User` 添加上述作用域后，调用 `User::all()` 会执行以下 SQL 查询：

```sql
select * from `users` where `created_at` < 0021-02-18 00:00:00
```

<a name="anonymous-global-scopes"></a>
#### 匿名全局作用域

Eloquent 也支持通过闭包定义全局作用域，适用于无需单独建类的简单作用域。使用闭包时，请将作用域名称作为 `addGlobalScope` 的第一个参数：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 booted 方法。
     */
    protected static function booted(): void
    {
        static::addGlobalScope('ancient', function (Builder $builder) {
            $builder->where('created_at', '<', now()->minus(years: 2000));
        });
    }
}
```

<a name="removing-global-scopes"></a>
#### 移除全局作用域

要在某次查询中移除全局作用域，可以调用 `withoutGlobalScope`，并传入全局作用域的类名：

```php
User::withoutGlobalScope(AncientScope::class)->get();
```

如果作用域是通过闭包定义的，则传入为该作用域指定的名称：

```php
User::withoutGlobalScope('ancient')->get();
```

要移除多个或全部全局作用域，可以使用 `withoutGlobalScopes` 和 `withoutGlobalScopesExcept`：

```php
// 移除所有全局作用域……
User::withoutGlobalScopes()->get();

// 移除部分全局作用域……
User::withoutGlobalScopes([
    FirstScope::class, SecondScope::class
])->get();

// 移除指定作用域以外的所有全局作用域……
User::withoutGlobalScopesExcept([
    SecondScope::class,
])->get();
```

<a name="local-scopes"></a>
### 局部作用域

局部作用域可以将常用的查询约束定义在一起，方便在应用中复用。例如，你可能经常需要检索所有「热门」用户。要定义作用域，请在 Eloquent 方法上添加 `Scope` 特性。

作用域方法应始终返回同一个查询构造器实例或 `void`：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 将查询限定为仅包含热门用户。
     */
    #[Scope]
    protected function popular(Builder $query): void
    {
        $query->where('votes', '>', 100);
    }

    /**
     * 将查询限定为仅包含活跃用户。
     */
    #[Scope]
    protected function active(Builder $query): void
    {
        $query->where('active', 1);
    }
}
```

<a name="utilizing-a-local-scope"></a>
#### 使用局部作用域

定义作用域后，就可以在查询模型时调用作用域方法，也可以链式调用多个作用域：

```php
use App\Models\User;

$users = User::popular()->active()->orderBy('created_at')->get();
```

通过 `or` 运算符组合多个作用域时，可能需要使用闭包，确保正确的[逻辑分组](/docs/{{version}}/queries#logical-grouping)：

```php
$users = User::popular()->orWhere(function (Builder $query) {
    $query->active();
})->get();
```

为简化这种写法，Laravel 提供了「高阶」`orWhere` 方法，无需闭包即可链式组合这些作用域：

```php
$users = User::popular()->orWhere->active()->get();
```

<a name="dynamic-scopes"></a>
#### 动态作用域

作用域也可以接受参数。只需在方法签名中添加参数，并将它们放在 `$query` 参数之后：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 将查询限定为仅包含指定类型的用户。
     */
    #[Scope]
    protected function ofType(Builder $query, string $type): void
    {
        $query->where('type', $type);
    }
}
```

在方法签名中添加参数后，就可以在调用作用域时传值：

```php
$users = User::ofType('admin')->get();
```

使用特性声明的作用域方法应为 `protected`。在模型类内部调用这类作用域时，应通过查询构造器实例调用，例如 `static::query()->ofType('admin')`，确保由 Eloquent 的作用域机制处理调用。

<a name="pending-attributes"></a>
### 待处理属性

如果希望通过作用域创建模型，并让模型具有该作用域用于筛选的属性值，可以在构建作用域查询时使用 `withAttributes`：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    /**
     * 将查询限定为仅包含草稿。
     */
    #[Scope]
    protected function draft(Builder $query): void
    {
        $query->withAttributes([
            'hidden' => true,
        ]);
    }
}
```

`withAttributes` 会根据给定属性添加 `where` 条件，并将这些属性应用到通过该作用域创建的模型：

```php
$draft = Post::draft()->create(['title' => 'In Progress']);

$draft->hidden; // true
```

如果不希望 `withAttributes` 添加 `where` 条件，可以将 `asConditions` 参数设为 `false`：

```php
$query->withAttributes([
    'hidden' => true,
], asConditions: false);
```

<a name="comparing-models"></a>
## 比较模型

可以使用 `is` 和 `isNot`，快速判断两个模型是否具有相同的主键、表和数据库连接：

```php
if ($post->is($anotherPost)) {
    // ...
}

if ($post->isNot($anotherPost)) {
    // ...
}
```

`belongsTo`、`hasOne`、`morphTo` 和 `morphOne` [关系](/docs/{{version}}/eloquent-relationships)也提供了 `is` 和 `isNot`，可直接比较关联模型，无需先执行查询检索模型：

```php
if ($post->author()->is($user)) {
    // ...
}
```

<a name="events"></a>
## 事件

> [!NOTE]
> 要将 Eloquent 事件直接广播到客户端应用，请参阅 Laravel 的[模型事件广播](/docs/{{version}}/broadcasting#model-broadcasting)。

Eloquent 模型会派发多种事件，方便你在模型生命周期的各个阶段执行操作，包括：`retrieved`、`creating`、`created`、`updating`、`updated`、`saving`、`saved`、`deleting`、`deleted`、`trashed`、`forceDeleting`、`forceDeleted`、`restoring`、`restored` 和 `replicating`。

从数据库检索现有模型时，会派发 `retrieved`。首次保存新模型时，会派发 `creating` 和 `created`。修改现有模型并调用 `save` 时，会派发 `updating` / `updated`。创建或更新模型时，即使属性没有变化，也会派发 `saving` / `saved`。以 `-ing` 结尾的事件在模型变更写入数据库之前派发，以 `-ed` 结尾的事件则在写入之后派发。

要监听模型事件，可以在 Eloquent 模型中定义 `$dispatchesEvents` 属性，将生命周期中的各个事件映射到你自己的[事件类](/docs/{{version}}/events)。每个事件类都应通过构造函数接收受影响的模型实例：

```php
<?php

namespace App\Models;

use App\Events\UserDeleted;
use App\Events\UserSaved;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 模型的事件映射。
     *
     * @var array<string, string>
     */
    protected $dispatchesEvents = [
        'saved' => UserSaved::class,
        'deleted' => UserDeleted::class,
    ];
}
```

定义事件映射后，就可以使用[事件监听器](/docs/{{version}}/events#defining-listeners)处理这些事件。

> [!WARNING]
> 通过 Eloquent 批量更新或删除时，不会为受影响的模型派发 `saved`、`updated`、`deleting` 和 `deleted` 事件，因为这些操作没有实际检索模型。

<a name="events-using-closures"></a>
### 使用闭包

除了自定义事件类，你也可以注册闭包，在模型事件派发时执行。通常应在模型的 `booted` 方法中注册：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 booted 方法。
     */
    protected static function booted(): void
    {
        static::created(function (User $user) {
            // ...
        });
    }
}
```

注册模型事件时，也可以使用[可入队的匿名事件监听器](/docs/{{version}}/events#queueable-anonymous-event-listeners)，让 Laravel 通过应用的[队列](/docs/{{version}}/queues)在后台执行监听器：

```php
use function Illuminate\Events\queueable;

static::created(queueable(function (User $user) {
    // ...
}));
```

<a name="observers"></a>
### 观察者

<a name="defining-observers"></a>
#### 定义观察者

如果需要监听同一模型的多个事件，可以使用观察者，将监听逻辑集中到一个类中。观察者的方法名对应要监听的 Eloquent 事件，每个方法只接受受影响的模型实例作为参数。可以使用 `make:observer` Artisan 命令生成观察者类：

```shell
php artisan make:observer UserObserver --model=User
```

生成的观察者会放在 `app/Observers` 目录中。如果目录不存在，Artisan 会自动创建。新观察者的内容如下：

```php
<?php

namespace App\Observers;

use App\Models\User;

class UserObserver
{
    /**
     * 处理 User 的 created 事件。
     */
    public function created(User $user): void
    {
        // ...
    }

    /**
     * 处理 User 的 updated 事件。
     */
    public function updated(User $user): void
    {
        // ...
    }

    /**
     * 处理 User 的 deleted 事件。
     */
    public function deleted(User $user): void
    {
        // ...
    }

    /**
     * 处理 User 的 restored 事件。
     */
    public function restored(User $user): void
    {
        // ...
    }

    /**
     * 处理 User 的 forceDeleted 事件。
     */
    public function forceDeleted(User $user): void
    {
        // ...
    }
}
```

要注册观察者，可以在对应模型上添加 `ObservedBy` 特性：

```php
use App\Observers\UserObserver;
use Illuminate\Database\Eloquent\Attributes\ObservedBy;

#[ObservedBy([UserObserver::class])]
class User extends Authenticatable
{
    //
}
```

也可以在需要观察的模型上调用 `observe` 手动注册。通常将注册代码放在应用 `AppServiceProvider` 的 `boot` 方法中：

```php
use App\Models\User;
use App\Observers\UserObserver;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    User::observe(UserObserver::class);
}
```

> [!NOTE]
> 观察者还可以监听 `saving`、`retrieved` 等其他事件，详情请参阅[事件](#events)部分。

<a name="observers-and-database-transactions"></a>
#### 观察者与数据库事务

在数据库事务中创建模型时，你可能希望观察者等事务提交后再处理事件。为此，可以让观察者实现 `ShouldHandleEventsAfterCommit` 接口。如果当前没有进行中的数据库事务，事件处理方法会立即执行：

```php
<?php

namespace App\Observers;

use App\Models\User;
use Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit;

class UserObserver implements ShouldHandleEventsAfterCommit
{
    /**
     * 处理 User 的 created 事件。
     */
    public function created(User $user): void
    {
        // ...
    }
}
```

<a name="muting-events"></a>
### 禁用事件

要临时禁用模型的所有事件，可以使用 `withoutEvents`。该方法只接受一个闭包参数，闭包内执行的代码不会派发模型事件，其返回值也会由 `withoutEvents` 返回：

```php
use App\Models\User;

$user = User::withoutEvents(function () {
    User::findOrFail(1)->delete();

    return User::find(2);
});
```

<a name="saving-a-single-model-without-events"></a>
#### 保存单个模型时不派发事件

要在保存模型时不派发事件，可以使用 `saveQuietly`：

```php
$user = User::findOrFail(1);

$user->name = 'Victoria Faith';

$user->saveQuietly();
```

你也可以在不派发事件的情况下更新、删除、软删除、恢复和复制模型：

```php
$user->deleteQuietly();
$user->forceDeleteQuietly();
$user->restoreQuietly();
```

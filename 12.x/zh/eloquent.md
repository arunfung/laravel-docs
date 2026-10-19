
# Eloquent: 快速入门

- [简介](#简介)
- [生成模型类](#生成模型类)
- [ Eloquent 模型约定](#Eloquent模型约定)
    - [表名](#表名)
    - [主键](#主键)
    - [UUID 与 ULID 键](#UUID与ULID键)
    - [时间戳](#时间戳)
    - [数据库连接](#数据库连接)
    - [默认属性值](#默认属性值)
    - [严格配置 Eloquent](#严格配置Eloquent)
- [模型检索](#模型检索)
    - [集合](#集合)
    - [分块结果集](#分块结果集)
    - [使用懒加载集合分块](#使用懒加载集合分块)
    - [游标](#游标)
    - [高级子查询](#高级子查询)
- [检索单个模型 / 聚合](#检索单个模型/聚合)
    - [检索或创建模型](#检索或创建模型)
    - [检索聚合](#检索聚合)
- [新增 & 更新模型](#新增&更新模型)
    - [新增](#新增)
    - [更新](#更新)
    - [批量任务](#批量任务)
    - [有则更新无则新增](#有则更新无则新增)
- [删除模型](#删除模型)
    - [软删除](#软删除)
    - [查询已被软删除模型](#查询已被软删除模型)
- [修剪模型](#修剪模型)
- [复制模型](#复制模型)
- [查询作用域](#查询作用域)
    - [全局作用域](#全局作用域)
    - [局部作用域](#局部作用域)
    - [待处理属性](#待处理属性)
- [模型对比](#模型对比)
- [事件](#事件)
    - [使用闭包方法](#使用闭包方法)
    - [观察者](#观察者)
    - [静默事件](#静默事件)

<a name="简介"></a>
## 简介

Laravel 包含的 Eloquent 模块，是一个对象关系映射 (ORM)，能使你更愉快地交互数据库。当你使用 Eloquent 时，数据库中每张表都有一个相对应的” 模型” 用于操作这张表。除了能从数据表中检索数据记录之外，Eloquent 模型同时也允许你新增，更新和删除这对应表中的数据。

> [!注意]
> 在开始之前，请务必在应用程序的 `config/database.php` 配置文件中配置数据库连接。有关配置数据库的更多信息，请参阅[数据库配置文档](/docs/laravel/12.x/​​database#configuration)。



<a name="generating-model-classes"></a>
## 生成模型类

首先，让我们创建一个 Eloquent 模型。模型通常位于 `app\Models` 目录中，并扩展 `Illuminate\Database\Eloquent\Model` 类。您可以使用 `make:model` [Artisan 命令](/docs/laravel/12.x/artisan) 生成新模型：

```shell
php artisan make:model Flight
```

如果您希望在生成模型时生成一个[数据库迁移](/docs/laravel/12.x/migrations)，可以使用 `--migration` 或 `-m` 选项：

```shell
php artisan make:model Flight --migration
```

在生成模型时，你可以生成各种其他类型的类，如工厂、填充器、策略、控制器和表单请求。此外，这些选项可以组合在一起一次创建多个类：

```shell
# 生成模型和 FlightFactory 类...
php artisan make:model Flight --factory
php artisan make:model Flight -f

# 生成模型和 FlightSeeder 类...
php artisan make:model Flight --seed
php artisan make:model Flight -s

# 生成模型和 FlightController 类...
php artisan make:model Flight --controller
php artisan make:model Flight -c

# 生成模型、FlightController 资源类和表单请求类...
php artisan make:model Flight --controller --resource --requests
php artisan make:model Flight -crR

# 生成模型和 FlightPolicy 类...
php artisan make:model Flight --policy

# 生成模型和迁移、工厂、填充器和控制器...
php artisan make:model Flight -mfsc

# 快捷方式生成一个模型、迁移、工厂、填充器、策略、控制器和表单请求...
php artisan make:model Flight --all
php artisan make:model Flight -a

# 生成一个 pivot 模型...
php artisan make:model Member --pivot
php artisan make:model Member -p
```



<a name="inspecting-models"></a>
#### 模型检查

有时候，仅仅通过浏览其代码很难确定模型的所有可用属性和关系。相反，尝试使用 `model:show` Artisan 命令，它能方便地概览模型的所有属性和关系：

```shell
php artisan model:show Flight
```

<a name="eloquent-model-conventions"></a>
## Eloquent 模型约定

`make:model` 命令生成的模型将放置在 `app/Models` 目录中。让我们检查一个基本模型类并讨论一些 Eloquent 的关键约定：

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

看完上面的示例后，你可能已经注意到，我们没有告诉 Eloquent `Flight` 模型对应的是哪个数据库表。按照惯例，类的「snake case」、复数名称将被用作表名，除非明确指定了另一个名称。因此，在本例中，Eloquent 将假设 `Flight` 模型存储记录在 `flights` 表中，而 `AirTrafficController` 模型则会存储记录在 `air_traffic_controllers` 表中。

如果你的模型对应的数据库表不符合此约定，你可以通过在模型上定义一个 `table` 属性来手动指定模型的表名：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 与模型关联的表
     *
     * @var string
     */
    protected $table = 'my_flights';
}
```

<a name="primary-keys"></a>
### 主键

Eloquent 还会假设每个模型的对应数据库表都有一个名为 `id` 的主键列。如果必要，你可以在你的模型上定义一个受保护的 `$primaryKey` 属性，以指定一个不同的列作为模型的主键：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 与表关联的主键
     *
     * @var string
     */
    protected $primaryKey = 'flight_id';
}
```



此外，Eloquent 认为主键是一个递增的整数值，这意味着 Eloquent 将自动将主键转换为整数。如果你希望使用非递增或非数字主键，你必须在模型上定义一个公共的 `$incrementing` 属性，并将之设置为 `false`：

```php
<?php

class Flight extends Model
{
    /**
     * 表明模型的 ID 是否自增
     *
     * @var bool
     */
    public $incrementing = false;
}
```

如果模型的主键不是整数，你应该在模型上定义一个受保护的 `$keyType` 属性。此属性应该具有 `string` 的值：

```php
<?php

class Flight extends Model
{
    /**
     * 主键 ID 的数据类型
     *
     * @var string
     */
    protected $keyType = 'string';
}
```

<a name="composite-primary-keys"></a>
#### 「复合」主键

Eloquent 要求每个模型至少有一个唯一标识的「ID」，可以作为其主键。Eloquent 模型不支持「复合」主键。不过，你可以在数据库表中添加额外的多列唯一索引，作为表的唯一识别主键。

<a name="uuid-and-ulid-keys"></a>
### UUID 与 ULID 键

你可能选择使用 UUID 而不是自增整数作为 Eloquent 模型的主键。UUID 是全球唯一的字母数字标识符，长度为 36 个字符。

如果你希望模型使用 UUID 键而不是自增整数键，你可以在模型上使用 `Illuminate\Database\Eloquent\Concerns\HasUuids`。当然，你应该确保模型有一个[相当于UUID 的主键列](/docs/laravel/12.x/migrations#column-method-uuid)：

```php
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class Article extends Model
{
    use HasUuids;

    // ...
}

$article = Article::create(['title' => 'Traveling to Europe']);

$article->id; // "8f8e8478-9035-4d23-b9a7-62f4d2612ce5"
```



默认情况下，`HasUuids` 特性将为您的模型生成 [「有序」UUID](/docs/laravel/12.x/strings#method-str-ordered-uuid)。这些 UUID 对于索引数据库存储更有效，因为它们可以按字典顺序排序。

您可以通过在模型上定义 `newUniqueId` 方法来覆盖给定模型的 UUID 生成过程。此外，您可以通过在模型上定义 `uniqueIds` 方法来指定哪些列应该接收 UUID：

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
 * 获取应接收唯一标识符的列。
 *
 * @return array<int, string>
 */
public function uniqueIds(): array
{
    return ['id', 'discount_code'];
}
```

如果您愿意，您可以选择使用「ULID」而不是 UUID。ULID 与 UUID 类似；但是，它们只有 26 个字符长。像有序 UUID 一样，ULID 可以按字典顺序排序，以便高效地进行数据库索引。要使用 ULID，您应该在模型上使用 `Illuminate\Database\Eloquent\Concerns\HasUlids` 特性。您还应确保模型具有 [ULID 等效的主键列](/docs/laravel/12.x/migrations#column-method-ulid)：

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

默认情况下，Eloquent 期望在模型对应的数据库表中存在 `created_at` 和 `updated_at` 列。当模型被创建或更新时，Eloquent 将自动设置这些列的值。如果您不希望 Eloquent 自动管理这些列，您应该在模型上定义一个值为 `false` 的 `$timestamps` 属性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 指示模型是否应该被时间戳标记。
     *
     * @var bool
     */
    public $timestamps = false;
}
```



如需自定义模型时间戳的格式，请在模型中设置 `$dateFormat` 属性。该属性决定了日期属性在数据库中的存储方式，以及模型序列化为数组或 JSON 时的显示格式：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 模型日期列的存储格式
     *
     * @var string
     */
    protected $dateFormat = 'U';
}
```

如需自定义存储时间戳的列名，可在模型中定义 `CREATED_AT` 和 `UPDATED_AT` 常量：

```php
<?php

class Flight extends Model
{
    const CREATED_AT = 'creation_date';
    const UPDATED_AT = 'updated_date';
}
```

若想在执行模型操作时避免更新 `updated_at` 时间戳，可将操作放在 `withoutTimestamps` 方法提供的闭包中执行：

```php
Model::withoutTimestamps(fn () => $post->increment('reads'));
```

<a name="database-connections"></a>
### 数据库连接

默认情况下，所有 Eloquent 模型都会使用应用程序配置的默认数据库连接。如需为特定模型指定不同的连接，请在模型中定义 `$connection` 属性：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 模型应使用的数据库连接
     *
     * @var string
     */
    protected $connection = 'mysql';
}
```

<a name="default-attribute-values"></a>
### 默认属性值

默认情况下，新实例化的模型不包含任何属性值。如需为模型的某些属性定义默认值，可在模型中定义 `$attributes` 属性。`$attributes` 数组中的属性值应采用原始的「可存储」格式，如同刚从数据库中读取一样：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 模型的默认属性值
     *
     * @var array
     */
    protected $attributes = [
        'options' => '[]',
        'delayed' => false,
    ];
}
```



<a name="configuring-eloquent-strictness"></a>
### 配置 Eloquent 严格模式

Laravel 提供了多种方法来配置 Eloquent 在不同场景下的行为和「严格模式」。

首先，`preventLazyLoading` 方法接受一个可选的布尔参数，用于指示是否应阻止延迟加载。例如，你可能希望仅在非生产环境中禁用延迟加载，这样即使在生产代码中意外存在延迟加载关系，生产环境仍能正常运行。通常，此方法应在应用程序的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 引导所有应用程序服务
 */
public function boot(): void
{
    Model::preventLazyLoading(! $this->app->isProduction());
}
```

此外，你还可以通过调用 `preventSilentlyDiscardingAttributes` 方法，指示 Laravel 在尝试填充不可填充属性时抛出异常。这有助于在本地开发期间防止因尝试设置未添加到模型 `fillable` 数组的属性而导致的意外错误：

```php
Model::preventSilentlyDiscardingAttributes(! $this->app->isProduction());
```

<a name="retrieving-models"></a>
## 获取模型

创建模型及其[关联的数据库表](/docs/laravel/12.x/migrations#generating-migrations)后，你就可以开始从数据库获取数据了。你可以将每个 Eloquent 模型视为一个强大的[查询构建器](/docs/laravel/12.x/queries)，能够流畅地查询与模型关联的数据库表。模型的 `all` 方法将获取与模型关联的数据库表中的所有记录：

```php
use App\Models\Flight;

foreach (Flight::all() as $flight) {
    echo $flight->name;
}
```

<a name="building-queries"></a>


#### 构建查询

Eloquent 的 `all` 方法会返回模型表中的所有结果。然而，由于每个 Eloquent 模型都充当 [查询构建器](/docs/laravel/12.x/queries)， 因此你可以在查询中添加额外的约束条件，然后调用 get 方法来获取结果：

```php
$flights = Flight::where('active', 1)
    ->orderBy('name')
    ->take(10)
    ->get();
```

> 注意
> 由于 Eloquent 模型本质上就是查询构建器，因此你应该去查看 Laravel [查询构建器](/docs/laravel/12.x/queries) 提供的所有方法。当你在编写 Eloquent 查询时，你可以使用这些方法中的任何一个。

<a name="refreshing-models"></a>
#### 刷新模型

如果你已经有一个从数据库中检索出来的 Eloquent 模型实例，你可以使用 `fresh` 和 `refresh`方法来「刷新」该模型。`fresh` 方法会从数据库中重新检索该模型。现有的模型实例不会受到影响：

```php
$flight = Flight::where('number', 'FR 900')->first();

$freshFlight = $flight->fresh();
```

 `refresh`  方法将使用数据库中的新数据重新填充现有模型，并且还将刷新其所有加载的关系：

```php
$flight = Flight::where('number', 'FR 900')->first();

$flight->number = 'FR 456';

$flight->refresh();

$flight->number; // "FR 900"
```

<a name="collections"></a>
### 集合

正如我们所见, 像 `all` 和 `get`  这样的 Eloquent 方法从数据库中检索的是多条记录。但是，这些方法不会返回普通的 PHP 数组。相反，返回的是 `Illuminate\Database\Eloquent\Collection` 类的实例。

Eloquent 的 `Collection` 来扩展了 Laravel 的基础 `Illuminate\Support\Collection` 类，为与数据集合交互提供了 [多种有用的方法](/docs/laravel/12.x/collections#available-methods) 。 例如, `reject` 方法可用于根据调用闭包的结果从集合中删除模型：

```php
$flights = Flight::where('destination', 'Paris')->get();

$flights = $flights->reject(function (Flight $flight) {
    return $flight->cancelled;
});
```



除了 Laravel 基础集合类提供的方法外，Eloquent 集合类还提供了[一些额外的方法](/docs/laravel/12.x/eloquent-collections#available-methods)，专门用于与 Eloquent 模型集合进行交互。

由于 Laravel 的所有集合都实现了 PHP 的可迭代接口，你可以像遍历数组一样遍历集合：

```php
foreach ($flights as $flight) {
    echo $flight->name;
}
```

<a name="chunking-results"></a>
### 分块处理结果

如果你尝试通过 `all` 或 `get` 方法加载数万条 Eloquent 记录，应用程序可能会耗尽内存。此时可以使用 `chunk` 方法来更高效地处理大量模型。

`chunk` 方法会获取一部分 Eloquent 模型，并将其传递给闭包进行处理。由于每次只获取当前块的 Eloquent 模型，因此在处理大量模型时，`chunk` 方法能够显著减少内存使用：

```php
use App\Models\Flight;
use Illuminate\Database\Eloquent\Collection;

Flight::chunk(200, function (Collection $flights) {
    foreach ($flights as $flight) {
        // ...
    }
});
```

传递给 `chunk` 方法的第一个参数是你希望每个「块」包含的记录数。作为第二个参数传递的闭包将对从数据库获取的每个块执行。每次都会执行数据库查询来获取传递给闭包的记录块。

如果你基于某个列对 `chunk` 方法的结果进行过滤，同时在遍历结果时还会更新该列，那么应该使用 `chunkById` 方法。在这些场景中使用 `chunk` 方法可能会导致意外和不一致的结果。`chunkById` 方法在内部始终会获取 `id` 列值大于前一块中最后一个模型的模型：

```php
Flight::where('departed', true)
    ->chunkById(200, function (Collection $flights) {
        $flights->each->update(['departed' => false]);
    }, column: 'id');
```



由于 `chunkById` 和 `lazyById` 方法会向正在执行的查询添加自己的 "where" 条件，你通常应该将你自己的条件[逻辑分组](/docs/laravel/12.x/queries#logical-grouping)在闭包内：

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
### 使用惰性集合进行分块

`lazy` 方法在幕后以块为单位执行查询，这与 [`chunk` 方法](#chunking-results)类似。然而，`lazy` 方法不会直接将每个块传递给回调函数，而是返回一个扁平的 Eloquent 模型[惰性集合](/docs/laravel/12.x/collections#lazy-collections)，让你可以将结果作为单个流进行交互：

```php
use App\Models\Flight;

foreach (Flight::lazy() as $flight) {
    // ...
}
```

如果你基于某个列对 `lazy` 方法的结果进行过滤，同时在遍历结果时还会更新该列，那么应该使用 `lazyById` 方法。在内部，`lazyById` 方法始终会获取 `id` 列值大于前一块中最后一个模型的模型：

```php
Flight::where('departed', true)
    ->lazyById(200, column: 'id')
    ->each->update(['departed' => false]);
```

你可以使用 `lazyByIdDesc` 方法基于 `id` 的降序来过滤结果。

<a name="cursors"></a>
### 游标

与 `lazy` 方法类似，`cursor` 方法可用于在遍历数万条 Eloquent 模型记录时显著减少应用程序的内存消耗。



`cursor` 方法只会执行一次数据库查询；然而，各个 Eloquent 模型只有在实际遍历时才会被实例化。因此，在遍历游标时，任何给定时间都只有一个 Eloquent 模型保留在内存中。

> [注意]
> 由于 `cursor` 方法一次只在内存中保留一个 Eloquent 模型，因此它无法预加载关联关系。如果你需要预加载关联关系，请考虑改用 [`lazy` 方法](#chunking-using-lazy-collections)。

在内部，`cursor` 方法使用 PHP 的[生成器](https://www.php.net/manual/en/language.generators.overview.php)来实现此功能：

```php
use App\Models\Flight;

foreach (Flight::where('destination', 'Zurich')->cursor() as $flight) {
    // ...
}
```

`cursor` 返回一个 `Illuminate\Support\LazyCollection` 实例。[惰性集合](/docs/laravel/12.x/collections#lazy-collections)允许你使用典型 Laravel 集合上的许多集合方法，同时一次只将一个模型加载到内存中：

```php
use App\Models\User;

$users = User::cursor()->filter(function (User $user) {
    return $user->id > 500;
});

foreach ($users as $user) {
    echo $user->id;
}
```

尽管 `cursor` 方法通过一次只在内存中保留一个 Eloquent 模型而比普通查询使用更少的内存，但它最终仍可能耗尽内存。这是由于 [PHP 的 PDO 驱动程序会在其缓冲区中内部缓存所有原始查询结果](https://www.php.net/manual/en/mysqlinfo.concepts.buffering.php)。如果你正在处理大量 Eloquent 记录，请考虑改用 [`lazy` 方法](#chunking-using-lazy-collections)。



<a name="advanced-subqueries"></a>
### 高级子查询

<a name="subquery-selects"></a>
#### 子查询选择

Eloquent 还提供了高级子查询支持，允许你在单个查询中从关联表中提取信息。例如，假设我们有一个航班「目的地」表和一个前往目的地的「航班」表。航班表中包含一个 `arrived_at` 列，用于指示航班到达目的地的时间。

利用查询构建器的 `select` 和 `addSelect` 方法提供的子查询功能，我们可以通过单个查询选择所有「目的地」以及最近到达该目的地的航班名称：

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

此外，查询构建器的 `orderBy` 函数也支持子查询。继续使用我们的航班示例，我们可以使用此功能根据最后一班航班到达该目的地的时间对所有目的地进行排序。同样，这可以通过执行单个数据库查询来完成：

```php
return Destination::orderByDesc(
    Flight::select('arrived_at')
        ->whereColumn('destination_id', 'destinations.id')
        ->orderByDesc('arrived_at')
        ->limit(1)
)->get();
```

<a name="retrieving-single-models"></a>
## 获取单个模型/聚合

除了获取与给定查询匹配的所有记录外，你还可以使用 `find`、`first` 或 `firstWhere` 方法获取单个记录。这些方法不返回模型集合，而是返回单个模型实例：

```php
use App\Models\Flight;

// 通过主键获取模型...
$flight = Flight::find(1);

// 获取与查询约束匹配的第一个模型...
$flight = Flight::where('active', 1)->first();

// 获取与查询约束匹配的第一个模型的替代方法...
$flight = Flight::firstWhere('active', 1);
```



有时你可能希望在找不到结果时执行其他操作。`findOr` 和 `firstOr` 方法将返回单个模型实例，如果未找到结果，则执行给定的闭包。闭包返回的值将被视为方法的结果：

```php
$flight = Flight::findOr(1, function () {
    // ...
});

$flight = Flight::where('legs', '>', 3)->firstOr(function () {
    // ...
});
```

<a name="not-found-exceptions"></a>
#### 未找到异常

有时你可能希望在找不到模型时抛出异常。这在路由或控制器中特别有用。`findOrFail` 和 `firstOrFail` 方法将获取查询的第一个结果；但是，如果未找到结果，将抛出 `Illuminate\Database\Eloquent\ModelNotFoundException`：

```php
$flight = Flight::findOrFail(1);

$flight = Flight::where('legs', '>', 3)->firstOrFail();
```

如果未捕获 `ModelNotFoundException`，将自动向客户端发送 404 HTTP 响应：

```php
use App\Models\Flight;

Route::get('/api/flights/{id}', function (string $id) {
    return Flight::findOrFail($id);
});
```

<a name="retrieving-or-creating-models"></a>
### 获取或创建模型

`firstOrCreate` 方法将尝试使用给定的列/值对查找数据库记录。如果在数据库中找不到模型，将插入一条记录，其属性由第一个数组参数与可选的第二个数组参数合并而成：

`firstOrNew` 方法与 `firstOrCreate` 类似，也将尝试在数据库中查找与给定属性匹配的记录。但是，如果找不到模型，将返回一个新的模型实例。请注意，`firstOrNew` 返回的模型尚未持久化到数据库。你需要手动调用 `save` 方法来持久化它：

```php
use App\Models\Flight;

// 按名称检索航班，如果不存在则创建...
$flight = Flight::firstOrCreate([
    'name' => 'London to Paris'
]);

// 按名称检索航班，或使用名称、延迟和到达时间属性创建...
$flight = Flight::firstOrCreate(
    ['name' => 'London to Paris'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);

// 按名称检索航班，或实例化一个新的 Flight 实例...
$flight = Flight::firstOrNew([
    'name' => 'London to Paris'
]);

// 按名称检索航班，或使用名称、延迟和到达时间属性实例化...
$flight = Flight::firstOrNew(
    ['name' => 'Tokyo to Sydney'],
    ['delayed' => 1, 'arrival_time' => '11:30']
);
```



<a name="retrieving-aggregates"></a>
### 检索聚合

在与 Eloquent 模型交互时，你还可以使用 Laravel  [查询构造器](/docs/laravel/12.x/queries) 中提供的 `count`, `sum`, `max` 和其他的 [聚合方法](/docs/laravel/12.x/queries#aggregates)，正如您所期望的，这些方法返回标量值而不是 Eloquent 模型实例：

```php
$count = Flight::where('active', 1)->count();

$max = Flight::where('active', 1)->max('price');
```

<a name="inserting-and-updating-models"></a>
## 插入和更新模型

<a name="inserts"></a>
### 插入

当然，使用 Eloquent 时，我们不仅需要从数据库中检索模型。我们还需要插入新的记录。幸运的是， Eloquent 会使其变得简单。要将新纪录插入到数据库中，你应该实例化一个新的模型实例并设置模型的属性。然后，在模型实例上调用 `save` 方法：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Flight;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class FlightController extends Controller
{
    /**
     * Store a new flight in the database.
     */
    public function store(Request $request): RedirectResponse
    {
        // Validate the request...

        $flight = new Flight;

        $flight->name = $request->name;

        $flight->save();

        return redirect('/flights');
    }
}
```
在此实例中， 我们将传入的 HTTP 请求中的 `name` 字段分配给 `App\Models\Flight` 模型实例的 `name` 属性。当我们调用 `save` 方法时，会在数据库中插入一条新的记录。在调用 `save` 方法时，模型的 `created_at` 和 `updated_at` 时间戳将自动设置，因此无需手动设置它们。



或者，您可以使用 `create` 方法通过单条 PHP 语句「保存」新模型。 `create` 方法将返回插入的模型实例：

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```

但是，在使用 `create` 方法之前，您需要在模型类上指定 `fillable` 或 `guarded` 属性。 这些属性是必需的，因为默认情况下所有 Eloquent 模型都受到保护，防止批量赋值漏洞。 要了解更多关于批量赋值的信息，请查阅 [批量赋值文档](#mass-assignment) 。

<a name="updates"></a>
### 更新

`save` 方法也可用于更新数据库中已存在的模型。 要更新模型，您应该先检索它，然后设置要更新的任何属性。 接着，调用模型的 `save` 方法。 同样， `updated_at` 时间戳会自动更新，因此无需手动设置其值：

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->name = 'Paris to London';

$flight->save();
```

有时，您可能需要更新现有模型，如果不存在匹配的模型则创建新模型。 与 `firstOrCreate` 方法类似， `updateOrCreate` 方法会持久化模型，因此无需手动调用 `save` 方法。

在下面的示例中，如果存在 `departure` 位置为 `Oakland` 且 `destination` 位置为 `San Diego` 的航班，则将更新其 `price` 和 `discounted` 列。 如果不存在这样的航班，则将创建一个新航班，其属性由第一个参数数组与第二个参数数组合并而成：

```php
$flight = Flight::updateOrCreate(
    ['departure' => 'Oakland', 'destination' => 'San Diego'],
    ['price' => 99, 'discounted' => 1]
);
```

<a name="mass-updates"></a>
#### 批量更新

也可以对匹配给定查询的模型执行更新操作。 在此示例中，所有 `active` 为 1 且 `destination` 为 `San Diego` 的航班将被标记为延误：

```php
Flight::where('active', 1)
    ->where('destination', 'San Diego')
    ->update(['delayed' => 1]);
```

`update` 方法需要一个列和值对的数组，表示应该更新的列。 `update` 方法返回受影响的行数。

> [!警告]
> 通过 Eloquent 执行批量更新时，更新后的模型不会触发 `saving` 、 `saved` 、 `updating` 和 `updated` 模型事件。 这是因为在执行批量更新时，模型实际上从未被检索过。

<a name="examining-attribute-changes"></a>
#### 检查属性变化

Eloquent 提供了 `isDirty` 、 `isClean` 和 `wasChanged` 方法来检查模型的内部状态，并确定其属性自最初检索以来发生了哪些变化。

`isDirty` 方法确定模型的任何属性自检索后是否已被更改。 您可以将特定属性名称或属性数组传递给 `isDirty` 方法，以确定是否有任何属性是「脏的」。 `isClean` 方法将确定属性自模型检索后是否保持不变。 此方法也接受可选的属性参数：

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

`wasChanged` 方法用于判断在当前请求周期内，模型上次保存时是否有任何属性被更改。
如果需要，你可以传递一个属性名来检查某个特定属性是否被更改：

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

`getOriginal` 方法会返回一个数组，包含了模型的**原始属性值**，不论自模型被检索后做了任何修改。
如果需要，你可以传递一个属性名来获取该属性的原始值：

```php
$user = User::find(1);

$user->name; // John
$user->email; // john@example.com

$user->name = 'Jack';
$user->name; // Jack

$user->getOriginal('name'); // John
$user->getOriginal(); // 原始属性的数组...
```

`getChanges` 方法会返回一个数组，包含模型上次保存时被更改的属性；
而 `getPrevious` 方法会返回一个数组，包含模型上次保存前的原始属性值：

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


### 批量赋值（Mass Assignment）

你可以使用 `create` 方法，通过一条 PHP 语句来“保存”一个新模型。
该方法会返回刚刚插入的模型实例：

```php
use App\Models\Flight;

$flight = Flight::create([
    'name' => 'London to Paris',
]);
```



然而，在使用 `create` 方法之前，你需要在模型类上指定 `fillable` 或 `guarded` 属性。
这是必须的，因为所有 Eloquent 模型默认都受到 **批量赋值漏洞** 的保护。

**批量赋值漏洞** 发生在用户传递了一个意料之外的 HTTP 请求字段，并且该字段修改了你数据库中某个你并不打算修改的列。
例如，一个恶意用户可能会通过 HTTP 请求发送一个 `is_admin` 参数，这个参数随后被传递到模型的 `create` 方法，从而让该用户将自己提升为管理员。

所以，首先你应该定义哪些模型属性允许进行批量赋值。
你可以通过在模型中使用 `$fillable` 属性来实现。
例如，我们将 `Flight` 模型的 `name` 属性设为可批量赋值：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Flight extends Model
{
    /**
     * 可以批量赋值的属性。
     *
     * @var array<int, string>
     */
    protected $fillable = ['name'];
}
```

一旦你指定了哪些属性可以批量赋值，就可以使用 `create` 方法在数据库中插入一条新记录。
`create` 方法会返回新创建的模型实例：

```php
$flight = Flight::create(['name' => 'London to Paris']);
```

如果你已经有一个模型实例，你可以使用 `fill` 方法为其填充一个属性数组：

```php
$flight->fill(['name' => 'Amsterdam to Frankfurt']);
```

#### 批量赋值与 JSON 列

在赋值 JSON 列时，每一个列的批量赋值键必须在模型的 `$fillable` 数组中指定。
出于安全考虑，Laravel 在使用 `guarded` 属性时 **不支持更新嵌套的 JSON 属性**：

```php
/**
 * 可以批量赋值的属性。
 *
 * @var array<int, string>
 */
protected $fillable = [
    'options->enabled',
];
```



#### 允许批量赋值

如果你希望让所有属性都可以批量赋值，可以将模型的 `$guarded` 属性定义为空数组。
如果你选择 **完全取消保护** 模型，就需要特别小心，务必手工构建传递给 Eloquent 的 `fill`、`create` 和 `update` 方法的数组：

```php
/**
 * 不能被批量赋值的属性。
 *
 * @var array<string>|bool
 */
protected $guarded = [];
```

#### 批量赋值异常

默认情况下，在执行批量赋值操作时，那些没有包含在 `$fillable` 数组中的属性会被**静默丢弃**。
在生产环境中，这是预期的行为；但是在本地开发时，这可能会导致困惑 —— 因为你可能不明白为什么模型的更改没有生效。

如果你愿意，可以让 Laravel 在尝试填充一个不可批量赋值的属性时 **抛出异常**。
你可以通过调用 `preventSilentlyDiscardingAttributes` 方法来实现。
通常，这个方法应当在应用的 `AppServiceProvider` 类的 `boot` 方法中调用：

```php
use Illuminate\Database\Eloquent\Model;

/**
 * 启动任意应用服务。
 */
public function boot(): void
{
    Model::preventSilentlyDiscardingAttributes($this->app->isLocal());
}
```

### Upserts

Eloquent 的 `upsert` 方法可用于 **在一次原子操作中更新或创建记录**。

-   方法的第一个参数是要插入或更新的值；
-   第二个参数是表中 **唯一标识记录** 的列；
-   第三个参数是当数据库中已经存在匹配记录时需要更新的列。

如果模型启用了时间戳，`upsert` 方法会自动设置 `created_at` 和 `updated_at` 字段：

```php
Flight::upsert([
    ['departure' => 'Oakland', 'destination' => 'San Diego', 'price' => 99],
    ['departure' => 'Chicago', 'destination' => 'New York', 'price' => 150]
], uniqueBy: ['departure', 'destination'], update: ['price']);
```

> [!警告]
> 除了 **SQL Server** 之外，其他所有数据库都要求 `upsert` 方法的第二个参数中的列必须有 “主键（primary）” 或 “唯一（unique）” 索引。
另外，MariaDB 和 MySQL 数据库驱动会忽略 `upsert` 方法的第二个参数，而总是使用数据表自身的 “主键” 和 “唯一” 索引来检测已存在的记录。



## 删除模型

要删除一个模型，你可以在模型实例上调用 `delete` 方法：

```php
use App\Models\Flight;

$flight = Flight::find(1);

$flight->delete();
```

#### 通过主键删除已存在的模型

在上面的例子中，我们先从数据库中检索模型，然后再调用 `delete` 方法。
但是，如果你已经知道模型的主键，可以在不显式检索模型的情况下，通过调用 `destroy` 方法来删除它。
除了接受单个主键外，`destroy` 方法还可以接受多个主键、主键数组，或主键的 [集合](/docs/laravel/12.x/collections)：

```php
Flight::destroy(1);

Flight::destroy(1, 2, 3);

Flight::destroy([1, 2, 3]);

Flight::destroy(collect([1, 2, 3]));
```

如果你在使用 [软删除模型](#soft-deleting)，你可以通过 `forceDestroy` 方法永久删除模型：

```php
Flight::forceDestroy(1);
```

> [!警告]
> `destroy` 方法会逐个加载每个模型，并调用其 `delete` 方法，以便 `deleting` 和 `deleted` 事件能够正确地为每个模型触发。

#### 使用查询删除模型

当然，你也可以构建一个 Eloquent 查询来删除符合条件的所有模型。
在下面的例子中，我们将删除所有被标记为非活动的航班。
与批量更新类似，批量删除不会为被删除的模型触发任何模型事件：

```php
$deleted = Flight::where('active', 0)->delete();
```

To delete all models in a table, you should execute a query without adding any conditions:

```php
$deleted = Flight::query()->delete();
```

> [!警告]
> 当通过 Eloquent 执行批量删除语句时，`deleting` 和 `deleted` 模型事件不会被触发。
这是因为在执行删除语句时，这些模型实际上从未被检索出来。



### 软删除

除了实际从数据库中移除记录之外，Eloquent 还可以对模型进行“软删除”。
当模型被软删除时，它们实际上并不会从数据库中移除。
相反，模型上会设置一个 `deleted_at` 属性，用来表示模型被“删除”的日期和时间。

要为某个模型启用软删除，只需要在模型中添加 `Illuminate\Database\Eloquent\SoftDeletes` trait：

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

> [!注意]
> `SoftDeletes` trait 会自动将 `deleted_at` 属性转换为 `DateTime` / `Carbon` 实例。

你还需要在数据库表中添加 `deleted_at` 列。
Laravel 的 [schema builder](/docs/laravel/12.x/migrations) 提供了一个辅助方法来创建该列：

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

现在，当你在模型上调用 `delete` 方法时，`deleted_at` 列会被设置为当前的日期和时间。
然而，模型对应的数据库记录依然会保留在表中。
当你对启用了软删除的模型进行查询时，这些已软删除的模型会被自动从查询结果中排除。

要判断某个模型实例是否已被软删除，可以使用 `trashed` 方法：

```php
if ($flight->trashed()) {
    // ...
}
```

#### 恢复软删除的模型

有时你可能希望“取消删除”某个已软删除的模型。
要恢复一个软删除的模型，可以在模型实例上调用 `restore` 方法。
`restore` 方法会将模型的 `deleted_at` 列设置为 `null`：

```php
$flight->restore();
```



你也可以在查询中使用 `restore` 方法来恢复多个模型。
同样地，和其他“批量”操作一样，这不会为被恢复的模型分发任何模型事件：

```php
Flight::withTrashed()
    ->where('airline_id', 1)
    ->restore();
```

在构建 [关联关系](/docs/laravel/12.x/eloquent-relationships) 查询时，也可以使用 `restore` 方法：

```php
$flight->history()->restore();
```

#### 永久删除模型

有时你可能需要真正地从数据库中移除某个模型。
你可以使用 `forceDelete` 方法来将一个已软删除的模型从数据库表中永久删除：

```php
$flight->forceDelete();
```

在构建 Eloquent 关联关系查询时，同样也可以使用 `forceDelete` 方法：

```php
$flight->history()->forceDelete();
```

### 查询软删除的模型

#### 包含软删除的模型

如前所述，软删除的模型会被自动从查询结果中排除。
然而，你可以在查询中调用 `withTrashed` 方法，强制将软删除的模型包含在结果中：

```php
use App\Models\Flight;

$flights = Flight::withTrashed()
    ->where('account_id', 1)
    ->get();
```

在构建 [关联关系](/docs/laravel/12.x/eloquent-relationships) 查询时，也可以调用 `withTrashed` 方法

```php
$flight->history()->withTrashed()->get();
```

#### 仅检索软删除的模型

`onlyTrashed` 方法将检索 **仅有** 软删除的模型：

```php
$flights = Flight::onlyTrashed()
    ->where('airline_id', 1)
    ->get();
```

## 修剪（Pruning）模型

有时你可能希望定期删除一些不再需要的模型。
为此，你可以在模型中添加 `Illuminate\Database\Eloquent\Prunable` 或 `Illuminate\Database\Eloquent\MassPrunable` trait。
在模型中添加其中一个 trait 之后，实现一个 `prunable` 方法，该方法返回一个 Eloquent 查询构造器，用来解析出那些不再需要的模型：

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
     * 获取可修剪的模型查询。
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', now()->subMonth());
    }
}
```



当将模型标记为 `Prunable` 时，你也可以在模型上定义一个 `pruning` 方法。该方法会在模型被删除之前调用。此方法可用于删除与该模型相关的其他资源（例如存储的文件），以便在模型从数据库中被永久移除之前清理这些资源：

```php
/**
 * 为修剪做准备。
 */
protected function pruning(): void
{
    // ...
}
```

在配置好可修剪模型后，你需要在应用的 `routes/console.php` 文件中调度 `model:prune` Artisan 命令。你可以自由选择该命令运行的合适时间间隔：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('model:prune')->daily();
```

在幕后，`model:prune` 命令会自动检测应用中 `app/Models` 目录下的所有 “Prunable” 模型。
如果你的模型位于其他位置，你可以使用 `--model` 选项来指定模型类名：

```php
Schedule::command('model:prune', [
    '--model' => [Address::class, Flight::class],
])->daily();
```

如果你希望在修剪时排除某些模型，同时修剪所有其他被检测到的模型，可以使用 `--except` 选项：

```php
Schedule::command('model:prune', [
    '--except' => [Address::class, Flight::class],
])->daily();
```

你可以通过执行带有 `--pretend` 选项的 `model:prune` 命令来测试你的 `prunable` 查询。
在“假装”模式下，`model:prune` 命令只会报告如果实际运行会被修剪的记录数量：

```shell
php artisan model:prune --pretend
```

> [!警告]
> 如果软删除模型匹配了可修剪查询，它们将会被永久删除（`forceDelete`）。



#### 批量修剪（Mass Pruning）

当模型使用了 `Illuminate\Database\Eloquent\MassPrunable` 特性时，模型会通过批量删除查询从数据库中删除。
因此，`pruning` 方法不会被调用，模型的 `deleting` 和 `deleted` 事件也不会被触发。
这是因为这些模型在删除之前根本不会被实际检索，从而使修剪过程更加高效：

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
     * 获取可修剪的模型查询。
     */
    public function prunable(): Builder
    {
        return static::where('created_at', '<=', now()->subMonth());
    }
}
```

## 复制模型

你可以使用 `replicate` 方法创建现有模型实例的未保存副本。
当你有多个模型实例共享许多相同属性时，这个方法特别有用：

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

如果你希望在复制时排除一个或多个属性，可以将属性名数组传给 `replicate` 方法：

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

## 查询作用域

### 全局作用域（Global Scopes）

全局作用域允许你为某个模型的所有查询添加约束条件。
Laravel 自身的[软删除](#soft-deleting)功能就利用全局作用域，只检索数据库中“未删除”的模型。
编写你自己的全局作用域可以提供一种方便的方式，确保针对某个模型的每个查询都应用特定约束。



#### 生成作用域

要生成一个新的全局作用域，你可以调用 `make:scope` Artisan 命令。该命令会将生成的作用域类放在应用的 `app/Models/Scopes` 目录中：

```shell
php artisan make:scope AncientScope
```

#### 编写全局作用域

编写全局作用域很简单。首先，使用 `make:scope` 命令生成一个实现了 `Illuminate\Database\Eloquent\Scope` 接口的类。
`Scope` 接口要求你实现一个方法：`apply`。
`apply` 方法可根据需要向查询添加 `where` 条件或其他类型的子句：

```php
<?php

namespace App\Models\Scopes;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;

class AncientScope implements Scope
{
    /**
     * 将作用域应用到指定的 Eloquent 查询构造器。
     */
    public function apply(Builder $builder, Model $model): void
    {
        $builder->where('created_at', '<', now()->subYears(2000));
    }
}
```

> [!注意]
> 如果你的全局作用域需要向查询的 select 子句添加列，应使用 `addSelect` 方法而不是 `select`。
> 这样可以避免意外替换查询中已有的 select 子句。


#### 应用全局作用域（Applying Global Scopes）

要将全局作用域分配给模型，你可以直接在模型上使用 `ScopedBy` 属性：

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

或者，你也可以通过重写模型的 `booted` 方法手动注册全局作用域，并调用模型的 `addGlobalScope` 方法。
`addGlobalScope` 方法只接受你的作用域实例作为参数：

```php
<?php

namespace App\Models;

use App\Models\Scopes\AncientScope;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 "booted" 方法。
     */
    protected static function booted(): void
    {
        static::addGlobalScope(new AncientScope);
    }
}
```



在上面的示例中，将作用域添加到 `App\Models\User` 模型之后，对 `User::all()` 的调用会执行如下 SQL 查询：

```sql
select * from `users` where `created_at` < 0021-02-18 00:00:00
```

#### 匿名全局作用域

Eloquent 也允许你使用闭包定义全局作用域，这对于一些不值得单独创建类的简单作用域来说特别有用。
当使用闭包定义全局作用域时，你应将作用域的名称作为第一个参数传递给 `addGlobalScope` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 "booted" 方法。
     */
    protected static function booted(): void
    {
        static::addGlobalScope('ancient', function (Builder $builder) {
            $builder->where('created_at', '<', now()->subYears(2000));
        });
    }
}
```

#### 移除全局作用域

如果你希望在某个查询中移除全局作用域，可以使用 `withoutGlobalScope` 方法。
此方法接收全局作用域的类名作为唯一参数：

```php
User::withoutGlobalScope(AncientScope::class)->get();
```

如果你使用闭包定义了全局作用域，则应传递你分配给该全局作用域的字符串名称：

```php
User::withoutGlobalScope('ancient')->get();
```

如果你希望移除多个或全部的全局作用域，可以使用 `withoutGlobalScopes` 方法：

```php
// 移除所有全局作用域...
User::withoutGlobalScopes()->get();

// 移除部分全局作用域...
User::withoutGlobalScopes([
    FirstScope::class, SecondScope::class
])->get();
```



### 本地作用域（Local Scopes）

本地作用域允许你定义一组常用的查询约束，并在应用的各个地方轻松复用。
例如，你可能经常需要获取所有被认为是“热门”的用户。
要定义一个作用域，只需在 Eloquent 方法上添加 `Scope` 属性。

作用域方法应始终返回相同的查询构造器实例（`Builder`）或 `void`：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 将查询作用域限定为仅包含热门用户。
     */
    #[Scope]
    protected function popular(Builder $query): void
    {
        $query->where('votes', '>', 100);
    }

    /**
     * 将查询作用域限定为仅包含活跃用户。
     */
    #[Scope]
    protected function active(Builder $query): void
    {
        $query->where('active', 1);
    }
}
```

#### 使用本地作用域

一旦定义了作用域，你就可以在查询模型时调用这些作用域方法。
你甚至可以链式调用多个作用域：

```php
use App\Models\User;

$users = User::popular()->active()->orderBy('created_at')->get();
```

如果要通过 `or` 运算符组合多个 Eloquent 模型作用域，可能需要借助闭包来实现正确的[逻辑分组](/docs/laravel/12.x/queries#logical-grouping)：

```php
$users = User::popular()->orWhere(function (Builder $query) {
    $query->active();
})->get();
```

不过，由于这种方式会显得繁琐，Laravel 提供了一个“高阶” `orWhere` 方法，允许你在不使用闭包的情况下更流畅地链式调用作用域：

```php
$users = User::popular()->orWhere->active()->get();
```


#### 动态作用域

有时您可能希望定义一个接受参数的作用域。 开始使用只需将额外参数添加到作用域方法的签名中即可。 作用域参数应在 `$query` 参数之后定义：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 将查询范围限制为仅包含给定类型的用户。
     */
    #[Scope]
    protected function ofType(Builder $query, string $type): void
    {
        $query->where('type', $type);
    }
}
```

一旦将预期的参数添加到作用域方法的签名中，您就可以在调用作用域时传递参数：

```php
$users = User::ofType('admin')->get();
```

<a name="pending-attributes"></a>
### 待定属性

如果您希望使用作用域来创建具有与约束作用域所用属性相同的模型，可以在构建作用域查询时使用 `withAttributes` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Scope;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    /**
     * 将查询范围限制为仅包含草稿。
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

`withAttributes` 方法将使用给定的属性向查询添加 `where` 条件，并且还会将这些属性添加到通过作用域创建的任何模型中：

```php
$draft = Post::draft()->create(['title' => 'In Progress']);

$draft->hidden; // true
```

要指示 `withAttributes` 方法不向查询添加 `where` 条件，您可以将 `asConditions` 参数设置为 `false`：

```php
$query->withAttributes([
    'hidden' => true,
], asConditions: false);
```

<a name="comparing-models"></a>
## 模型比较

有时您可能需要判断两个模型是否「相同」。 `is` 和 `isNot` 方法可用于快速验证两个模型是否具有相同的主键、数据表和数据库连接：

```php
if ($post->is($anotherPost)) {
    // ...
}

if ($post->isNot($anotherPost)) {
    // ...
}
```

在使用 `belongsTo` 、 `hasOne` 、 `morphTo` 和 `morphOne` [关联关系](https://laravel.com/docs/laravel/12.x/eloquent-relationships) 时， `is` 和 `isNot` 方法也可用。 当您希望比较关联模型而不需要发起查询检索该模型时，此方法特别有用：

```php
if ($post->author()->is($user)) {
    // ...
}
```

<a name="events"></a>
## 事件

> [!注意]
> 想要将 Eloquent 事件直接广播到您的客户端应用？ 查看 Laravel 的 [模型事件广播](https://laravel.com/docs/laravel/12.x/broadcasting#model-broadcasting) 。

Eloquent 模型会派发多个事件，允许您挂接到模型生命周期的以下时刻： `retrieved` 、 `creating` 、 `created` 、 `updating` 、 `updated` 、 `saving` 、 `saved` 、 `deleting` 、 `deleted` 、 `trashed` 、 `forceDeleting` 、 `forceDeleted` 、 `restoring` 、 `restored` 和 `replicating` 。

当从数据库中检索现有模型时，会派发 `retrieved` 事件。 当首次保存新模型时，会派发 `creating` 和 `created` 事件。 当修改现有模型并调用 `save` 方法时，会派发 `updating` / `updated` 事件。 当创建或更新模型时，会派发 `saving` / `saved` 事件 —— 即使模型的属性未更改。 以 `-ing` 结尾的事件名称在对模型的任何更改持久化之前派发，而以 `-ed` 结尾的事件则在模型的更改持久化之后派发。

要开始监听模型事件，请在 Eloquent 模型上定义 `$dispatchesEvents` 属性。 此属性将 Eloquent 模型生命周期的各个节点映射到您自己的 [事件类](https://laravel.com/docs/laravel/12.x/events) 。 每个模型事件类都应该通过其构造函数接收受影响模型的实例：

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
     * 模型的事件映射
     *
     * @var array<string, string>
     */
    protected $dispatchesEvents = [
        'saved' => UserSaved::class,
        'deleted' => UserDeleted::class,
    ];
}
```

定义并映射 Eloquent 事件后，您可以使用 [事件监听器](https://laravel.com/docs/laravel/12.x/events#defining-listeners) 来处理这些事件。

> [!警告]
> 通过 Eloquent 执行批量更新或删除查询时，受影响的模型不会派发 `saved` 、 `updated` 、 `deleting` 和 `deleted` 模型事件。 这是因为在执行批量更新或删除时，模型实际上从未被检索过。

<a name="events-using-closures"></a>
### 使用闭包

除了使用自定义事件类之外，您还可以注册在各种模型事件派发时执行的闭包。 通常，您应该在模型的 `booted` 方法中注册这些闭包：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    /**
     * 模型的 "booted" 方法
     */
    protected static function booted(): void
    {
        static::created(function (User $user) {
            // ...
        });
    }
}
```

如果需要，在注册模型事件时可以使用 [可队列化的匿名事件监听器](https://laravel.com/docs/laravel/12.x/events#queuable-anonymous-event-listeners) 。 这将指示 Laravel 使用应用的 [队列](https://laravel.com/docs/laravel/12.x/queues) 在后台执行模型事件监听器：

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

如果您需要在给定模型上监听多个事件，可以使用观察者将所有监听器分组到单个类中。 观察者类的方法名称反映了您希望监听的 Eloquent 事件。 这些方法中的每一个都接收受影响的模型作为其唯一参数。 `make:observer` Artisan 命令是创建新观察者类的最简单方法：

```shell
php artisan make:observer UserObserver --model=User
```

此命令将新的观察者放置在 `app/Observers` 目录中。 如果该目录不存在，Artisan 将为您创建它。 您的新观察者将如下所示：

```php
<?php

namespace App\Observers;

use App\Models\User;

class UserObserver
{
    /**
     * 处理 User "created" 事件
     */
    public function created(User $user): void
    {
        // ...
    }

    /**
     * 处理 User "updated" 事件
     */
    public function updated(User $user): void
    {
        // ...
    }

    /**
     * 处理 User "deleted" 事件
     */
    public function deleted(User $user): void
    {
        // ...
    }

    /**
     * 处理 User "restored" 事件
     */
    public function restored(User $user): void
    {
        // ...
    }

    /**
     * 处理 User "forceDeleted" 事件
     */
    public function forceDeleted(User $user): void
    {
        // ...
    }
}
```

要注册观察者，您可以在相应的模型上添加 `ObservedBy` 属性：

```php
use App\Observers\UserObserver;
use Illuminate\Database\Eloquent\Attributes\ObservedBy;

#[ObservedBy([UserObserver::class])]
class User extends Authenticatable
{
    //
}
```

或者，您可以通过在要观察的模型上调用 `observe` 方法手动注册观察者。 您可以在应用程序的 `AppServiceProvider` 类的 `boot` 方法中注册观察者：

```php
use App\Models\User;
use App\Observers\UserObserver;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    User::observe(UserObserver::class);
}
```

> [!注意]
> 观察者还可以监听其他事件，例如 `saving` 和 `retrieved` 。 这些事件在 [事件](#events) 文档中有详细说明。

<a name="observers-and-database-transactions"></a>
#### 观察者与数据库事务

当在数据库事务中创建模型时，您可能希望指示观察者仅在数据库事务提交后才执行其事件处理程序。 您可以通过在观察者上实现 `ShouldHandleEventsAfterCommit` 接口来实现这一点。 如果当前没有进行中的数据库事务，事件处理程序将立即执行：

```php
<?php

namespace App\Observers;

use App\Models\User;
use Illuminate\Contracts\Events\ShouldHandleEventsAfterCommit;

class UserObserver implements ShouldHandleEventsAfterCommit
{
    /**
     * 处理 User "created" 事件
     */
    public function created(User $user): void
    {
        // ...
    }
}
```

<a name="muting-events"></a>
### 静默事件

您有时可能需要临时「静音」模型触发的所有事件。 您可以使用 `withoutEvents` 方法来实现这一点。 `withoutEvents` 方法接受一个闭包作为其唯一参数。 在此闭包内执行的任何代码都不会派发模型事件，闭包返回的任何值都将由 `withoutEvents` 方法返回：

```php
use App\Models\User;

$user = User::withoutEvents(function () {
    User::findOrFail(1)->delete();

    return User::find(2);
});
```

<a name="saving-a-single-model-without-events"></a>
#### 无事件保存单个模型

有时您可能希望在不派发任何事件的情况下「保存」给定模型。 您可以使用 `saveQuietly` 方法来实现：

```php
$user = User::findOrFail(1);

$user->name = 'Victoria Faith';

$user->saveQuietly();
```

您还可以在不派发任何事件的情况下「更新」、「删除」、「软删除」、「恢复」和「复制」给定模型：

```php
$user->deleteQuietly();
$user->forceDeleteQuietly();
$user->restoreQuietly();
```

# 缓存

- [简介](#introduction)
- [配置](#configuration)
    - [驱动前置条件](#driver-prerequisites)
- [缓存使用](#cache-usage)
    - [获取缓存实例](#obtaining-a-cache-instance)
    - [从缓存中检索项目](#retrieving-items-from-the-cache)
    - [在缓存中存储项目](#storing-items-in-the-cache)
    - [延长项目生命周期](#extending-item-lifetime)
    - [从缓存中移除项目](#removing-items-from-the-cache)
    - [缓存记忆化](#cache-memoization)
    - [缓存辅助函数](#the-cache-helper)
- [缓存标签](#cache-tags)
- [原子锁](#atomic-locks)
    - [管理锁](#managing-locks)
    - [跨进程管理锁](#managing-locks-across-processes)
    - [刷新锁](#refreshing-locks)
    - [并发限制](#concurrency-limiting)
- [缓存故障转移](#cache-failover)
- [添加自定义缓存驱动](#adding-custom-cache-drivers)
    - [编写驱动](#writing-the-driver)
    - [注册驱动](#registering-the-driver)
- [事件](#events)

<a name="introduction"></a>
## 简介

应用执行的某些数据检索或处理任务可能会消耗大量 CPU，或需要数秒才能完成。遇到这种情况，通常会将检索到的数据缓存一段时间，以便后续请求相同数据时能够快速获取。缓存数据通常存储在 [Memcached](https://memcached.org) 或 [Redis](https://redis.io) 等速度极快的数据存储中。

幸运的是，Laravel 为各种缓存后端提供了一套富有表现力的统一 API，让你能够利用它们极快的数据检索速度来提升 Web 应用性能。

<a name="configuration"></a>
## 配置

应用的缓存配置文件位于 `config/cache.php`。在此文件中，可以指定应用默认使用的缓存存储。Laravel 开箱即支持 [Memcached](https://memcached.org)、[Redis](https://redis.io)、[DynamoDB](https://aws.amazon.com/dynamodb)、关系型数据库和文件系统磁盘等常用缓存后端。此外，Laravel 还提供基于文件的缓存驱动，而 `array` 和 `null` 缓存驱动则为自动化测试提供了便捷的缓存后端。

缓存配置文件还包含多种其他选项，你可以自行查看。默认情况下，Laravel 配置为使用 `database` 缓存驱动，将序列化后的缓存对象存储在应用数据库中。

<a name="driver-prerequisites"></a>
### 驱动前置条件

<a name="prerequisites-database"></a>
#### Database

使用 `database` 缓存驱动时，需要一张数据库表来保存缓存数据。通常，Laravel 默认的 `0001_01_01_000001_create_cache_table.php` [数据库迁移](/docs/{{version}}/migrations)中已经包含此表；不过，如果应用不包含该迁移，可以使用 `make:cache-table` Artisan 命令创建：

```shell
php artisan make:cache-table

php artisan migrate
```

<a name="memcached"></a>
#### Memcached

使用 Memcached 驱动前，需要安装 [Memcached PECL 软件包](https://pecl.php.net/package/memcached)。可以在 `config/cache.php` 配置文件中列出所有 Memcached 服务器。该文件已经包含一个 `memcached.servers` 配置项，方便你开始使用：

```php
'memcached' => [
    // ...

    'servers' => [
        [
            'host' => env('MEMCACHED_HOST', '127.0.0.1'),
            'port' => env('MEMCACHED_PORT', 11211),
            'weight' => 100,
        ],
    ],
],
```

如有需要，可以将 `host` 选项设置为 UNIX 套接字路径。此时，应将 `port` 选项设置为 `0`：

```php
'memcached' => [
    // ...

    'servers' => [
        [
            'host' => '/var/run/memcached/memcached.sock',
            'port' => 0,
            'weight' => 100
        ],
    ],
],
```

<a name="redis"></a>
#### Redis

在 Laravel 中使用 Redis 缓存前，需要通过 PECL 安装 PhpRedis PHP 扩展，或通过 Composer 安装 `predis/predis` 软件包（~2.0）。[Laravel Sail](/docs/{{version}}/sail) 已包含此扩展。此外，[Laravel Cloud](https://cloud.laravel.com) 和 [Laravel Forge](https://forge.laravel.com) 等 Laravel 官方应用平台默认也安装了 PhpRedis 扩展。

有关 Redis 配置的更多信息，请参阅其 [Laravel 文档页面](/docs/{{version}}/redis#configuration)。

<a name="storage"></a>
#### 存储

`storage` 缓存驱动允许你将缓存值存储在应用已配置的任意[文件系统磁盘](/docs/{{version}}/filesystem)上。如果要使用现有磁盘（例如 S3 磁盘）作为键 / 值缓存存储，此功能会很有用：

```php
'storage' => [
    'driver' => 'storage',
    'disk' => env('CACHE_STORAGE_DISK'),
    'path' => env('CACHE_STORAGE_PATH', 'framework/cache/data'),
],
```

<a name="dynamodb"></a>
#### DynamoDB

使用 [DynamoDB](https://aws.amazon.com/dynamodb) 缓存驱动前，必须创建一个 DynamoDB 表来存储所有缓存数据。通常，此表应命名为 `cache`。不过，应根据 `cache` 配置文件中 `stores.dynamodb.table` 配置值来命名该表。也可以通过 `DYNAMODB_CACHE_TABLE` 环境变量设置表名。

该表还应具有一个字符串分区键，其名称应与应用 `cache` 配置文件中 `stores.dynamodb.attributes.key` 配置项的值对应。默认情况下，分区键应命名为 `key`。

通常，DynamoDB 不会主动从表中移除已过期的项目。因此，应在表上[启用生存时间（TTL）](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)。配置表的 TTL 设置时，应将 TTL 属性名称设置为 `expires_at`。

接下来，安装 AWS SDK，以便 Laravel 应用与 DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

此外，应确保为 DynamoDB 缓存存储配置选项提供相应的值。通常，`AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 等选项应在应用的 `.env` 配置文件中定义：

```php
'dynamodb' => [
    'driver' => 'dynamodb',
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => env('DYNAMODB_CACHE_TABLE', 'cache'),
    'endpoint' => env('DYNAMODB_ENDPOINT'),
],
```

<a name="mongodb"></a>
#### MongoDB

如果使用 MongoDB，官方 `mongodb/laravel-mongodb` 软件包提供了 `mongodb` 缓存驱动，可以通过 `mongodb` 数据库连接进行配置。MongoDB 支持 TTL 索引，可用于自动清除过期的缓存项目。

有关 MongoDB 配置的更多信息，请参阅 MongoDB 的[缓存与锁文档](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/cache/)。

<a name="cache-usage"></a>
## 缓存使用

<a name="obtaining-a-cache-instance"></a>
### 获取缓存实例

若要获取缓存存储实例，可以使用 `Cache` 门面，本文档将始终使用该门面。`Cache` 门面提供了一种简洁便利的方式来访问 Laravel 缓存契约的底层实现：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Cache;

class UserController extends Controller
{
    /**
     * 显示应用的所有用户列表。
     */
    public function index(): array
    {
        $value = Cache::get('key');

        return [
            // ...
        ];
    }
}
```

<a name="accessing-multiple-cache-stores"></a>
#### 访问多个缓存存储

使用 `Cache` 门面，可以通过 `store` 方法访问不同的缓存存储。传给 `store` 方法的键应与 `cache` 配置文件中 `stores` 配置数组所列的存储之一对应：

```php
$value = Cache::store('file')->get('foo');

Cache::store('redis')->put('bar', 'baz', 600); // 10 分钟
```

<a name="retrieving-items-from-the-cache"></a>
### 从缓存中检索项目

`Cache` 门面的 `get` 方法用于从缓存中检索项目。如果缓存中不存在该项目，将返回 `null`。如果愿意，可以向 `get` 方法传递第二个参数，指定项目不存在时要返回的默认值：

```php
$value = Cache::get('key');

$value = Cache::get('key', 'default');
```

甚至可以传入闭包作为默认值。如果指定项目在缓存中不存在，将返回闭包的执行结果。传入闭包可以将默认值的检索推迟到需要时再从数据库或其他外部服务中获取：

```php
$value = Cache::get('key', function () {
    return DB::table(/* ... */)->get();
});
```

<a name="determining-item-existence"></a>
#### 判断项目是否存在

可以使用 `has` 方法判断缓存中是否存在某个项目。如果项目存在但其值为 `null`，此方法也会返回 `false`：

```php
if (Cache::has('key')) {
    // ...
}
```

<a name="incrementing-decrementing-values"></a>
#### 递增 / 递减值

可以使用 `increment` 和 `decrement` 方法调整缓存中整数项目的值。这两个方法都接受可选的第二个参数，用于指定递增或递减的数值：

```php
// 如果值不存在，则将其初始化...
Cache::add('key', 0, now()->plus(hours: 4));

// 递增或递减值...
Cache::increment('key');
Cache::increment('key', $amount);
Cache::decrement('key');
Cache::decrement('key', $amount);
```

<a name="retrieve-store"></a>
#### 检索并存储

有时，你可能希望从缓存中检索项目，并在所请求的项目不存在时存储默认值。例如，可能希望从缓存中检索所有用户；如果缓存中不存在，则从数据库检索并将其添加到缓存。可以使用 `Cache::remember` 方法来完成此操作：

```php
$value = Cache::remember('users', $seconds, function () {
    return DB::table('users')->get();
});
```

如果缓存中不存在该项目，系统将执行传给 `remember` 方法的闭包，并将其结果放入缓存。

如果需要知道项目是从缓存中检索的，而不是通过执行给定闭包获得的，可以使用 `rememberWithWarmth` 方法。该方法返回一个数组，其中包含缓存值和一个布尔值，用于指示项目是否为「热」数据，即该项目是从缓存中检索的，而不是通过闭包解析的：

```php
[$value, $warm] = Cache::rememberWithWarmth('users', $seconds, function () {
    return DB::table('users')->get();
});
```

可以使用 `rememberForever` 方法从缓存中检索项目；如果该项目不存在，则将其永久存储：

```php
$value = Cache::rememberForever('users', function () {
    return DB::table('users')->get();
});
```

<a name="swr"></a>
#### 过期后重新验证

使用 `Cache::remember` 方法时，如果缓存值已经过期，部分用户可能会遇到响应缓慢的情况。对于某些类型的数据，在后台重新计算缓存值的同时提供部分陈旧的数据会很有用，这样可以避免部分用户在计算缓存值时遇到响应缓慢。这通常称为「过期后重新验证」（stale-while-revalidate）模式，`Cache::flexible` 方法提供了此模式的实现。

`flexible` 方法接受一个数组，用于指定缓存值被视为「新鲜」的时长，以及何时变为「陈旧」。数组中的第一个值表示缓存被视为新鲜状态的秒数，第二个值则定义了在必须重新计算前，可以将其作为陈旧数据提供多长时间。

如果请求发生在新鲜期内（第一个值之前），系统会立即返回缓存，无须重新计算。如果请求发生在陈旧期内（两个值之间），系统会向用户提供陈旧值，并注册一个[延迟函数](/docs/{{version}}/helpers#deferred-functions)，在响应发送给用户后刷新缓存值。如果请求发生在第二个值之后，则缓存被视为已过期，并会立即重新计算该值，这可能导致用户收到较慢的响应：

```php
$value = Cache::flexible('users', [5, 10], function () {
    return DB::table('users')->get();
});
```

<a name="retrieve-delete"></a>
#### 检索并删除

如果需要从缓存中检索项目并将其删除，可以使用 `pull` 方法。与 `get` 方法一样，如果缓存中不存在该项目，将返回 `null`：

```php
$value = Cache::pull('key');

$value = Cache::pull('key', 'default');
```

<a name="storing-items-in-the-cache"></a>
### 在缓存中存储项目

可以使用 `Cache` 门面的 `put` 方法在缓存中存储项目：

```php
Cache::put('key', 'value', $seconds = 10);
```

如果未向 `put` 方法传递存储时长，该项目将被无限期存储：

```php
Cache::put('key', 'value');
```

除了将秒数作为整数传入外，也可以传入一个 `DateTime` 实例，表示缓存项目所需的过期时间：

```php
Cache::put('key', 'value', now()->plus(minutes: 10));
```

<a name="store-if-not-present"></a>
#### 不存在时存储

只有当缓存存储中尚不存在该项目时，`add` 方法才会将其添加到缓存。如果项目确实已添加到缓存，该方法将返回 `true`；否则返回 `false`。`add` 方法是一项原子操作：

```php
Cache::add('key', 'value', $seconds);
```

<a name="extending-item-lifetime"></a>
### 延长项目生命周期

`touch` 方法允许你延长现有缓存项目的生命周期（TTL）。如果缓存项目存在且成功延长其过期时间，`touch` 方法将返回 `true`。如果缓存中不存在该项目，该方法将返回 `false`：

```php
Cache::touch('key', 3600);
```

可以提供 `DateTimeInterface`、`DateInterval` 或 `Carbon` 实例来指定确切的过期时间：

```php
Cache::touch('key', now()->addHours(2));
```

<a name="storing-items-forever"></a>
#### 永久存储项目

可以使用 `forever` 方法将项目永久存储在缓存中。由于这些项目不会过期，必须使用 `forget` 方法手动将其从缓存中移除：

```php
Cache::forever('key', 'value');
```

> [!NOTE]
> 如果使用 Memcached 驱动，当缓存达到大小上限时，「永久」存储的项目可能会被移除。

<a name="removing-items-from-the-cache"></a>
### 从缓存中移除项目

可以使用 `forget` 方法从缓存中移除项目：

```php
Cache::forget('key');
```

还可以通过提供零或负数的过期秒数来移除项目：

```php
Cache::put('key', 'value', 0);

Cache::put('key', 'value', -5);
```

可以使用 `flush` 方法清空整个缓存：

```php
Cache::flush();
```

可以使用 `flushLocks` 方法清除缓存中的所有原子锁：

```php
Cache::flushLocks();
```

> [!WARNING]
> 清空缓存时不会遵循已配置的缓存「前缀」，而是会移除缓存中的所有条目。清除由其他应用共享的缓存时，请务必慎重考虑。

<a name="cache-memoization"></a>
### 缓存记忆化

Laravel 的 `memo` 缓存驱动允许你在单个请求或任务执行期间，将已解析的缓存值临时存储在内存中。这可以避免在同一次执行中重复命中缓存，从而显著提升性能。

若要使用记忆化缓存，请调用 `memo` 方法：

```php
use Illuminate\Support\Facades\Cache;

$value = Cache::memo()->get('key');
```

`memo` 方法可以选择接受缓存存储的名称，用于指定记忆化驱动要装饰的底层缓存存储：

```php
// 使用默认缓存存储...
$value = Cache::memo()->get('key');

// 使用 Redis 缓存存储...
$value = Cache::memo('redis')->get('key');
```

对于给定的键，第一次调用 `get` 会从缓存存储中检索值，但同一请求或任务中的后续调用将从内存中检索值：

```php
// 命中缓存...
$value = Cache::memo()->get('key');

// 不命中缓存，返回记忆化值...
$value = Cache::memo()->get('key');
```

调用修改缓存值的方法（例如 `put`、`increment`、`remember` 等）时，记忆化缓存会自动忘记记忆化值，并将修改方法的调用委托给底层缓存存储：

```php
Cache::memo()->put('name', 'Taylor'); // 写入底层缓存...
Cache::memo()->get('name');           // 命中底层缓存...
Cache::memo()->get('name');           // 已记忆化，不命中缓存...

Cache::memo()->put('name', 'Tim');    // 忘记记忆化值，写入新值...
Cache::memo()->get('name');           // 再次命中底层缓存...
```

<a name="the-cache-helper"></a>
### 缓存辅助函数

除了使用 `Cache` 门面外，还可以使用全局 `cache` 函数通过缓存检索和存储数据。使用单个字符串参数调用 `cache` 函数时，它将返回给定键的值：

```php
$value = cache('key');
```

如果向该函数提供键 / 值对数组和过期时间，它会在指定时长内将值存储在缓存中：

```php
cache(['key' => 'value'], $seconds);

cache(['key' => 'value'], now()->plus(minutes: 10));
```

不带任何参数调用 `cache` 函数时，它会返回 `Illuminate\Contracts\Cache\Factory` 实现的实例，允许你调用其他缓存方法：

```php
cache()->remember('users', $seconds, function () {
    return DB::table('users')->get();
});
```

> [!NOTE]
> 测试对全局 `cache` 函数的调用时，可以像[测试门面](/docs/{{version}}/mocking#mocking-facades)一样使用 `Cache::shouldReceive` 方法。

<a name="cache-tags"></a>
## 缓存标签

> [!WARNING]
> 使用 `file`、`dynamodb`、`database` 或 `storage` 缓存驱动时，不支持缓存标签。

<a name="storing-tagged-cache-items"></a>
### 存储带标签的缓存项目

缓存标签允许你为缓存中的相关项目添加标签，然后清空分配了指定标签的所有缓存值。可以传入一个有序的标签名称数组来访问带标签的缓存。例如，下面访问一个带标签的缓存，并使用 `put` 将值放入缓存：

```php
use Illuminate\Support\Facades\Cache;

Cache::tags(['people', 'artists'])->put('John', $john, $seconds);
Cache::tags(['people', 'authors'])->put('Anne', $anne, $seconds);
```

<a name="accessing-tagged-cache-items"></a>
### 访问带标签的缓存项目

如果不同时提供存储值时使用的标签，就无法访问通过标签存储的项目。若要检索带标签的缓存项目，请将相同的有序标签列表传给 `tags` 方法，然后使用要检索的键调用 `get` 方法：

```php
$john = Cache::tags(['people', 'artists'])->get('John');

$anne = Cache::tags(['people', 'authors'])->get('Anne');
```

<a name="removing-tagged-cache-items"></a>
### 移除带标签的缓存项目

可以清空分配了某个标签或标签列表的所有项目。例如，以下代码会移除带有 `people`、`authors` 或同时带有这两个标签的所有缓存。因此，`Anne` 和 `John` 都会从缓存中移除：

```php
Cache::tags(['people', 'authors'])->flush();
```

相比之下，以下代码只会移除带有 `authors` 标签的缓存值，因此会移除 `Anne`，但不会移除 `John`：

```php
Cache::tags('authors')->flush();
```

<a name="atomic-locks"></a>
## 原子锁

> [!WARNING]
> 若要使用此功能，应用必须将 `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array` 缓存驱动作为默认缓存驱动。此外，所有服务器必须与同一个中央缓存服务器通信。

<a name="managing-locks"></a>
### 管理锁

原子锁允许你操作分布式锁，而无须担心竞态条件。例如，[Laravel Cloud](https://cloud.laravel.com) 使用原子锁来确保服务器上同一时间只执行一个远程任务。可以使用 `Cache::lock` 方法创建和管理锁：

```php
use Illuminate\Support\Facades\Cache;

$lock = Cache::lock('foo', 10);

if ($lock->get()) {
    // 获取锁 10 秒...

    $lock->release();
}
```

`get` 方法也接受闭包。闭包执行完毕后，Laravel 会自动释放锁：

```php
Cache::lock('foo', 10)->get(function () {
    // 获取锁 10 秒，并自动释放...
});
```

如果请求锁时该锁不可用，可以指示 Laravel 等待指定的秒数。如果在指定时限内无法获取锁，系统将抛出 `Illuminate\Contracts\Cache\LockTimeoutException`：

```php
use Illuminate\Contracts\Cache\LockTimeoutException;

$lock = Cache::lock('foo', 10);

try {
    $lock->block(5);

    // 最多等待 5 秒后获取锁...
} catch (LockTimeoutException $e) {
    // 无法获取锁...
} finally {
    $lock->release();
}
```

可以通过向 `block` 方法传递闭包来简化上述示例。向此方法传递闭包时，Laravel 会尝试在指定秒数内获取锁，并在闭包执行完毕后自动释放锁：

```php
Cache::lock('foo', 10)->block(5, function () {
    // 最多等待 5 秒后获取锁 10 秒...
});
```

<a name="managing-locks-across-processes"></a>
### 跨进程管理锁

有时，你可能希望在一个进程中获取锁，并在另一个进程中释放。例如，可能在 Web 请求期间获取锁，并希望在该请求触发的队列任务结束时释放锁。在这种情况下，应将锁中限定作用域的「所有者令牌」传给队列任务，使任务能够使用给定令牌重新实例化该锁。

在以下示例中，如果成功获取锁，我们将分发一个队列任务。此外，还会通过锁的 `owner` 方法将锁的所有者令牌传给队列任务：

```php
$podcast = Podcast::find($id);

$lock = Cache::lock('processing', 120);

if ($lock->get()) {
    ProcessPodcast::dispatch($podcast, $lock->owner());
}
```

在应用的 `ProcessPodcast` 任务中，可以使用所有者令牌恢复并释放锁：

```php
Cache::restoreLock('processing', $this->owner)->release();
```

如果要释放锁而不考虑其当前所有者，可以使用 `forceRelease` 方法：

```php
Cache::lock('processing')->forceRelease();
```

<a name="refreshing-locks"></a>
### 刷新锁

如果需要延长当前所拥有锁的过期时间，可以使用 `refresh` 方法。如果未提供秒数，将使用锁原来的持续时间。这对于长时间运行的操作很有用：你可以获取一个短时锁并定期延长，而不必获取一个过期时间很长的锁：

```php
$lock = Cache::lock('generate-reports', 60);

if ($lock->get()) {
    foreach ($reports as $report) {
        $report->generate();

        // 将锁再延长 60 秒...
        $lock->refresh();
    }

    $lock->release();
}
```

<a name="concurrency-limiting"></a>
### 并发限制

Laravel 的原子锁功能还提供了多种限制闭包并发执行的方式。如果只允许整个基础设施中运行一个实例，请使用 `withoutOverlapping`：

```php
Cache::withoutOverlapping('foo', function () {
    // 最多等待 10 秒后获取锁...
});
```

默认情况下，锁会一直保持到闭包执行完毕，并且该方法最多等待 10 秒来获取锁。可以使用其他参数自定义这些值：

```php
Cache::withoutOverlapping('foo', function () {
    // 最多等待 5 秒后获取锁 120 秒...
}, lockFor: 120, waitFor: 5);
```

如果在指定等待时间内无法获取锁，系统将抛出 `Illuminate\Contracts\Cache\LockTimeoutException`。

如果需要可控的并行执行，可以使用 `funnel` 方法设置最大并发执行数。`funnel` 方法适用于所有支持锁的缓存驱动：

```php
Cache::funnel('foo')
    ->limit(3)
    ->releaseAfter(60)
    ->block(10)
    ->then(function () {
        // 已获取并发锁...
    }, function () {
        // 无法获取并发锁...
    });
```

`funnel` 键用于标识受限制的资源。`limit` 方法定义最大并发执行数。`releaseAfter` 方法设置安全超时秒数，超过该时间后，已获取的槽位会自动释放。`block` 方法设置等待可用槽位的秒数。

如果希望通过异常处理超时，而不是提供失败闭包，可以省略第二个闭包。如果在指定等待时间内无法获取锁，系统将抛出 `Illuminate\Cache\Limiters\LimiterTimeoutException`：

```php
use Illuminate\Cache\Limiters\LimiterTimeoutException;

try {
    Cache::funnel('foo')
        ->limit(3)
        ->releaseAfter(60)
        ->block(10)
        ->then(function () {
            // 已获取并发锁...
        });
} catch (LimiterTimeoutException $e) {
    // 无法获取并发锁...
}
```

如果要为并发限制器使用特定的缓存存储，可以在所需存储上调用 `funnel` 方法：

```php
Cache::store('redis')->funnel('foo')
    ->limit(3)
    ->block(10)
    ->then(function () {
        // 使用「redis」存储获取并发锁...
    });
```

> [!NOTE]
> `funnel` 方法要求缓存存储实现 `Illuminate\Contracts\Cache\LockProvider` 接口。如果尝试将 `funnel` 用于不支持锁的缓存存储，系统将抛出 `BadMethodCallException`。

<a name="cache-failover"></a>
## 缓存故障转移

`failover` 缓存驱动在与缓存交互时提供自动故障转移功能。如果 `failover` 存储的主缓存存储因任何原因发生故障，Laravel 会自动尝试使用列表中下一个已配置的存储。这对于确保生产环境的高可用性特别有用，因为缓存可靠性在生产环境中至关重要。

若要配置故障转移缓存存储，请指定 `failover` 驱动，并按尝试顺序提供存储名称数组。默认情况下，Laravel 在应用的 `config/cache.php` 配置文件中包含一个故障转移配置示例：

```php
'failover' => [
    'driver' => 'failover',
    'stores' => [
        'database',
        'array',
    ],
],
```

配置使用 `failover` 驱动的存储后，需要在应用的 `.env` 文件中将故障转移存储设置为默认缓存存储，才能使用故障转移功能：

```ini
CACHE_STORE=failover
```

当缓存存储操作失败并激活故障转移时，Laravel 会分发 `Illuminate\Cache\Events\CacheFailedOver` 事件，让你能够报告或记录缓存存储故障。

<a name="adding-custom-cache-drivers"></a>
## 添加自定义缓存驱动

<a name="writing-the-driver"></a>
### 编写驱动

若要创建自定义缓存驱动，首先需要实现 `Illuminate\Contracts\Cache\Store` [契约](/docs/{{version}}/contracts)。因此，MongoDB 缓存实现可能如下所示：

```php
<?php

namespace App\Extensions;

use Illuminate\Contracts\Cache\Store;

class MongoStore implements Store
{
    public function get($key) {}
    public function many(array $keys) {}
    public function put($key, $value, $seconds) {}
    public function putMany(array $values, $seconds) {}
    public function increment($key, $value = 1) {}
    public function decrement($key, $value = 1) {}
    public function forever($key, $value) {}
    public function forget($key) {}
    public function flush() {}
    public function getPrefix() {}
}
```

只需使用 MongoDB 连接实现这些方法即可。有关如何实现各个方法的示例，请查看 [Laravel 框架源代码](https://github.com/laravel/framework)中的 `Illuminate\Cache\MemcachedStore`。实现完成后，可以调用 `Cache` 门面的 `extend` 方法来完成自定义驱动的注册：

```php
Cache::extend('mongo', function (Application $app) {
    return Cache::repository(new MongoStore);
});
```

> [!NOTE]
> 如果想知道应将自定义缓存驱动代码放在哪里，可以在 `app` 目录中创建 `Extensions` 命名空间。不过，请记住，Laravel 没有僵化的应用结构，你可以根据自己的偏好自由组织应用。

<a name="registering-the-driver"></a>
### 注册驱动

若要向 Laravel 注册自定义缓存驱动，我们将使用 `Cache` 门面的 `extend` 方法。由于其他服务提供者可能会尝试在其 `boot` 方法中读取缓存值，因此我们会在 `booting` 回调中注册自定义驱动。通过使用 `booting` 回调，可以确保在调用应用服务提供者的 `boot` 方法之前、所有服务提供者的 `register` 方法调用之后注册自定义驱动。我们会在应用的 `App\Providers\AppServiceProvider` 类的 `register` 方法中注册 `booting` 回调：

```php
<?php

namespace App\Providers;

use App\Extensions\MongoStore;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册所有应用服务。
     */
    public function register(): void
    {
        $this->app->booting(function () {
             Cache::extend('mongo', function (Application $app) {
                 return Cache::repository(new MongoStore);
             });
         });
    }

    /**
     * 启动所有应用服务。
     */
    public function boot(): void
    {
        // ...
    }
}
```

传给 `extend` 方法的第一个参数是驱动名称，它与 `config/cache.php` 配置文件中的 `driver` 选项对应。第二个参数是一个应返回 `Illuminate\Cache\Repository` 实例的闭包。该闭包会收到 `$app` 实例，即[服务容器](/docs/{{version}}/container)的实例。

注册扩展后，请将 `CACHE_STORE` 环境变量或应用 `config/cache.php` 配置文件中的 `default` 选项更新为扩展名称。

<a name="events"></a>
## 事件

若要在每次缓存操作时执行代码，可以监听缓存分发的各种[事件](/docs/{{version}}/events)：

<div class="overflow-auto">

| 事件名称 |
| --- |
| `Illuminate\Cache\Events\CacheFlushed` |
| `Illuminate\Cache\Events\CacheFlushing` |
| `Illuminate\Cache\Events\CacheFlushFailed` |
| `Illuminate\Cache\Events\CacheLocksFlushed` |
| `Illuminate\Cache\Events\CacheLocksFlushing` |
| `Illuminate\Cache\Events\CacheLocksFlushFailed` |
| `Illuminate\Cache\Events\CacheHit` |
| `Illuminate\Cache\Events\CacheMissed` |
| `Illuminate\Cache\Events\ForgettingKey` |
| `Illuminate\Cache\Events\KeyForgetFailed` |
| `Illuminate\Cache\Events\KeyForgotten` |
| `Illuminate\Cache\Events\KeyWriteFailed` |
| `Illuminate\Cache\Events\KeyWritten` |
| `Illuminate\Cache\Events\RetrievingKey` |
| `Illuminate\Cache\Events\RetrievingManyKeys` |
| `Illuminate\Cache\Events\WritingKey` |
| `Illuminate\Cache\Events\WritingManyKeys` |

</div>

为了提升性能，可以在应用的 `config/cache.php` 配置文件中，将指定缓存存储的 `events` 配置选项设置为 `false`，以禁用缓存事件：

```php
'database' => [
    'driver' => 'database',
    // ...
    'events' => false,
],
```

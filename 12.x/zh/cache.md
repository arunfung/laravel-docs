# 缓存

- [简介](#introduction)
- [配置](#configuration)
  - [驱动器先决条件](#driver-prerequisites)
- [缓存使用](#cache-usage)
  - [获取缓存实例](#obtaining-a-cache-instance)
  - [从缓存中查询项目](#retrieving-items-from-the-cache)
  - [在缓存中存储项目](#storing-items-in-the-cache)
  - [从缓存中移除项目](#removing-items-from-the-cache)
  - [缓存记忆化](#cache-memoization)
  - [缓存辅助函数](#the-cache-helper)
- [原子锁](#atomic-locks)
  - [管理锁](#managing-locks)
  - [跨进程管理锁](#managing-locks-across-processes)
- [添加自定义缓存驱动程序](#adding-custom-cache-drivers)
  - [编写驱动程序](#writing-the-driver)
  - [注册驱动程序](#registering-the-driver)
- [事件](#events)

<a name="introduction"></a>
## 简介

应用程序执行的某些数据查询或处理任务可能会占用大量 CPU 资源，或需要数秒才能完成。在这种情况下，通常会将查询到的数据缓存一段时间，以便在后续对相同数据的请求中快速获取。缓存的数据通常存储在 [Memcached](https://memcached.org) 或 [Redis](https://redis.io) 等速度极快的数据存储中。

值得庆幸的是，Laravel 为各种缓存后端提供了一种富有表现力的统一 API，使你能够利用其极快的数据查询能力来加速 Web 应用程序。

<a name="configuration"></a>
## 配置

应用程序的缓存配置文件位于 `config/cache.php` 。在该文件中，你可以指定应用程序默认使用的缓存存储。Laravel 开箱即用地支持 [Memcached](https://memcached.org) 、 [Redis](https://redis.io) 、[DynamoDB](https://aws.amazon.com/dynamodb) 等流行的缓存后端以及关系型数据库。此外，还提供了基于文件的缓存驱动，而 `array` 和 `null` 缓存驱动则为自动化测试提供了便捷的缓存后端。



缓存配置文件还包含多种其他可供查看的选项。默认情况下，Laravel 被配置为使用 `database` 缓存驱动，该驱动会将序列化的缓存对象存储在应用程序的数据库中。

### 驱动前提条件

#### Database

当使用 `database` 缓存驱动时，你需要一个数据库表来存放缓存数据。通常，这包含在 Laravel 默认的 `0001_01_01_000001_create_cache_table.php` [数据库迁移](/docs/laravel/12.x/migrations) 中；然而，如果你的应用程序没有包含这个迁移，你可以使用 `make:cache-table` Artisan 命令来创建它：

```shell
php artisan make:cache-table

php artisan migrate
```

#### Memcached

使用 Memcached 驱动需要安装 [Memcached PECL 扩展包](https://pecl.php.net/package/memcached)。你可以在 `config/cache.php` 配置文件中列出所有的 Memcached 服务器。该文件已经包含了一个 `memcached.servers` 条目，供你开始使用：

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

如果需要，你可以将 `host` 选项设置为 UNIX 套接字路径。如果这样做，`port` 选项应设置为 `0`：

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

#### Redis

在 Laravel 中使用 Redis 缓存之前，你需要通过 PECL 安装 PhpRedis PHP 扩展，或者通过 Composer 安装 `predis/predis` 包（~2.0）。[Laravel Sail](/docs/laravel/12.x/sail) 已经包含了这个扩展。此外，官方的 Laravel 应用平台，例如 [Laravel Cloud](https://cloud.laravel.com) 和 [Laravel Forge](https://forge.laravel.com)，默认已安装 PhpRedis 扩展。



#### DynamoDB

在使用 [DynamoDB](https://aws.amazon.com/dynamodb) 缓存驱动之前，你必须创建一个 DynamoDB 表来存储所有缓存数据。通常，这个表应该命名为 `cache`。但是，你应根据 `cache` 配置文件中的 `stores.dynamodb.table` 配置值来命名该表。表名也可以通过 `DYNAMODB_CACHE_TABLE` 环境变量来设置。

该表还应具有一个字符串分区键，其名称应与应用程序 `cache` 配置文件中 `stores.dynamodb.attributes.key` 配置项的值相对应。默认情况下，分区键应命名为 `key`。

通常，DynamoDB 不会主动从表中移除已过期的项目。因此，你应该在表上 [启用生存时间 (TTL)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)。在配置表的 TTL 设置时，应将 TTL 属性名称设置为 `expires_at`。

接下来，安装 AWS SDK，以便你的 Laravel 应用程序可以与 DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

此外，你还应确保为 DynamoDB 缓存存储配置项提供值。通常，这些选项（如 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY`）应在应用程序的 `.env` 配置文件中定义：

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



#### MongoDB

如果你使用 MongoDB，可以通过官方的 `mongodb/laravel-mongodb` 包提供的 `mongodb` 缓存驱动来实现，并且它可以通过 `mongodb` 数据库连接进行配置。MongoDB 支持 TTL 索引，可用于自动清理已过期的缓存项。

有关 MongoDB 配置的更多信息，请参阅 MongoDB [缓存与锁文档](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/cache/)。

## 缓存使用

### 获取缓存实例

要获取缓存存储实例，你可以使用 `Cache` facade，我们将在整个文档中使用它。`Cache` facade 提供了简洁、方便的方式来访问 Laravel 缓存契约的底层实现：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Cache;

class UserController extends Controller
{
    /**
     * 显示应用程序的所有用户列表
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

#### 访问多个缓存存储

使用 `Cache` facade，你可以通过 `store` 方法访问不同的缓存存储。传递给 `store` 方法的键应与 `cache` 配置文件中 `stores` 配置数组中的某个存储相对应：

```php
$value = Cache::store('file')->get('foo');

Cache::store('redis')->put('bar', 'baz', 600); // 10 Minutes
```

### 从缓存中检索项目

`Cache` facade 的 `get` 方法用于从缓存中检索项目。如果缓存中不存在该项目，将返回 `null`。如果需要，你可以向 `get` 方法传递第二个参数，指定当项目不存在时希望返回的默认值：

```php
$value = Cache::get('key');

$value = Cache::get('key', 'default');
```



你甚至可以将闭包作为默认值传递。如果指定的项目在缓存中不存在，将返回该闭包的结果。传递闭包可以让你延迟从数据库或其他外部服务中获取默认值：

```php
$value = Cache::get('key', function () {
    return DB::table(/* ... */)->get();
});
```

#### 判断项目是否存在

`has` 方法可用于判断缓存中是否存在某个项目。如果项目存在但其值为 `null`，该方法同样会返回 `false`：

```php
if (Cache::has('key')) {
    // ...
}
```

#### 递增 / 递减值

`increment` 和 `decrement` 方法可用于调整缓存中整数项目的值。这两个方法都可以接收一个可选的第二个参数，用于指定递增或递减的数值：

```php
// 如果不存在则初始化该值...
Cache::add('key', 0, now()->addHours(4));

// 递增或递减该值...
Cache::increment('key');
Cache::increment('key', $amount);
Cache::decrement('key');
Cache::decrement('key', $amount);
```

#### 获取并存储

有时候你可能希望从缓存中获取某个项目，但如果该项目不存在，则存储一个默认值。例如，你可能希望从缓存中获取所有用户，如果不存在，则从数据库中获取并添加到缓存中。你可以使用 `Cache::remember` 方法来实现：

```php
$value = Cache::remember('users', $seconds, function () {
    return DB::table('users')->get();
});
```



如果缓存中不存在该项目，传递给 `remember` 方法的闭包将会被执行，其结果会被存入缓存。

你可以使用 `rememberForever` 方法从缓存中获取项目，如果不存在则永久存储：

```php
$value = Cache::rememberForever('users', function () {
    return DB::table('users')->get();
});
```

#### 过期后重验证 (Stale While Revalidate)

当使用 `Cache::remember` 方法时，如果缓存值已过期，一些用户可能会遇到响应变慢的情况。对于某些类型的数据，允许在后台重新计算缓存值时提供部分过期的数据会很有用，这样可以避免部分用户在缓存值计算过程中遇到延迟。这通常被称为 **“stale-while-revalidate” 模式**，而 `Cache::flexible` 方法提供了该模式的实现。

`flexible` 方法接受一个数组，用于指定缓存值被视为 “新鲜” 的时长以及在变为 “过期” 后还能使用的时长。数组中的第一个值表示缓存被认为是新鲜的秒数，第二个值定义了它可以作为过期数据提供的时长，超过该时长后必须重新计算。

-   如果请求在新鲜期内（第一个值之前），缓存会立即返回，不会重新计算。
-   如果请求在过期期内（介于两个值之间），用户会获得过期值，同时会注册一个 [延迟函数](/docs/laravel/12.x/helpers#deferred-functions)，在响应发送给用户后刷新缓存值。
-   如果请求在第二个值之后到来，缓存被视为已过期，值会立即重新计算，这可能会导致用户的响应较慢。

```php
$value = Cache::flexible('users', [5, 10], function () {
    return DB::table('users')->get();
});
```



#### 获取并删除

如果你需要从缓存中获取某个项目并随后删除它，可以使用 `pull` 方法。与 `get` 方法类似，如果该项目在缓存中不存在，将返回 `null`：

```php
$value = Cache::pull('key');

$value = Cache::pull('key', 'default');
```

### 在缓存中存储项目

你可以在 `Cache` facade 上使用 `put` 方法将项目存入缓存：

```php
Cache::put('key', 'value', $seconds = 10);
```

如果没有向 `put` 方法传递存储时间，该项目将被无限期存储：

```php
Cache::put('key', 'value');
```

除了以整数的形式传递秒数之外，你还可以传递一个 `DateTime` 实例，表示缓存项目所需的过期时间：

```php
Cache::put('key', 'value', now()->addMinutes(10));
```

#### 如果不存在则存储

`add` 方法只会在项目尚不存在于缓存存储时，才将其添加到缓存中。如果项目确实被添加到缓存中，该方法将返回 `true`。否则，该方法将返回 `false`。`add` 方法是一个原子操作：

```php
Cache::add('key', 'value', $seconds);
```

#### 永久存储项目

`forever` 方法可用于将某个项目永久存储在缓存中。由于这些项目不会过期，因此必须通过 `forget` 方法手动将其从缓存中移除：

```php
Cache::forever('key', 'value');
```

> [!注意]
> 如果你使用的是 Memcached 驱动，当缓存达到其大小限制时，存储为 “永久” 的项目可能会被移除。




### 从缓存中移除项目

你可以使用 `forget` 方法从缓存中移除项目：

```php
Cache::forget('key');
```

你也可以通过提供 **0 或负数** 的过期秒数来移除项目：

```php
Cache::put('key', 'value', 0);

Cache::put('key', 'value', -5);
```

你可以使用 `flush` 方法清空整个缓存：

```php
Cache::flush();
```

> [!警告]
> 清空缓存不会遵循你配置的缓存“前缀”，它会移除缓存中的所有条目。在清理由其他应用程序共享的缓存时，请谨慎考虑这一点。

### 缓存记忆化 (Cache Memoization)

Laravel 的 `memo` 缓存驱动允许你在单个请求或任务执行期间，将已解析的缓存值临时存储在内存中。这可以防止在同一次执行中重复访问缓存，从而显著提升性能。

要使用记忆化缓存，可以调用 `memo` 方法：

```php
use Illuminate\Support\Facades\Cache;

$value = Cache::memo()->get('key');
```

`memo` 方法还可以选择接受一个缓存存储的名称，用来指定记忆化驱动所装饰的底层缓存存储：

```php
// 使用默认缓存存储...
$value = Cache::memo()->get('key');

// 使用 Redis 缓存存储...
$value = Cache::memo('redis')->get('key');
```

对同一个键的第一次 `get` 调用会从你的缓存存储中获取值，但同一次请求或任务中的后续调用会直接从内存中获取记忆化的值：

```php
// 访问缓存存储...
$value = Cache::memo()->get('key');

// 不再访问缓存存储，直接返回记忆化值...
$value = Cache::memo()->get('key');
```



当调用会修改缓存值的方法（例如 `put`、`increment`、`remember` 等）时，记忆化缓存会自动忘记已记忆的值，并将修改方法的调用委托给底层缓存存储：

```php
Cache::memo()->put('name', 'Taylor'); // 写入到底层缓存...
Cache::memo()->get('name');           // 访问底层缓存...
Cache::memo()->get('name');           // 已记忆，不再访问缓存...

Cache::memo()->put('name', 'Tim');    // 忘记已记忆的值，写入新值...
Cache::memo()->get('name');           // 再次访问底层缓存...
```

### Cache 助手函数

除了使用 `Cache` facade，你还可以使用全局的 `cache` 函数来通过缓存获取和存储数据。当 `cache` 函数仅被传入一个字符串参数时，它会返回该键对应的值：

```php
$value = cache('key');
```

如果你向函数提供一个键/值对数组以及过期时间，它会将值存储在缓存中并持续指定的时间：

```php
cache(['key' => 'value'], $seconds);

cache(['key' => 'value'], now()->addMinutes(10));
```

当调用 `cache` 函数时不传递任何参数，它会返回一个 `Illuminate\Contracts\Cache\Factory` 实现的实例，从而允许你调用其他缓存方法：

```php
cache()->remember('users', $seconds, function () {
    return DB::table('users')->get();
});
```

> [!注意]
> 在测试对全局 `cache` 函数的调用时，你可以使用 `Cache::shouldReceive` 方法，就像你在 [测试 facade](/docs/laravel/12.x/mocking#mocking-facades) 时一样。

## 原子锁 (Atomic Locks)

> [!警告]
> 要使用此功能，你的应用程序必须将 `memcached`、`redis`、`dynamodb`、`database`、`file` 或 `array` 缓存驱动作为默认缓存驱动。此外，所有服务器必须与同一个中央缓存服务器进行通信。



### 管理锁 (Managing Locks)

原子锁允许操作分布式锁而无需担心竞争条件。例如，[Laravel Cloud](https://cloud.laravel.com) 使用原子锁来确保同一时间在服务器上只执行一个远程任务。你可以使用 `Cache::lock` 方法来创建和管理锁：

```php
use Illuminate\Support\Facades\Cache;

$lock = Cache::lock('foo', 10);

if ($lock->get()) {
     // 已获取 10 秒的锁...

    $lock->release();
}
```

`get` 方法同样可以接收一个闭包。在闭包执行完成后，Laravel 会自动释放该锁：

```php
Cache::lock('foo', 10)->get(function () {
     // 已获取 10 秒的锁，并在执行完成后自动释放...
});
```

如果在请求锁时该锁不可用，你可以指示 Laravel 等待指定的秒数。如果在指定的时间限制内无法获取锁，将抛出 `Illuminate\Contracts\Cache\LockTimeoutException` 异常：

```php
use Illuminate\Contracts\Cache\LockTimeoutException;

$lock = Cache::lock('foo', 10);

try {
    $lock->block(5);

    // 在最多等待 5 秒后获取到锁...
} catch (LockTimeoutException $e) {
    // 无法获取到锁...
} finally {
    $lock->release();
}
```

上面的示例可以通过向 `block` 方法传递一个闭包来简化。当闭包传递给该方法时，Laravel 会尝试在指定的秒数内获取锁，并在闭包执行完成后自动释放锁：

```php
Cache::lock('foo', 10)->block(5, function () {
    // 在最多等待 5 秒后获取到 10 秒的锁，并在执行完成后自动释放...
});
```


### 跨进程管理锁 (Managing Locks Across Processes)

有时，你可能希望在一个进程中获取锁，而在另一个进程中释放锁。
例如：你可能在一个 **Web 请求** 中获取锁，并希望在由该请求触发的 **队列任务** 执行结束时释放锁。

在这种场景下，你需要将锁的作用域 **“所有者令牌 (owner token)”** 传递给队列任务，使得该任务能够使用这个令牌重新实例化锁。

在下面的示例中，如果成功获取到锁，我们会派发一个队列任务。同时，我们会通过锁的 `owner` 方法，将锁的所有者令牌传递给该任务：

```php
$podcast = Podcast::find($id);

$lock = Cache::lock('processing', 120);

if ($lock->get()) {
    ProcessPodcast::dispatch($podcast, $lock->owner());
}
```

在应用的 `ProcessPodcast` 队列任务中，我们可以使用所有者令牌来 **恢复并释放锁**：

```php
Cache::restoreLock('processing', $this->owner)->release();
```

如果你希望释放锁而 **忽略当前所有者**，可以使用 `forceRelease` 方法：

```php
Cache::lock('processing')->forceRelease();
```

## 添加自定义缓存驱动 (Adding Custom Cache Drivers)

### 编写驱动 (Writing the Driver)

要创建自定义的缓存驱动，我们首先需要实现 `Illuminate\Contracts\Cache\Store` [契约](/docs/laravel/12.x/contracts)。

例如，一个 MongoDB 缓存实现可能看起来像这样：

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



我们只需要使用 MongoDB 连接实现这些方法即可。
如果你想看每个方法的具体实现方式，可以参考 Laravel 框架源码中的 `Illuminate\Cache\MemcachedStore`：[GitHub 链接](https://github.com/laravel/framework)。
在自定义实现完成后，我们可以通过调用 `Cache` facade 的 `extend` 方法来完成自定义驱动的注册：

```php
Cache::extend('mongo', function (Application $app) {
    return Cache::repository(new MongoStore);
});
```

> [!注意]
> 如果你在想自定义缓存驱动的代码放在哪里，可以在 `app` 目录下创建一个 `Extensions` 命名空间。不过需要注意，Laravel 没有严格的应用程序结构，你可以根据自己的喜好组织应用程序。

### 注册驱动 (Registering the Driver)

要在 Laravel 中注册自定义缓存驱动，我们使用 `Cache` facade 的 `extend` 方法。
由于其他服务提供者可能会在其 `boot` 方法中尝试读取缓存值，我们将在 `booting` 回调中注册自定义驱动。
通过使用 `booting` 回调，可以确保自定义驱动在应用服务提供者的 `boot` 方法调用之前注册，并且在所有服务提供者的 `register` 方法调用之后完成注册。

我们将在应用程序的 `App\Providers\AppServiceProvider` 类中的 `register` 方法中注册这个 `booting` 回调：

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
     * 注册任何应用服务
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
     * 启动任何应用服务
     */
    public function boot(): void
    {
        // ...
    }
}

```



`extend` 方法的第一个参数是驱动名称，这将对应于你在 `config/cache.php` 配置文件中的 `driver` 选项。
第二个参数是一个闭包，该闭包应返回一个 `Illuminate\Cache\Repository` 实例。闭包会接收一个 `$app` 实例，它是 [服务容器](/docs/laravel/12.x/container) 的实例。

一旦自定义扩展注册完成，更新应用程序的 `CACHE_STORE` 环境变量，或者在 `config/cache.php` 配置文件中将 `default` 选项设置为你的扩展名称即可使用自定义驱动。

## 事件 (Events)

要在每次缓存操作时执行代码，你可以监听缓存触发的各种 [事件](/docs/laravel/12.x/events)：

<div class="overflow-auto">

| Event Name                                   |
|----------------------------------------------|
| `Illuminate\Cache\Events\CacheFlushed`       |
| `Illuminate\Cache\Events\CacheFlushing`      |
| `Illuminate\Cache\Events\CacheHit`           |
| `Illuminate\Cache\Events\CacheMissed`        |
| `Illuminate\Cache\Events\ForgettingKey`      |
| `Illuminate\Cache\Events\KeyForgetFailed`    |
| `Illuminate\Cache\Events\KeyForgotten`       |
| `Illuminate\Cache\Events\KeyWriteFailed`     |
| `Illuminate\Cache\Events\KeyWritten`         |
| `Illuminate\Cache\Events\RetrievingKey`      |
| `Illuminate\Cache\Events\RetrievingManyKeys` |
| `Illuminate\Cache\Events\WritingKey`         |
| `Illuminate\Cache\Events\WritingManyKeys`    |

</div>

为了提升性能，你可以通过在应用程序的 `config/cache.php` 配置文件中，将某个缓存存储的 `events` 配置项设置为 `false` 来禁用缓存事件：

```php
'database' => [
    'driver' => 'database',
    // ...
    'events' => false,
],
```

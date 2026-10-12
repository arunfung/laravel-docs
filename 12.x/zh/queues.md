
# 队列 (Queues)

- [介绍](#introduction)
    - [连接与队列](#connections-vs-queues)
    - [驱动程序说明与前置条件](#driver-prerequisites)
- [创建任务](#creating-jobs)
    - [生成任务类](#generating-job-classes)
    - [任务类结构](#class-structure)
    - [唯一任务](#unique-jobs)
    - [加密任务](#encrypted-jobs)
- [任务中间件](#job-middleware)
    - [限流](#rate-limiting)
    - [防止任务重复执行](#preventing-job-overlaps)
    - [异常节流](#throttling-exceptions)
    - [跳过任务](#skipping-jobs)
- [调度任务](#dispatching-jobs)
    - [延迟调度](#delayed-dispatching)
    - [同步调度](#synchronous-dispatching)
    - [任务 & 数据库事务](#jobs-and-database-transactions)
    - [任务链](#job-chaining)
    - [自定义队列 & 连接](#customizing-the-queue-and-connection)
    - [指定最大任务尝试次数 / 超时值](#max-job-attempts-and-timeout)
    - [错误处理](#error-handling)
- [任务批处理 ](#job-batching)
    - [定义可批处理任务](#defining-batchable-jobs)
    - [分派批处理](#dispatching-batches)
    - [链和批处理](#chains-and-batches)
    - [将任务添加到批处理](#adding-jobs-to-batches)
    - [校验批处理](#inspecting-batches)
    - [取消批处理](#cancelling-batches)
    - [批处理失败](#batch-failures)
    - [修剪批处理](#pruning-batches)
    - [在 DynamoDB 中存储批处理](#storing-batches-in-dynamodb)
- [队列闭包](#queueing-closures)
- [运行队列处理器](#running-the-queue-worker)
    - [ `queue:work` 命令](#the-queue-work-command)
    - [队列优先级](#queue-priorities)
    - [队列处理器 & 部署](#queue-workers-and-deployment)
    - [任务过期 & 超时](#job-expirations-and-timeouts)
- [Supervisor 配置](#supervisor-configuration)
- [处理失败的任务](#dealing-with-failed-jobs)
    - [任务失败后清理](#cleaning-up-after-failed-jobs)
    - [重试失败的任务](#retrying-failed-jobs)
    - [忽略缺失的模型](#ignoring-missing-models)
    - [删除失败的任务](#pruning-failed-jobs)
    - [在 DynamoDB 中存储失败的任务](#storing-failed-jobs-in-dynamodb)
    - [禁用失败的任务存储](#disabling-failed-job-storage)
    - [失败的任务事件](#failed-job-events)
- [从队列中清除任务](#clearing-jobs-from-queues)
- [监控你的队列](#monitoring-your-queues)
- [测试](#testing)
    - [伪造任务的一个子集](#faking-a-subset-of-jobs)
    - [测试任务链](#testing-job-chains)
    - [测试任务批处理](#testing-job-batches)
    - [测试任务 / 队列互动](#testing-job-queue-interactions)
- [任务事件](#job-events)



<a name="introduction"></a>
## 简介

在构建 Web 应用程序时，你可能需要执行一些任务，例如解析和存储上传的 CSV 文件，这些任务在典型的 Web 请求期间需要很长时间才能执行。 值得庆幸的是，Laravel 允许你轻松创建可以在后台处理的队列任务。 通过将时间密集型任务移至队列，你的应用程序可以以极快的速度响应 Web 请求，并为你的客户提供更好的用户体验。

Laravel 队列为各种不同的队列驱动提供统一的队列 API，例如 [Amazon SQS](https://aws.amazon.com/sqs/), [Redis](https://redis.io/)，甚至是关系型数据库。

Laravel 队列的配置选项存储在 `config/queue.php` 文件中。 在这个文件中，你可以找到框架中包含的每个队列驱动的连接配置，包括数据库， [Amazon SQS](https://aws.amazon.com/sqs/), [Redis](https://redis.io/), 和 [Beanstalkd](https://beanstalkd.github.io/) 驱动，以及一个会立即执行任务的同步驱动（用于本地开发）。还包括一个用于丢弃排队任务的 `null` 队列驱动。

> [!注意]
> Laravel 提供了 Horizon ，一个关于 Redis 队列的漂亮仪表盘后台和配置系统。如需了解更多信息请查看完整的 [Horizon 文档](https://learnku.com/docs/laravel/12.x/horizon)。

<a name="connections-vs-queues"></a>
### 连接 vs 驱动

在开始使用 Laravel 队列之前，理解「连接」和「队列」之间的区别非常重要。 在 `config/queue.php` 配置文件中，有一个 `connections` 连接选项。这个选项可以定义连接到哪个后台队列系统，例如: Amazon SQS 、 Beanstalk 、 或者 Redis 。然而，任何给定的队列连接都可能有多个「队列」，这些「队列」可能被认为是不同的堆栈或成堆的排队任务。

请注意， `queue` 配置文件中的每个连接配置示例都包含一个 `queue` 属性。这是将任务发送到给定连接时将被分配到的默认队列。换句话说，如果你没有显式地指定任务队列，那么该任务将被放置在连接配置的 `queue` 属性中定义的队列上：

```php
use App\Jobs\ProcessPodcast;

// 这个任务将被推送到默认队列...
ProcessPodcast::dispatch();

// 这个任务将被推送到「emails」队列...
ProcessPodcast::dispatch()->onQueue('emails');
```

有些应用可能不需要将任务推到多个队列中，而是倾向于使用一个简单的队列。然而，如果希望对任务的处理方式进行优先级排序或分段时，将任务推送到多个队列就显得特别有用，因为 Laravel 队列工作程序允许你指定哪些队列应该按优先级处理。例如，如果你将任务推送到一个 `high` 队列，你可能会运行一个赋予它们更高处理优先级的 worker：

```shell
php artisan queue:work --queue=high,default
```

<a name="driver-prerequisites"></a>
### 驱动程序说明和先决条件

<a name="database"></a>
#### 数据库

要使用 `database` 队列驱动，你需要一个数据库表来保存任务。通常，这包含在 Laravel 默认的 `0001_01_01_000002_create_jobs_table.php` [数据库迁移](https://learnku.com/docs/laravel/12.x/migrations) 中； 然而，如果你的应用程序不包含此迁移，可以使用 `make:queue-table` Artisan 命令创建它：

```shell
php artisan make:queue-table

php artisan migrate
```



<a name="redis"></a>
#### Redis

要使用 `redis` 队列驱动程序，需要在 `config/database.php` 配置文件中配置一个 redis 数据库连接。

> [!注意]
> `serializer` 和 `compression` 选项不被 `redis` 队列驱动支持。

**Redis 集群**

如果你的 Redis 队列当中使用了 Redis 集群，那么你的队列名称就必须包含一个 [key hash tag](https://redis.io/docs/reference/cluster-spec/#hash-tags)。这是为了确保一个给定队列的所有 Redis 键都被放在同一个哈希槽中：

```php
'redis' => [
    'driver' => 'redis',
    'connection' => env('REDIS_QUEUE_CONNECTION', 'default'),
    'queue' => env('REDIS_QUEUE', '{default}'),
    'retry_after' => env('REDIS_QUEUE_RETRY_AFTER', 90),
    'block_for' => null,
    'after_commit' => false,
],
```

**阻塞**

当使用 Redis 队列时，您可以使用 `block_for` 配置选项来指定在遍历 worker 循环和重新轮询 Redis 数据库之前，驱动程序需要等待多长时间才能使任务变得可用。

根据你的队列负载调整此值要比连续轮询 Redis 数据库中的新任务更加有效。例如，你可以将值设置为 `5` 以指示驱动程序在等待任务变得可用时应该阻塞 5 秒：

```php
'redis' => [
    'driver' => 'redis',
    'connection' => env('REDIS_QUEUE_CONNECTION', 'default'),
    'queue' => env('REDIS_QUEUE', 'default'),
    'retry_after' => env('REDIS_QUEUE_RETRY_AFTER', 90),
    'block_for' => 5,
    'after_commit' => false,
],
```

> [!注意]
> 将 `block_for` 设置成 `0` 将导致队列任务一直阻塞，直到某一个任务变得可用。这也将防止在下一个任务被处理之前处理诸如 `SIGTERM` 之类的信号。

<a name="other-driver-prerequisites"></a>
#### 其他驱动所需的先决条件

其它队列驱动需要下面的依赖。这些依赖可以通过 Composer 包管理器安装：

<div class="content-list" markdown="1">

- Amazon SQS: `aws/aws-sdk-php ~3.0`
- Beanstalkd: `pda/pheanstalk ~5.0`
- Redis: `predis/predis ~2.0` or phpredis PHP 扩展
- [MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/queues/): `mongodb/laravel-mongodb`

</div>

<a name="creating-jobs"></a>
## 创建任务

<a name="generating-job-classes"></a>
### 生成任务类

默认情况下，应用程序的所有的可排队任务都被存储在了 `app/Jobs` 目录中。如果 `app/Jobs` 目录不存在，当你运行 `make:job` Artisan 命令时，将会自动创建该目录：

```shell
php artisan make:job ProcessPodcast
```

生成的类将会实现 `Illuminate\Contracts\Queue\ShouldQueue` 接口， 告诉 Laravel ，该任务应该推入队列以异步的方式运行。

> [!注意]
> 任务 stubs 可以使用 [stub publishing](/docs/laravel/12.x/artisan#stub-customization) 定制。

<a name="class-structure"></a>
### 任务类结构

任务类非常简单，通常只包含一个 `handle` 方法，在队列处理任务时将会调用它。让我们看一个任务类的示例。在这个例子中，我们假设我们管理一个 podcast 服务，并且需要在上传的 podcast 文件发布之前对其进行处理：

```php
<?php

namespace App\Jobs;

use App\Models\Podcast;
use App\Services\AudioProcessor;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     *  创建一个任务实例
     */
    public function __construct(
        public Podcast $podcast,
    ) {}

    /**
     * 执行任务
     */
    public function handle(AudioProcessor $processor): void
    {
        // 处理上传的 podcast...
    }
}
```



在这个示例中，需要注意的是我们可以直接将一个 [Eloquent 模型](/docs/laravel/12.x/eloquent) 传入到队列任务的构造函数中。 由于任务中使用`Queueable` trait，Eloquent 模型及其已加载的关联关系会在任务处理时被优雅地序列化与反序列化。  
如果你的队列任务在构造函数中接收一个 Eloquent 模型，那么在写入队列时，只有模型的标识符会被序列化。  当任务被执行时，队列系统会自动从数据库中重新获取完整的模型实例和已加载的关联关系。  
这种模型序列化的方式，可以让发送到队列驱动的任务负载体积更小，更高效。

<a name="handle-method-dependency-injection"></a>
#### `handle` 依赖注入

当队列开始处理任务时，就会调用 `handle` 方法。你也可以在任务的 `handle` 方法参数中使用「类型提示」来声明依赖。Laravel 的 [服务容器](/docs/laravel/12.x/container) 会自动注入这些依赖。

如果你想完全掌控服务容器是如何将依赖注入到 `handle` 方法中，可以使用容`bindMethod`方法。 `bindMethod` 方法接收一个回调函数，这个回调会获得任务实例和容器实例。你可以在回调中根据自己的需要来调用 `handle` 方法。
通常，需要在 `App\Providers\AppServiceProvider` 的 `boot` 方法中调用这个方法，该类是应用程序的 [服务提供者](/docs/laravel/12.x/providers)：

```php
use App\Jobs\ProcessPodcast;
use App\Services\AudioProcessor;
use Illuminate\Contracts\Foundation\Application;

$this->app->bindMethod([ProcessPodcast::class, 'handle'], function (ProcessPodcast $job, Application $app) {
    return $job->handle($app->make(AudioProcessor::class));
});
```

> [警告]
> 二进制数据（例如原始图片内容）在传递到队列任务之前，应该先使用 `base64_encode` 函数进行编码。  否则，当任务被放入队列时，可能无法正确序列化为 JSON。



<a name="handling-relationships"></a>
#### 队列中的关联关系

由于所有已加载的 Eloquent 模型关联关系在队列入队时也会被一并序列化，因此序列化后的队列字符串有时可能会非常庞大。  
此外，当队列被反序列化并重新从数据库中获取模型关联关系时，这些关系会「完整地」被取回。  需要注意，队列在入队前对模型应用的任何关联约束条件，在队列反序列化后都不会再次生效。  因此，如果你只想处理某个关联关系的部分数据，需要在队列任务中重新对该关系进行约束。  

另外，如果你想避免模型的关联关系被序列化，可以在设置属性值时调用模型的 `withoutRelations` 方法。  此方法会返回一个不包含已加载关联关系的模型实例：

```php
/**
 * 创建一个新的队列实例.
 */
public function __construct(
    Podcast $podcast,
) {
    $this->podcast = $podcast->withoutRelations();
}
```

如果你在使用 PHP 的构造函数，并且希望某个 Eloquent 模型在序列化时不包含关联关系，可以使用 `WithoutRelations`  属性：

```php
use Illuminate\Queue\Attributes\WithoutRelations;

/**
 * 创建一个新的队列实例.
 */
public function __construct(
    #[WithoutRelations]
    public Podcast $podcast,
) {}
```

如果一个队列接收的是一组 Eloquent 模型集合或数组，而不是单个模型，那么在队列被反序列化并执行时，这些模型的关联关系将不会被恢复。这样是为了避免在处理大量模型的队列中消耗过多资源。

<a name="unique-jobs"></a>
### 唯一队列

> [!警告]
> 唯一队列需要一个支持 [锁](/docs/laravel/12.x/cache#atomic-locks) 的缓存驱动。目前，`memcached`、`redis`、`dynamodb`、`database`、`file` 和 `array` 缓存驱动都支持原子锁。 并且，唯一队列约束不适用于批量队列。



有时候，你可能希望在任意时刻，队列中只保留某个特定任务的一个实例。要实现这一点，只需要在队列类上「实现」 `ShouldBeUnique` 接口即可。  
而且，这个接口并不要求你在类中额外定义任何方法:

```php
<?php

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUnique;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...
}
```

在上面的示例中，`UpdateSearchIndex` 队列是「唯一的」。  因此，如果该队列的另一个实例已经在队列中且尚未处理完成，那么它将不会再次被调度。  

在某些情况下，你可能希望通过一个特定的「键」来让队列保持唯一，或者希望指定一个超时时间，超过该时间后队列就不再保持唯一。  
要实现这一点，你可以在队列类中定义 `uniqueId` 和 `uniqueFor` 属性或方法：

```php
<?php

use App\Models\Product;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUnique;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    /**
     * 产品实例.
     *
     * @var \App\Product
     */
    public $product;

    /**
     * 队列的唯一锁将在 N 秒后被释放.
     *
     * @var int
     */
    public $uniqueFor = 3600;

    /**
     * 获取该队列的唯一 ID.
     */
    public function uniqueId(): string
    {
        return $this->product->id;
    }
}
```

在上面示例中，`UpdateSearchIndex` 队列是通过产品 ID 来保持唯一的。因此，任何带有相同产品 ID 的新队列在现有队列处理完成之前，都将会被忽略。  
但是，如果现有队列在一小时内仍未被处理完毕，那么唯一锁将会被释放，此时带有相同唯一键的另一个队列就可以被调度到队列中。

> [!警告]
> 如果你的应用会从多个 Web 服务器或容器中调度队列, 你需要确保所有服务都连接到同一个中央缓存服务器，这样 Laravel 才能准确判断某个队列是否唯一。



<a name="keeping-jobs-unique-until-processing-begins"></a>
#### 保持队列唯一 直到开始处理

默认情况下，唯一队列会在队列处理完成或所有重试都失败后才「解锁」。  但是有些情况下，你如果希望队列在开始处理之前就立即解锁。  
想要实现这一点，你的队列类应实现 `ShouldBeUniqueUntilProcessing` 接口，而不是 `ShouldBeUnique` 接口：

```php
<?php

use App\Models\Product;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUniqueUntilProcessing;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    // ...
}
```

<a name="unique-job-locks"></a>
#### 唯一队列锁

在后台，当一个实现了 `ShouldBeUnique` 接口的队列被调度时，Laravel 会尝试使用 `uniqueId` 作为键去获取一个 [锁](/docs/laravel/12.x/cache#atomic-locks)。  如果锁未能获取到，该队列将不会被调度。  
该锁会在队列处理完成或所有重试尝试都失败后被释放。  默认情况下，Laravel 会使用默认缓存驱动来获取这个锁。  
如果你希望使用其他缓存驱动来获取锁，可以在队列类中定义一个 `uniqueVia` 方法，该方法返回要使用的缓存驱动。

```php
use Illuminate\Contracts\Cache\Repository;
use Illuminate\Support\Facades\Cache;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...

    /**
     * 获取唯一队列锁所使用的缓存驱动.
     */
    public function uniqueVia(): Repository
    {
        return Cache::driver('redis');
    }
}
```

> [!注意]  
> 如果你只需要限制队列的并发处理，可以改用 [WithoutOverlapping](/docs/laravel/12.x/queues#preventing-job-overlaps) 队列中间件。

<a name="encrypted-jobs"></a>
### 队列加密

Laravel 允许你通过 [加密](/docs/laravel/12.x/encryption) 来保证队列数据的隐私性和完整性。  
要开始使用，只需在队列类中实现 `ShouldBeEncrypted` 接口。 一旦队列类中实现了该接口，Laravel 会在将队列推送到队列前自动对其进行加密：

```php
<?php

use Illuminate\Contracts\Queue\ShouldBeEncrypted;
use Illuminate\Contracts\Queue\ShouldQueue;

class UpdateSearchIndex implements ShouldQueue, ShouldBeEncrypted
{
    // ...
}
```



<a name="job-middleware"></a>
## 任务中间件

队列中间件允许在队列执行过程中包裹自定义逻辑，从而减少队列本身的代码。  
例如，下面的 `handle` 方法利用了 Laravel 的 Redis 限流功能，使得每五秒仅允许一个队列被处理：

```php
use Illuminate\Support\Facades\Redis;

/**
 * 执行当前队列.
 */
public function handle(): void
{
    Redis::throttle('key')->block(0)->allow(1)->every(5)->then(function () {
        info('Lock obtained...');

        // 处理当前队列...
    }, function () {
        // 无法获取到锁...

        return $this->release(5);
    });
}
```

这段代码虽然有效，但 `handle` 方法的实现非常杂乱，因为它被 Redis 限流逻辑充斥。  如果我们希望对其他队列也进行限流，这段限流逻辑就必须重复实现。  

所以与其在 `handle` 方法中进行限流，不如定义一个专门处理限流的队列中间件。  
Laravel 并没有为队列中间件规定默认存放位置，你可以在应用中的任意位置放置队列中间件。  
在这个示例中，我们会将中间件放在 `app/Jobs/Middleware` 目录下：

```php
<?php

namespace App\Jobs\Middleware;

use Closure;
use Illuminate\Support\Facades\Redis;

class RateLimited
{
    /**
     * 处理当前队列任务.
     *
     * @param  \Closure(object): void  $next
     */
    public function handle(object $job, Closure $next): void
    {
        Redis::throttle('key')
            ->block(0)->allow(1)->every(5)
            ->then(function () use ($job, $next) {
                // 锁已获取...

                $next($job);
            }, function () use ($job) {
                // 无法获取到锁...

                $job->release(5);
            });
    }
}
```

如你所见，和 [路由中间件](/docs/laravel/12.x/middleware) 类似，队列中间件会接收当前正在处理的队列任务以及一个回调函数，该回调函数会被调用以继续处理队列任务。



创建队列中间件后，你可以在队列类的 `middleware` 方法中返回这些中间件，从而将它们应用到该队列上。   但是通过 `make:job` Artisan 命令生成的队列类默认**没有**该方法，因此你需要手动在队列类中添加 `middleware` 方法：

```php
use App\Jobs\Middleware\RateLimited;

/**
 * 获取队列需要通过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited];
}
```

> [!注意]
> 队列中间件同样可以应用于队列的事件监听器、邮件类和通知。

<a name="rate-limiting"></a>
### 限流

以上示例展示了如何编写自定义限流队列中间件，但 Laravel 实际上已经包含了可用于队列限流的中间件。  和 [路由限流器](/docs/laravel/12.x/routing#defining-rate-limiters) 类似，队列限流器通过 `RateLimiter` facade 的 `for` 方法进行定义。  

例如，如果你希望普通用户每小时只能备份一次数据，而对高级客户不做此限制。  要实现这一点，可以在 `AppServiceProvider` 的 `boot` 方法中定义一个 `RateLimiter`：

```php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Support\Facades\RateLimiter;

/**
 * 引导应用中的所有服务.
 */
public function boot(): void
{
    RateLimiter::for('backups', function (object $job) {
        return $job->user->vipCustomer()
            ? Limit::none()
            : Limit::perHour(1)->by($job->user->id);
    });
}
```

在以上示例中，我们定义了每小时限流。  当然你也可以使用 `perMinute` 方法轻松定义基于分钟的限流，你可以将任意值传递给限流的 `by` 方法，这个值最常用于按客户划分限流：

```php
return Limit::perMinute(50)->by($job->user->id);
```



定义好限流规则后，可以通过 `Illuminate\Queue\Middleware\RateLimited` 中间件，将该限流器应用到队列上。
每当队列任务超出限流阈值时，这个中间件就会根据限流时长计算合适的延迟，并将该任务重新释放回队列中。

```php
use Illuminate\Queue\Middleware\RateLimited;

/**
 * 获取队列在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited('backups')];
}
```

将超出限流的任务重新释放回队列时，该任务的 `attempts` 总次数仍会增加。  你可能需要根据实际情况调整队列类中的 `tries` 和 `maxExceptions` 属性。  或者也可以使用 [retryUntil 方法](#time-based-attempts) 来定义队列任务不再尝试的截止时间。  

此外，使用 `releaseAfter` 方法，你还可以指定在重新释放队列后，必须经过多少秒才能再次尝试执行：

```php
/**
 * 获取队列在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->releaseAfter(60)];
}
```

如果你不希望队列任务在被限流时被重试，可以使用 `dontRelease` 方法：

```php
/**
 * 获取队列在执行前需要经过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->dontRelease()];
}
```

> [!注意]
> 如果你使用 Redis，可以使用 `Illuminate\Queue\Middleware\RateLimitedWithRedis` 中间件。
> 该中间件针对 Redis 做了优化，比基础限流中间件更高效。




<a name="preventing-job-overlaps"></a>
### 防止任务重复执行

Laravel 提供了一个 `Illuminate\Queue\Middleware\WithoutOverlapping` 中间件，可以通过任意键防止任务重复执行。  当队列任务需要修改某个资源，而该资源一次只应被一个任务修改时，这个中间件就很有作用。

例如，假设你有一个队列任务用于更新用户的信用分数，你不希望同一用户 ID 更新信用分任务时发生重复执行。  对此你可以在队列任务的 `middleware` 方法中返回 `WithoutOverlapping` 中间件：

```php
use Illuminate\Queue\Middleware\WithoutOverlapping;

/**
 * 获取队列在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new WithoutOverlapping($this->user->id)];
}
```

同类型的任何重复执行队列任务都会被重新释放回队列。  你还可以指定在重新释放队列后，必须经过多少秒才能再次执行：

```php
/**
 * 获取队列在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->releaseAfter(60)];
}
```

如果你希望立即删除所有重复执行的队列任务，使其不再被重试，可以使用 `dontRelease` 方法：

```php
/**
 * 获取队列任务在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->dontRelease()];
}
```

`WithoutOverlapping` 中间件依赖于 Laravel 的原子锁功能。  当队列任务意外失败或超时，导致锁未被释放。 这时你可以使用 `expireAfter` 方法显式地定义锁的过期时间。  
如下所示，Laravel 会在队列任务开始处理后三分钟释放 `WithoutOverlapping` 锁：

```php
/**
 * 获取队列任务在执行前需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->expireAfter(180)];
}
```

> [!警告]
> `WithoutOverlapping` 中间件需要使用支持 [锁](/docs/laravel/12.x/cache#atomic-locks) 的缓存驱动。 目前  `memcached`、`redis`、`dynamodb`、`database`、`file` 和 `array` 缓存驱动均支持原子锁。




<a name="sharing-lock-keys"></a>
#### 队列类共享锁键

默认情况下，`WithoutOverlapping` 中间件仅会防止同一队列类的任务重叠。  因此即使两个不同的队列类使用相同的锁键，它们仍可能发生重叠。  
为此可以使用 `shared` 方法让 Laravel 在多个队列类间共享该锁键：

```php
use Illuminate\Queue\Middleware\WithoutOverlapping;

class ProviderIsDown
{
    // ...

    public function middleware(): array
    {
        return [
            (new WithoutOverlapping("status:{$this->provider}"))->shared(),
        ];
    }
}

class ProviderIsUp
{
    // ...

    public function middleware(): array
    {
        return [
            (new WithoutOverlapping("status:{$this->provider}"))->shared(),
        ];
    }
}
```

<a name="throttling-exceptions"></a>
### 异常限流

Laravel 提供了一个 `Illuminate\Queue\Middleware\ThrottlesExceptions` 中间件，用于限流异常。  当队列抛出指定次数的异常后，所有后续的执行尝试都会被延迟，直到指定的时间间隔结束。  该中间件对不稳定的第三方服务交互的队列任务非常友好。

假设有一个队列任务需要调用第三方 API，而该 API 开始抛出异常。  为了对异常进行限流，你可以在队列任务的 `middleware` 方法中返回 `ThrottlesExceptions` 中间件。
该中间件要和实现了 [基于时间的尝试](#time-based-attempts) 的队列任务配合使用：


```php
use DateTime;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取队列需要经过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new ThrottlesExceptions(10, 5 * 60)];
}

/**
 * 获取队列的超时时间。
 */
public function retryUntil(): DateTime
{
    return now()->addMinutes(30);
}
```

中间件接受的第一个构造函数参数是队列在被限流之前允许抛出的异常次数， 第二个参数是队列任务在被限流后再次尝试执行前必须经过的秒数。
在上面的代码示例中，如果队列任务连续抛出 10 次异常，我们将在 5 分钟后再次尝试执行该任务，并且限制时间 30 分钟。




当任务抛出异常但尚未达到异常阈值时，通常会立即重试该任务。但是，你可以通过在将中间件附加到任务时调用 `backoff` 方法来指定此类任务应延迟的分钟数：

```php
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 5 * 60))->backoff(5)];
}
```

在内部，这个中间件使用 Laravel 的缓存系统来实现速率限制，并利用任务的类名作为缓存 「键」。 在将中间件附加到任务时，你可以通过调用 `by` 法来覆盖此键。 如果你有多个任务与同一个第三方服务交互并且你希望它们共享一个共同的节流 「桶」，这可能会很有用：

```php
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->by('key')];
}
```

默认情况下，这个中间件将限制每个异常。你可以通过在附加中间件到任务时调用 `when` 方法来修改这种行为。只有当提供给 `when` 方法的闭包返回 `true` 时，异常才会被节流：

```php
use Illuminate\Http\Client\HttpClientException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->when(
        fn (Throwable $throwable) => $throwable instanceof HttpClientException
    )];
}
```

与 `when` 方法不同（该方法会将任务放回队列或抛出异常）， `deleteWhen` 方法允许你在指定异常发生时，将任务完全删除：

```php
use App\Exceptions\CustomerDeletedException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * Get the middleware the job should pass through.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(2, 10 * 60))->deleteWhen(CustomerDeletedException::class)];
}
```



如果你希望将被节流的异常报告给应用程序的异常处理程序，可以在将中间件附加到任务时调用 `report` 方法来实现。
也可以为 `report` 方法提供一个闭包，并且只有当该闭包返回 `true` 时，异常才会被报告：

```php
use Illuminate\Http\Client\HttpClientException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务时，应该通过的中间件.
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->report(
        fn (Throwable $throwable) => $throwable instanceof HttpClientException
    )];
}
```

> [技巧]
> 如果你使用的是 Redis，可以使用 `Illuminate\Queue\Middleware\ThrottlesExceptionsWithRedis` 中间件。  该中间件针对 Redis 进行了优化，比基础的异常节流中间件更高效。


<a name="skipping-jobs"></a>
### 跳过任务

`Skip` 中间件允许你在不修改任务逻辑的情况下，指定某个任务跳过或删除。
`Skip::when` 方法会在给定条件为 `true` 时删除任务，而 `Skip::unless` 方法会在条件为 `false` 时删除任务：

```php
use Illuminate\Queue\Middleware\Skip;

/**
 * 获取任务应通过的中间件.
 */
public function middleware(): array
{
    return [
        Skip::when($someCondition),
    ];
}
```

你还可以向 `when` 和 `unless` 方法传递一个 `Closure`，用于更复杂的条件判断：

```php
use Illuminate\Queue\Middleware\Skip;

class ProcessPodcast implements ShouldQueue
{
    public function middleware(): array
    {
        return [
            Skip::unless(function () {
                return $this->user->subscriptionActive() && 
                       $this->podcast->isPublished();
            }),
        ];
    }

    public function handle(): void
    {
        // 任务逻辑
    }
}


```php
use Illuminate\Queue\Middleware\Skip;

/**
 * 获取任务要通过的中间件.
 */
public function middleware(): array
{
    return [
        Skip::when(function (): bool {
            return $this->shouldSkip();
        }),
    ];
}
```

<a name="dispatching-jobs"></a>
## 调度任务

一旦你写好了队列类，你可以使用任务本身的 `dispatch` 方法来调度它。  
传递给 `dispatch` 方法的参数将会传入队列类的构造函数：

```php
<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PodcastController extends Controller
{
    /**
     * 存储一个新的播客.
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // ...

        ProcessPodcast::dispatch($podcast);

        return redirect('/podcasts');
    }
}
```



如果你想有条件地分派任务，你可以使用 `dispatchIf` 和 `dispatchUnless` 方法：

```php
ProcessPodcast::dispatchIf($accountActive, $podcast);

ProcessPodcast::dispatchUnless($accountSuspended, $podcast);
```

在新的 Laravel 应用程序中，默认的队列驱动是 `sync` 驱动。这个驱动在当前请求的前台同步执行任务，通常在本地开发中很方便。如果你想在后台处理队列任务，你可以在应用程序的 `config/queue.php` 配置文件中指定不同的队列驱动。

<a name="delayed-dispatching"></a>
### 延迟调度

如果你想指定一个任务不应该立即可供队列工作器处理，当调度任务时，你可以使用 `delay` 方法。例如，让我们指定一个任务应该在调度后 10 分钟才能被处理：

```php
<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PodcastController extends Controller
{
    /**
     * 储存一个新的播客.
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // ...

        ProcessPodcast::dispatch($podcast)
            ->delay(now()->addMinutes(10));

        return redirect('/podcasts');
    }
}
```

在某些情况下，队列可能配置了默认延迟。 如果你需要跳过这个延迟并立即调度任务，可以使用 `withoutDelay` 方法：

```php
ProcessPodcast::dispatch($podcast)->withoutDelay();
```

> [!注意]
>Amazon SQS 队列服务的最大延迟时间为 15 分钟。

<a name="dispatching-after-the-response-is-sent-to-browser"></a>
#### 响应发送到浏览器后调度



另外，如果你的 web 服务器使用 FastCGI，`dispatchAfterResponse` 方法延迟调度作业，直到 HTTP 响应发送到用户浏览器之后。这将仍然允许用户开始使用应用程序，即使一个排队的任务仍然在执行。这通常只应该用于执行时间大约一秒钟的任务，例如发送电子邮件。由于它们是在当前 HTTP 请求中处理的，以这种方式调度的任务不需要运行队列工作器就能被处理：

```php
use App\Jobs\SendNotification;

SendNotification::dispatchAfterResponse();
```

你也可以 `dispatch` 一个闭包并将 `afterResponse` 方法链式调用到 `dispatch` 帮助器上，以在发送 HTTP 响应后执行闭包：

```php
use App\Mail\WelcomeMessage;
use Illuminate\Support\Facades\Mail;

dispatch(function () {
    Mail::to('taylor@example.com')->send(new WelcomeMessage);
})->afterResponse();
```

<a name="synchronous-dispatching"></a>
### 同步调度

如果你想立即（同步）调度任务，你可以使用 `dispatchSync 方法`。使用此方法时，任务不会排队，会在当前进程内立即执行

```php
<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PodcastController extends Controller
{
    /**
     * 存储一个新的播客.
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // 创建播客...

        ProcessPodcast::dispatchSync($podcast);

        return redirect('/podcasts');
    }
}
```

<a name="jobs-and-database-transactions"></a>
### 队列和数据库事务

在数据库事务中调度作业是完全可以的，但你应该特别注意确保你的作业实际上能够成功执行。在事务中调度作业时，有可能作业在父事务提交之前就被工作器处理了。当这种情况发生时，你在数据库事务期间对模型或数据库记录所做的任何更新可能还没有反映在数据库中。此外，在事务中创建的任何模型或数据库记录可能还不存在于数据库中。



幸运的是，Laravel 提供了几种方法来解决这个问题。首先，你可以在队列连接的配置数组中设置 `after_commit` 连接选项：

```php
'redis' => [
    'driver' => 'redis',
    // ...
    'after_commit' => true,
],
```

当 `after_commit` 选项为 `true`, 你可以在数据库事务中调度作业；但是，Laravel 会等到打开的父数据库事务提交后再实际调度作业。当然，如果目前没有开启的数据库事务，作业将被立即调度。

如果事务因在事务期间发生的异常而回滚，那么在该事务期间调度的作业将被丢弃。

>[!注意]
>将 `after_commit` 配置选项设置为 `true` 还会导致任何排队的事件监听器、邮件、通知和广播事件在所有打开的数据库事务提交后被调度。

<a name="specifying-commit-dispatch-behavior-inline"></a>
#### 内联指定提交调度行为

如果你没有将 `after_commit` 队列连接配置选项设置为 `true`，你仍然可以指定特定作业应在所有打开的数据库事务提交后被调度。为此，你可以将 `afterCommit` 方法链接到你的调度操作：

```php
use App\Jobs\ProcessPodcast;

ProcessPodcast::dispatch($podcast)->afterCommit();
```

类似地，如果 `after_commit` 配置选项被设置为 `true`，你可以指定特定作业应立即调度，无需等待任何打开的数据库事务提交：

```php
ProcessPodcast::dispatch($podcast)->beforeCommit();
```

<a name="job-chaining"></a>
### 任务链

任务链允许你指定一组应在主任务成功执行后按顺序运行的排队任务。如果序列中的一个任务失败，其余的任务将不会运行。要执行一个排队的任务链，你可以使用 Bus facade 提供的 chain 方法。Laravel 的命令总线是建立在排队作业调度之上的底层组件：

```php
use App\Jobs\OptimizePodcast;
use App\Jobs\ProcessPodcast;
use App\Jobs\ReleasePodcast;
use Illuminate\Support\Facades\Bus;

Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->dispatch();
```



除了链式调用作业类实例，你还可以链式闭包：

```php
Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    function () {
        Podcast::update(/* ... */);
    },
])->dispatch();
```

> [!警告]
> 在任务中使用 `$this->delete()` 方法删除任务不会阻止链式任务的处理。只有当链中的任务失败时，链才会停止执行。

<a name="chain-connection-queue"></a>
#### 链式连接 & 队列

如果要指定链式任务应使用的连接和队列，可以使用 `onConnection` 和 `onQueue` 方法。这些方法指定应使用的队列连接和队列名称，除非为排队任务显式分配了不同的连接 / 队列：

```php
Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->onConnection('redis')->onQueue('podcasts')->dispatch();
```

<a name="adding-jobs-to-the-chain"></a>
#### 向链中添加任务
如果你想要从链中的另一个任务内向现有的任务链前置或后置添加任务。你可以使用 `prependToChain` 和 `appendToChain` 方法来实现这一点：

```php
/**
 * 执行任务.
 */
public function handle(): void
{
    // ...

    // 前置到当前链，在当前任务之后立即运行任务...
    $this->prependToChain(new TranscribePodcast);

    // 后置到当前链，在链末尾运行任务...
    $this->appendToChain(new TranscribePodcast);
}
```

<a name="chain-failures"></a>
#### 链式失败
在链式任务中，你可以使用 `catch` 方法来指定一个闭包，该闭包在链中的任务失败时被调用。给定的回调将接收导致任务失败的 `Throwable` 实例：

```php
use Illuminate\Support\Facades\Bus;
use Throwable;

Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->catch(function (Throwable $e) {
    // 链中的某个任务失败了...
})->dispatch();
```

> [!警告]
> 由于链回调被序列化并在稍后由 Laravel 队列执行，因此你不应在链回调中使用 `$this` 变量。



<a name="customizing-the-queue-and-connection"></a>
###自定义队列连接

###分发到特定队列
通过将任务推送到不同的队列，你可以「分类」你的队列任务，甚至可以优先分配多少个 worker 到各种队列。请记住，这并不会将任务推送到队列配置文件中定义的不同队列「连接」，而只是推送到单个连接内的特定队列。要指定队列，在分发任务时使用 `onQueue` 方法：

```php
<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PodcastController extends Controller
{
    /**
     * 存储一个新的播客.
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // 创建播客...

        ProcessPodcast::dispatch($podcast)->onQueue('processing');

        return redirect('/podcasts');
    }
}
```

或者，你可以在任务的构造函数中调用 `onQueue` 方法来指定任务的队列：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例.
     */
    public function __construct()
    {
        $this->onQueue('processing');
    }
}
```

<a name="dispatching-to-a-particular-connection"></a>
#### 调度到特定连接
如果你的应用与多个队列连接交互，你可以使用 `onConnection` 方法来指定任务应推送到的连接：

```php
<?php

namespace App\Http\Controllers;

use App\Jobs\ProcessPodcast;
use App\Models\Podcast;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PodcastController extends Controller
{
    /**
     * 存储一个新的播客.
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // 创建播客...

        ProcessPodcast::dispatch($podcast)->onConnection('sqs');

        return redirect('/podcasts');
    }
}
```



你可以链式调用 `onConnection` 和 `onQueue` 方法来指定任务的连接和队列：

```php
ProcessPodcast::dispatch($podcast)
    ->onConnection('sqs')
    ->onQueue('processing');
```

或者，你可以在任务的构造函数中调用 `onConnection` 方法来指定任务的连接：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的作业实例.
     */
    public function __construct()
    {
        $this->onConnection('sqs');
    }
}
```

<a name="max-job-attempts-and-timeout"></a>
### 指定最大任务尝试 次数 / 超时值

<a name="max-attempts"></a>
#### 最大尝试次数

如果你的队列任务遇到错误，你可能不希望它无限期地重试。因此，Laravel 提供了多种方法来指定任务可以尝试的次数或持续时间。

指定作业可能尝试的最大次数的一种方法是通过 Artisan 命令行的 `--tries` 开关。这将适用于调度作业的所有任务，除非正在处理的任务指定了它最大尝试次数：

```shell
php artisan queue:work --tries=3
```
如果一个任务超过其最大尝试次数，它将被视为「失败」的任务。有关处理失败任务的更多信息，请查看[处理失败队列](#dealing-with-failed-jobs)。如果给 `queue:work` 命令提供了 `--tries=0`，任务将无限次重试。

你可以采取更细粒度的方法，通过在任务类本身定义任务可以尝试的最大次数。如果在任务上指定了最大尝试次数，它将优先于命令行上提供的 `--tries` 值：

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * 任务可尝试的次数.
     *
     * @var int
     */
    public $tries = 5;
}
```



如果你需要对特定任务的最大尝试次数进行动态控制，你可以在作业上定义一个 tries 方法：

```php
/**
 * 确定任务可以尝试的次数.
 */
public function tries(): int
{
    return 5;
}
```

<a name="time-based-attempts"></a>
#### 基于时间的尝试

作为定义任务在失败前可尝试次数的替代方式，你可以定义一个任务应该超时的时间。这允许在给定时间范围内任意次数地尝试任务。要定义任务超时的时间，请在任务类中添加一个 `retryUntil` 方法。此方法应该返回一个 `DateTime` 实例：

```php
use DateTime;

/**
 * 确定任务应当超时的时间.
 */
public function retryUntil(): DateTime
{
    return now()->addMinutes(10);
}
```

如果同时定义了 `retryUntil` 和 `tries`，Laravel 会优先使用 `retryUntil` 方法。

> **注意**  
> 你也可以在 [队列事件监听器](/docs/laravel/12.x/events#queued-event-listeners) 和 [队列通知](/docs/laravel/12.x/notifications#queueing-notifications) 中定义 `tries` 属性或 `retryUntil` 方法。

<a name="max-exceptions"></a>
#### 最大异常数

有时你可能希望指定一个任务可以尝试多次，但如果重试是由给定数量的未处理异常触发的（而不是直接被 `release` 方法释放的），应该失败。为此，你可以在任务类中定义一个 `maxExceptions` 属性：

```php
<?php

namespace App\Jobs;

use Illuminate\Support\Facades\Redis;

class ProcessPodcast implements ShouldQueue
{
    /**
     * 可以尝试任务的次数.
     *
     * @var int
     */
    public $tries = 25;

    /**
     * 失败前允许的最大未处理异常数.
     *
     * @var int
     */
    public $maxExceptions = 3;

    /**
     * 执行任务.
     */
    public function handle(): void
    {
        Redis::throttle('key')->allow(10)->every(60)->then(function () {
            // 获得锁，处理播客...
        }, function () {
            // 无法获取锁...
            return $this->release(10);
        });
    }
}
```



在此示例中，如果应用程序无法获得 `Redis` 锁，则该任务将在 10 秒后被释放，并将继续重试最多 25 次。但是，如果任务抛出三个未处理的异常，则任务将失败。

<a name="timeout"></a>
#### 超时

通常，你大致知道你的排队任务需要多长时间。因此，Laravel 允许你指定一个「超时」值。默认情况下，超时值为 60 秒。如果任务的处理时间超过超时值指定的秒数，处理任务的工作进程将退出并报错。通常工作进程将由服务器上配置的 [进程管理器](#supervisor-configuration) 自动重启。

任务可以运行的最大秒数可以使用 Artisan 命令行上的 `--timeout` 开关指定：

```shell
php artisan queue:work --timeout=30
```

如果任务因不断超时超过其最大尝试次数，它将被标记为失败。

你还可以在任务类本身定义任务允许运行的最大秒数。如果在任务上指定了超时时间，它将优先于命令行上指定的任何超时时间：

```php
<?php

namespace App\Jobs;

class ProcessPodcast implements ShouldQueue
{
    /**
     * 在超时之前任务可以运行的秒数.
     *
     * @var int
     */
    public $timeout = 120;
}
```

有时，诸如 sockets 或外部 HTTP 连接之类的 IO 阻塞过程可能不会遵守你指定的超时。因此，在使用这些功能时，你应该始终尝试使用他们的 API 来指定超时时间。例如，当使用 Guzzle 时，你应该总是指定连接和请求超时值。

> [!警告]
> 必须安装 PHP `pcntl` 扩展才能指定任务超时。此外，任务的「超时」值应始终小于其[「任务到期」](#job-expiration) 值。否则，可能在任务实际完成执行或超时前，任务就会被重试。



<a name="failing-on-timeout"></a>
#### 超时失败

如果你希望在任务超时的时候将其标记为 [failed](#dealing-with-failed-jobs)，你可以在任务类上定义 `$failOnTimeout` 属性:

```php
/**
 * 标示是否应在超时时标记为失败
 *
 * @var bool
 */
public $failOnTimeout = true;
```

<a name="error-handling"></a>
### 错误处理

如果在处理任务时抛出异常，任务将自动被释放回队列，用于之后进行重试。任务将继续释放，直到尝试达到应用程序允许的最大次数。最大重试次数由 `queue:work` Artisan 命令上使用的 `--tries` 开关定义。或者，最大尝试次数可以在任务类本身上定义。有关运行队列工作器的更多信息可以在[下面找到](#running-the-queue-worker)。

<a name="manually-releasing-a-job"></a>
#### 手动释放任务

有时你可能希望手动将任务释放回队列，以便稍后再次尝试。你可以通过调用 `release` 方法来实现这一点：

```php
/**
 * 执行任务
 */
public function handle(): void
{
    // ...

    $this->release();
}
```

默认情况下，`release` 方法会将任务立即释放回队列。但是，你可以通过向 `release` 方法传递一个整数或日期实例来命令队列，使任务在指定的秒数之后才能进行处理：

```php
$this->release(10);

$this->release(now()->addSeconds(10));
```



<a name="manually-failing-a-job"></a>
#### 手动标记任务失败

有时你可能需要手动将任务标记为「失败」。为此，你可以调用 `fail` 方法：

```php
/**
 * 执行任务
 */
public function handle(): void
{
    // ...

    $this->fail();
}
```

如果你想在捕获到异常的时候直接将你的任务标记为失败，你可以将异常传递给 `fail` 方法。 或者，为方便起见，你可以传递一个字符串来表示错误异常信息：

```php
$this->fail($exception);

$this->fail('Something went wrong.');
```

> [注意]
> 有关失败任务的更多信息，请查看 [处理任务失败的文档](#dealing-with-failed-jobs)。

<a name="job-batching"></a>
## 任务批处理

Laravel 的任务批处理功能允许你轻松执行一批作业，然后在任务批次完成执行后执行某些操作。在开始之前，你应该创建一个数据库迁移来构建一个表，该表将包含有关任务批次的元信息，例如它们的完成百分比。可以使用 `make:queue-batches-table` Artisan 命令来生成这个迁移：

```shell
php artisan make:queue-batches-table

php artisan migrate
```

<a name="defining-batchable-jobs"></a>
### 定义可批处理的任务

要定义可批处理的任务，你应该像平常一样 [创建一个可排队的任务](#creating-jobs) ；但是，你应该将 `Illuminate\Bus\Batchable` trait 添加到任务类。这个 trait 提供了一个 `batch` 方法，可用于检索任务正在执行的当前批次：

```php
<?php

namespace App\Jobs;

use Illuminate\Bus\Batchable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ImportCsv implements ShouldQueue
{
    use Batchable, Queueable;

    /**
     * 执行任务
     */
    public function handle(): void
    {
        if ($this->batch()->cancelled()) {
            // 确定批次是否已取消...

            return;
        }

        // 导入 CSV 文件的一部分...
    }
}
```



<a name="dispatching-batches"></a>
### 调度批处理任务

要调度一批作业，你应该使用 `Bus` facade 的 `batch` 方法。当然，批处理主要在与完成回调结合使用时才有用。因此，你可以使用 `then`、`catch` 和 `finally` 方法为批处理的定义完成回调。这些回调在被调用时都将接收到一个 `Illuminate\Bus\Batch` 实例。在这个例子中，我们假设有正在排队的一批任务，每个任务都去处理 CSV 文件中给定数量的行：

```php
use App\Jobs\ImportCsv;
use Illuminate\Bus\Batch;
use Illuminate\Support\Facades\Bus;
use Throwable;

$batch = Bus::batch([
    new ImportCsv(1, 100),
    new ImportCsv(101, 200),
    new ImportCsv(201, 300),
    new ImportCsv(301, 400),
    new ImportCsv(401, 500),
])->before(function (Batch $batch) {
    // 批处理已创建但尚未添加的任务...
})->progress(function (Batch $batch) {
    // 单个任务已成功完成..
})->then(function (Batch $batch) {
    // 全部任务已成功完成..
})->catch(function (Batch $batch, Throwable $e) {
    // 检测到第一个批处理任务失败...
})->finally(function (Batch $batch) {
    // 批处理执行完毕...
})->dispatch();

return $batch->id;
```

批处理的 ID 可以通过 `$batch->id` 属性访问，可用于 [查询 Laravel 命令总线](#inspecting-batches) 以获取有关批次分派后的信息。

> [注意]
> 由于批处理回调会被序列化并在稍后由 Laravel 队列执行，所以你不应该在回调中使用 `$this` 变量。此外，由于批处理作业是封装在数据库事务中的，所以不应该在作业中执行触发隐式提交的数据库语句。



<a name="naming-batches"></a>
#### 命名批处理

部分工具，如 Laravel Horizon 和 Laravel Telescope 可能会为命名的批处理提供更友好的调试信息。为了给批处理分配一个任意名称，你可以在定义批处理时调用 `name` 方法：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务都已成功完成...
})->name('Import CSV')->dispatch();
```

<a name="batch-connection-queue"></a>
#### 批处理连接 & 队列

如果你想指定应用于批处理任务的连接和队列，你可以使用 `onConnection` 和 `onQueue` 方法。 所有批处理任务必须在相同的连接和队列中执行：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务都已成功完成...
})->onConnection('redis')->onQueue('imports')->dispatch();
```

<a name="chains-and-batches"></a>
### 链式 ＆ 批处理

你可以将一组 [链式任务](#job-chaining) 定义在一个批处理中，方法是将链接的任务放在一个数组内。例如，我们可以并行执行两个任务链，并在两个任务链都完成处理后执行一个回调：

```php
use App\Jobs\ReleasePodcast;
use App\Jobs\SendPodcastReleaseNotification;
use Illuminate\Bus\Batch;
use Illuminate\Support\Facades\Bus;

Bus::batch([
    [
        new ReleasePodcast(1),
        new SendPodcastReleaseNotification(1),
    ],
    [
        new ReleasePodcast(2),
        new SendPodcastReleaseNotification(2),
    ],
])->then(function (Batch $batch) {
    // ...
})->dispatch();
```

相反，你可以通过在 [链](#job-chaining) 中定义批处理来在一个链中运行一批任务。例如，你可以先运行一个批处理任务来发布多个播客，然后运行一个批处理任务来发送发布通知：

```php
use App\Jobs\FlushPodcastCache;
use App\Jobs\ReleasePodcast;
use App\Jobs\SendPodcastReleaseNotification;
use Illuminate\Support\Facades\Bus;

Bus::chain([
    new FlushPodcastCache,
    Bus::batch([
        new ReleasePodcast(1),
        new ReleasePodcast(2),
    ]),
    Bus::batch([
        new SendPodcastReleaseNotification(1),
        new SendPodcastReleaseNotification(2),
    ]),
])->dispatch();
```



<a name="adding-jobs-to-batches"></a>
### 批量添加任务

有些时候，批量向批处理中添加任务可能很有用。当你需要批量处理数千个任务时，这种模式非常好用，而这些任务在 Web 请求期间可能需要很长时间才能调度。因此，你可能希望调度初始批次的「加载器」任务，这些任务与更多任务相结合：

```php
$batch = Bus::batch([
    new LoadImportBatch,
    new LoadImportBatch,
    new LoadImportBatch,
])->then(function (Batch $batch) {
    // 所有任务都成功执行之后...
})->name('Import Contacts')->dispatch();
```

在这个例子中，我们将使用 `LoadImportBatch` 任务为批处理添加其他任务。为此，我们可以对批处理实例使用 `add` 方法，该方法可以通过任务的 `batch` 方法访问：

```php
use App\Jobs\ImportContacts;
use Illuminate\Support\Collection;

/**
 * 执行任务
 */
public function handle(): void
{
    if ($this->batch()->cancelled()) {
        return;
    }

    $this->batch()->add(Collection::times(1000, function () {
        return new ImportContacts;
    }));
}
```

> [!注意]
> 你只能将任务添加到当前任务所属的批处理中。

<a name="inspecting-batches"></a>
### 校验批处理

为批处理完成后提供回调的 `Illuminate\Bus\Batch` 实例中具有多种属性和方法，可以帮助你与指定的批处理业务进行交互和检查：

```php
// 批处理的UUID..
$batch->id;

// 批处理的名称（如果已经设置的话）...
$batch->name;

// 分配给批处理的任务数量...
$batch->totalJobs;

// 队列还没处理的任务数量...
$batch->pendingJobs;

// 失败的任务数量...
$batch->failedJobs;

// 到目前为止已经处理的任务数量...
$batch->processedJobs();

// 批处理已经完成的百分比（0-100）...
$batch->progress();

// 批处理是否已经完成执行...
$batch->finished();

// 取消批处理的运行...
$batch->cancel();

// 批处理是否已经取消...
$batch->cancelled();
```



<a name="returning-batches-from-routes"></a>
#### 从路由返回批次

所有 `Illuminate\Bus\Batch` 实例都是 JSON 可序列化的，这意味着你可以直接从应用程序的一个路由返回它们，以检索包含有关批处理的信息的 JSON 有效负载，包括其完成进度。这样可以方便地在应用程序的 UI 中显示有关批处理完成进度的信息。

要通过 ID 检索批次，你可以使用 `Bus` facade 的 `findBatch` 方法：

```php
use Illuminate\Support\Facades\Bus;
use Illuminate\Support\Facades\Route;

Route::get('/batch/{batchId}', function (string $batchId) {
    return Bus::findBatch($batchId);
});
```

<a name="cancelling-batches"></a>
### 取消批次

有时你可能需要取消给定批处理的执行。这可以通过调用 `Illuminate\Bus\Batch` 实例的 `cancel` 方法来完成：

```php
/**
 * 执行任务
 */
public function handle(): void
{
    if ($this->user->exceedsImportLimit()) {
        return $this->batch()->cancel();
    }

    if ($this->batch()->cancelled()) {
        return;
    }
}
```

正如你在前面的示例中可能已经注意到的那样，批处理任务通常应在继续执行之前确定其对应的批处理是否已被取消。但为了方便起见，你也可以为任务分配 `SkipIfBatchCancelled` [中间件](#job-middleware)。顾名思义，这个中间件会指示 Laravel，如果其对应的批处理已被取消，则不处理任务：

```php
use Illuminate\Queue\Middleware\SkipIfBatchCancelled;

/**
 * 获取任务应通过的中间件
 */
public function middleware(): array
{
    return [new SkipIfBatchCancelled];
}
```

<a name="batch-failures"></a>
### 批处理失败

当批处理任务失败时，将调用 `catch` 回调（如果已分配）。此回调仅针对批处理中失败的第一个任务调用。



<a name="allowing-failures"></a>
#### 允许失败

当批次中的作业失败时，Laravel 会自动将该批次标记为 「已取消」。如果需要，可以禁用此行为，以便任务失败后不会自动将批处理标记为已取消。这可以通过在调度批处理时调用 `allowFailures` 方法来实现：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务都已经成功执行...
})->allowFailures()->dispatch();
```

<a name="retrying-failed-batch-jobs"></a>
#### 重试失败的批处理任务

为了方便起见，Laravel 提供了一个 `queue:retry-batch` Artisan 命令，允许你轻松地重试给定批处理的所有失败作业。`queue:retry-batch` 命令接受要重试其失败任务的批处理的 UUID：

```shell
php artisan queue:retry-batch 32dbc76c-4f82-4749-b610-a639fe0099b5
```

<a name="pruning-batches"></a>
### 修剪批处理

如果不进行修剪，`job_batches` 表可以非常快速地累积记录。为了缓解这种情况，您应该将 `queue:prune-batches` Artisan 命令安排为 [每天](/docs/laravel/12.x/scheduling) 运行：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches')->daily();
```

默认情况下，所有已完成且超过 24 小时的批处理都会被修剪。在调用命令时你可以使用 `hours` 选项来决定保留批处理数据的时间长短。例如，以下命令将删除所有 48 小时前完成的批处理：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48')->daily();
```

有时，你的 `jobs_batches` 表可能会积累从未成功完成的批处理记录，例如未成功重试的失败任务的批处理。你可以指示 `queue:prune-batches` 命令使用 `unfinished` 选项来修剪这些未完成的批处理记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48 --unfinished=72')->daily();
```



同样，你的 `jobs_batches` 表也可能积累已取消批处理的批处理记录。你可以指示 `queue:prune-batches` 命令使用 `cancelled` 选项来修剪这些已取消批处理记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48 --cancelled=72')->daily();
```

<a name="storing-batches-in-dynamodb"></a>
### 在 DynamoDB 中存储批处理

Laravel 还支持在 [DynamoDB](https://aws.amazon.com/dynamodb) 中存储批处理元信息，而不是在关系数据库中。不过，你需要手动创建一个 DynamoDB 表来存储所有的批处理记录。

通常情况下，此表应命名为 `job_batches`，但你应基于应用程序 `queue` 配置文件中的 `queue.batching.table` 配置值来命名此表。

<a name="dynamodb-batch-table-configuration"></a>
#### DynamoDB 批处理表配置

`job_batches` 表应具有一个名为 `application` 的字符串主分区键和一个名为 `id` 的字符串主排序键。键中的 `application` 部分将包含你的应用程序名称，该名称由应用程序 `app` 配置文件中的 `name` 配置值定义。由于应用程序名称是 DynamoDB 表键的一部分，因此可以使用同一张表来存储多个 Laravel 应用程序的任务批处理。

此外，如果你希望利用 [自动批处理修剪](#pruning-batches-in-dynamodb) 功能，你可以为表定义 `ttl` 属性。

<a name="dynamodb-configuration"></a>
#### DynamoDB 配置

接下来，安装 AWS SDK，以便你的 Laravel 应用程序可以与 Amazon DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

然后，将 `queue.batching.driver` 配置选项的值设置为 `dynamodb`。此外，你应在 `batching` 配置数组中定义` key`、`secret` 和 `region` 配置选项。这些选项将用于认证 AWS。使用 `dynamodb` 驱动时不需要 `queue.batching.database` 配置选项：

```php
'batching' => [
    'driver' => env('QUEUE_BATCHING_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'job_batches',
],
```



#### 在 DynamoDB 中清理批次（Pruning Batches）

当使用 [DynamoDB](https://aws.amazon.com/dynamodb) 来存储任务批次（job batch）信息时，用于清理存储在关系型数据库中的批次的常规清理命令将无法使用。
相反，你可以利用 [DynamoDB 的原生 TTL 功能](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)，自动删除过期的批次记录。

如果你在定义 DynamoDB 表时设置了一个 `ttl` 属性，你可以通过配置参数告诉 Laravel 如何清理批次记录。
配置项 `queue.batching.ttl_attribute` 用于指定保存 TTL 值的属性名，而 `queue.batching.ttl` 用于定义批次记录在上次更新后经过多少秒后可以从 DynamoDB 表中删除：

```php
'batching' => [
    'driver' => env('QUEUE_FAILED_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'job_batches',
    'ttl_attribute' => 'ttl',
    'ttl' => 60 * 60 * 24 * 7,  // 7 天...
],
```

## 队列中的闭包（Queueing Closures）

除了将任务类（job class）派发到队列中，你还可以将 **闭包（closure）** 派发到队列中。
这对于需要在当前请求周期之外执行的快速、简单任务来说非常方便。

当你将闭包派发到队列时，闭包的代码内容会被 **加密签名**，以防止其在传输过程中被篡改：

```php
$podcast = App\Podcast::find(1);

dispatch(function () use ($podcast) {
    $podcast->publish();
});
```

如果你想为队列中的闭包指定一个名称，该名称可以用于队列监控面板（queue reporting dashboards）或通过 `queue:work` 命令显示，你可以使用 `name` 方法：

```php
dispatch(function () {
    // ...
})->name('Publish Podcast');
```



使用 `catch` 方法时，你可以提供一个闭包，当队列中的闭包在耗尽所有队列的[配置重试次数](#max-job-attempts-and-timeout)后仍未成功完成时，将会执行这个闭包：

```php
use Throwable;

dispatch(function () use ($podcast) {
    $podcast->publish();
})->catch(function (Throwable $e) {
    // 该任务执行失败...
});
```

> [!警告]
> 由于 `catch` 回调会被序列化，并在稍后的时间由 Laravel 队列执行，因此在 `catch` 回调中不要使用 `$this` 变量。

## 运行队列工作进程（Running the Queue Worker）

### `queue:work` 命令

Laravel 提供了一个 Artisan 命令，用于启动一个队列工作进程（worker），并在有新任务被推送到队列时进行处理。
你可以使用 `queue:work` Artisan 命令来运行该工作进程。
请注意，一旦 `queue:work` 命令启动后，它会一直运行，直到你手动停止它或关闭终端为止：

```shell
php artisan queue:work
```

> [!注意]
> 若要让 `queue:work` 进程在后台永久运行，你应使用诸如 [Supervisor](#supervisor-configuration) 之类的进程监控程序，以确保队列工作进程不会停止。

当调用 `queue:work` 命令时，如果希望在命令输出中包含已处理任务的 ID，可以添加 `-v` 参数：

```shell
php artisan queue:work -v
```

请记住，**队列工作进程是长时间运行的进程**，并会将启动时加载的应用状态保存在内存中。
因此，它们在启动后将不会察觉到你代码库中的任何更改。
所以，在部署过程中，请务必[重启你的队列工作进程](#queue-workers-and-deployment)。

此外，请注意，应用程序中创建或修改的任何静态状态，在任务之间不会被自动重置。



或者，你也可以运行 `queue:listen` 命令。
使用 `queue:listen` 命令时，当你想重新加载更新后的代码或重置应用程序状态时，无需手动重启工作进程；
然而，该命令的效率明显低于 `queue:work` 命令：

```shell
php artisan queue:listen
```

#### 运行多个队列工作进程（Running Multiple Queue Workers）

若要为同一个队列分配多个工作进程以并发处理任务，你只需启动多个 `queue:work` 进程即可。
在本地环境中，可以通过在终端中打开多个标签页来实现；
在生产环境中，则可以通过进程管理器的配置来实现。
[当使用 Supervisor 时](#supervisor-configuration)，可以使用 `numprocs` 配置项来设置进程数量。

#### 指定连接和队列（Specifying the Connection and Queue）

你也可以指定工作进程应使用的队列连接。
传递给 `work` 命令的连接名称应与 `config/queue.php` 配置文件中定义的某个连接名称相对应：

```shell
php artisan queue:work redis
```

默认情况下，`queue:work` 命令只会处理指定连接上的默认队列中的任务。
不过，你可以进一步自定义队列工作进程，只处理某个连接下的特定队列。
例如，如果你所有的邮件任务都在 `redis` 队列连接的 `emails` 队列中进行处理，可以运行以下命令来启动仅处理该队列的工作进程：

```shell
php artisan queue:work redis --queue=emails
```

#### 处理指定数量的任务（Processing a Specified Number of Jobs）

可以使用 `--once` 选项让工作进程只处理队列中的**一个任务**：

```shell
php artisan queue:work --once
```



`--max-jobs` 选项可用于指示工作进程在处理指定数量的任务后退出。
该选项在与 [Supervisor](#supervisor-configuration) 结合使用时非常有用，可以让工作进程在处理完一定数量的任务后自动重启，从而释放其可能累积的内存：

```shell
php artisan queue:work --max-jobs=1000
```

#### 处理所有队列任务后退出（Processing All Queued Jobs and Then Exiting）

`--stop-when-empty` 选项可用于指示工作进程在处理完所有队列中的任务后优雅地退出。
当你在 Docker 容器中处理 Laravel 队列，并希望在队列为空后关闭容器时，此选项会非常有用：

```shell
php artisan queue:work --stop-when-empty
```

#### 在指定时间内处理任务（Processing Jobs for a Given Number of Seconds）

`--max-time` 选项可用于指示工作进程在指定的秒数内处理任务，然后退出。
此选项与 [Supervisor](#supervisor-configuration) 配合使用时非常有用，可以让工作进程在运行一定时间后自动重启，从而释放其可能累积的内存：

```shell
# 处理任务一小时后退出...
php artisan queue:work --max-time=3600
```

#### 工作进程的休眠时间（Worker Sleep Duration）

当队列中有任务可用时，工作进程会持续处理任务，任务之间不会有延迟。
然而，`sleep` 选项用于指定当队列中**没有任务可用时**，工作进程应“休眠”多少秒。
当然，在休眠期间，工作进程不会处理任何新任务：

```shell
php artisan queue:work --sleep=3
```



#### 维护模式与队列（Maintenance Mode and Queues）

当你的应用处于[维护模式](/docs/laravel/12.x/configuration#maintenance-mode)时，**不会处理任何排队的任务（queued jobs）**。
一旦应用退出维护模式，这些任务将会恢复正常处理。

若要在启用维护模式时仍强制让队列工作进程处理任务，可以使用 `--force` 选项：

```shell
php artisan queue:work --force
```

#### 资源使用注意事项（Resource Considerations）

守护进程（daemon）队列工作进程在处理每个任务前**不会重新启动框架**。
因此，在每个任务执行完毕后，你应释放占用较大的资源。
例如，如果你使用 GD 库进行图像处理，那么在处理完图像后应调用 `imagedestroy` 来释放内存。

### 队列优先级（Queue Priorities）

有时你可能希望对队列的处理顺序进行优先级设置。
例如，在 `config/queue.php` 配置文件中，你可以将 `redis` 连接的默认 `queue` 设置为 `low`。
不过，偶尔你可能希望将任务推送到一个高优先级队列中，例如：

```php
dispatch((new Job)->onQueue('high'));
```

若要启动一个工作进程，使其在处理 `low` 队列中的任务之前，先处理完 `high` 队列中的所有任务，可以在执行 `work` 命令时传递一个以逗号分隔的队列名称列表：

```shell
php artisan queue:work --queue=high,low
```

### 队列工作进程与部署（Queue Workers and Deployment）

由于队列工作进程是长时间运行的进程，因此它们不会自动察觉代码的更改。
因此，部署使用队列的应用程序时，最简单的方式是在部署过程中**重启工作进程**。
你可以通过执行以下命令优雅地重启所有工作进程：

```shell
php artisan queue:restart
```



此命令会指示所有的队列工作进程在**完成当前正在处理的任务后优雅地退出**，从而确保不会丢失任何正在执行的任务。
由于在执行 `queue:restart` 命令时，队列工作进程会退出，因此你应当使用诸如 [Supervisor](#supervisor-configuration) 之类的**进程管理器**，以便自动重新启动这些队列工作进程。

> [!注意]
> 队列使用 [cache](/docs/laravel/12.x/cache)（缓存）来存储重启信号，因此在使用此功能之前，你应当确保应用程序已经正确配置了缓存驱动。

### 任务过期与超时（Job Expirations and Timeouts）

#### 任务过期（Job Expiration）

在 `config/queue.php` 配置文件中，每个队列连接都会定义一个 `retry_after` 选项。
该选项指定了队列连接在重新尝试处理某个任务之前应等待的秒数。
例如，如果 `retry_after` 的值设置为 `90`，则当某个任务已被处理了 90 秒但仍未被释放或删除时，它将被重新放回队列中。
通常，你应当将 `retry_after` 的值设置为任务在合理情况下应完成处理的最长时间。

> [!警告]
> 唯一没有 `retry_after` 配置项的队列连接是 **Amazon SQS**。
> SQS 会根据 AWS 控制台中设置的 [默认可见性超时时间（Default Visibility Timeout）](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/AboutVT.html) 来自动重试任务。

#### 工作进程超时（Worker Timeouts）

`queue:work` Artisan 命令提供了一个 `--timeout` 选项。
默认情况下，`--timeout` 的值为 **60 秒**。
如果某个任务的处理时间超过了该超时时间，正在处理该任务的工作进程将以错误状态退出。
通常，这类工作进程会由服务器上配置的 [进程管理器](#supervisor-configuration) 自动重新启动：

```shell
php artisan queue:work --timeout=60
```



`retry_after` 配置选项与 `--timeout` 命令行选项虽然不同，但它们协同工作，以确保任务不会丢失，并且每个任务只会被成功处理一次。

> [!警告]
> `--timeout` 的值应始终比 `retry_after` 配置值**短几秒钟**。这样可以确保在任务被重新尝试之前，处理卡死任务的工作进程会被终止。如果你的 `--timeout` 值比 `retry_after` 配置值更长，那么同一个任务可能会被处理两次。

## Supervisor 配置

在生产环境中，你需要一种方式来**保持 `queue:work` 进程持续运行**。
`queue:work` 进程可能因为多种原因而停止运行，例如超出工作进程超时时间（worker timeout）或执行了 `queue:restart` 命令。

因此，你需要配置一个**进程监控器（process monitor）**，以便在检测到 `queue:work` 进程退出时自动重新启动它们。
此外，进程监控器还可以让你指定希望同时运行多少个 `queue:work` 进程。
Supervisor 是 Linux 环境中常用的进程监控工具，以下文档将介绍如何配置它。

#### 安装 Supervisor

Supervisor 是一个用于 Linux 操作系统的进程监控器，它会在 `queue:work` 进程发生故障时自动重新启动这些进程。
在 Ubuntu 系统上，你可以使用以下命令安装 Supervisor

```shell
sudo apt-get install supervisor
```

> [!注意]
> 如果你觉得自己配置和管理 Supervisor 过于复杂，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com)，它提供了一个**全托管的平台**来运行 Laravel 队列工作进程。



#### 配置 Supervisor

Supervisor 的配置文件通常存放在 `/etc/supervisor/conf.d` 目录中。
在这个目录下，你可以创建任意数量的配置文件，用于指示 Supervisor 应如何监控你的进程。
例如，我们可以创建一个名为 `laravel-worker.conf` 的文件，用来启动并监控 `queue:work` 进程：

```ini
[program:laravel-worker]
process_name=%(program_name)s_%(process_num)02d
command=php /home/forge/app.com/artisan queue:work sqs --sleep=3 --tries=3 --max-time=3600
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
user=forge
numprocs=8
redirect_stderr=true
stdout_logfile=/home/forge/app.com/worker.log
stopwaitsecs=3600
```

在这个示例中，`numprocs` 指令会告诉 Supervisor 启动 **8 个 `queue:work` 进程** 并对它们进行监控，
如果任何一个进程发生故障，Supervisor 会自动重启它们。
你应该根据实际情况修改 `command` 指令的内容，以反映你所希望使用的队列连接和工作进程选项。

> [!警告]
> 请确保 `stopwaitsecs` 的值**大于你最长运行任务所需的时间（秒）**。否则，Supervisor 可能会在任务尚未处理完成时强制终止它。

#### 启动 Supervisor

创建好配置文件后，你可以使用以下命令更新 Supervisor 的配置并启动这些进程：

```shell
sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl start "laravel-worker:*"
```

有关 Supervisor 的更多信息，请参考 [Supervisor 官方文档](http://supervisord.org/index.html)。

## 处理失败的任务（Dealing With Failed Jobs）

有时，你的队列任务可能会失败。别担心，事情不总是一帆风顺的！
Laravel 提供了一种便捷的方式，可以[指定任务的最大尝试次数](#max-job-attempts-and-timeout)。
当一个异步任务超过该最大尝试次数后，它会被插入到 `failed_jobs` 数据表中。

而[同步分发的任务](/docs/laravel/12.x/queues#synchronous-dispatching)如果失败，则不会记录在此表中，
它们的异常会被应用程序**立即处理**。



在新的 Laravel 应用中，通常已经自带用于创建 `failed_jobs` 表的迁移文件。
但是，如果你的应用中没有这个表的迁移文件，可以使用以下命令创建：

```shell
php artisan make:queue-failed-table

php artisan migrate
```

当运行一个 [队列工作进程（queue worker）](#running-the-queue-worker) 时，
你可以通过在 `queue:work` 命令中使用 `--tries` 选项来指定任务的最大尝试次数。
如果你没有为 `--tries` 指定值，则任务只会被尝试一次，
或按照任务类中 `$tries` 属性所定义的次数执行：

```shell
php artisan queue:work redis --tries=3
```

使用 `--backoff` 选项，你可以指定当任务遇到异常时，Laravel 在重新尝试该任务前应等待多少秒。
默认情况下，任务在失败后会**立即**重新放回队列中以再次尝试：

```shell
php artisan queue:work redis --tries=3 --backoff=3
```

如果你希望**针对不同的任务单独配置**任务在遇到异常后重试前应等待的秒数，
可以在任务类中定义一个 `backoff` 属性：

```php
/**
 * 任务在重试前需要等待的秒数。
 *
 * @var int
 */
public $backoff = 3;
```

如果你需要更复杂的逻辑来动态计算任务的重试等待时间，
可以在任务类中定义一个 `backoff` 方法：

```php
/**
 * 计算任务在重试前需要等待的秒数。
 */
public function backoff(): int
{
    return 3;
}
```



你可以通过在 `backoff` 方法中返回一个数组来轻松配置“指数型（exponential）”的重试延迟。
在下面的示例中，任务第一次重试会等待 1 秒，第二次等待 5 秒，第三次等待 10 秒，
如果还有更多重试次数，之后的每次重试都会等待 10 秒：

```php
/**
 * 计算任务在重试前需要等待的秒数。
 *
 * @return array<int, int>
 */
public function backoff(): array
{
    return [1, 5, 10];
}
```

当某个任务执行失败时，你可能希望**向用户发送通知**，或**撤销任务已部分执行的操作**。
为此，你可以在任务类中定义一个 `failed` 方法。
导致任务失败的 `Throwable` 实例会作为参数传递给该方法：

```php
<?php

namespace App\Jobs;

use App\Models\Podcast;
use App\Services\AudioProcessor;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Throwable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(
        public Podcast $podcast,
    ) {}

    /**
     * 执行任务。
     */
    public function handle(AudioProcessor $processor): void
    {
        // 处理上传的播客音频...
    }

    /**
     * 处理任务失败的情况。
     */
    public function failed(?Throwable $exception): void
    {
        // 向用户发送失败通知等操作...
    }
}
```

> [!警告]
> 在调用 `failed` 方法之前，Laravel 会重新实例化一个新的任务对象。
> 因此，在 `handle` 方法中对类属性所做的任何修改都会**丢失**。

### 重试失败的任务（Retrying Failed Jobs）

要查看所有已插入到 `failed_jobs` 数据表中的失败任务，可以使用以下 Artisan 命令：

```shell
php artisan queue:failed
```



`queue:failed` 命令会列出作业的 ID、连接（connection）、队列（queue）、失败时间以及其他相关信息。
作业 ID 可以用来重试失败的作业。例如，要重试一个 ID 为 `ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece` 的失败作业，可以执行以下命令：

```shell
php artisan queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece
```

如果需要，你也可以在命令中传入多个 ID：

```shell
php artisan queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece 91401d2c-0784-4f43-824c-34f94a33c24d
```

你也可以重试某个特定队列中所有失败的作业：

```shell
php artisan queue:retry --queue=name
```

若要重试所有失败的作业，请在命令中将 `all` 作为 ID 传入：

```shell
php artisan queue:retry all
```

如果你想删除某个失败的作业，可以使用 `queue:forget` 命令：

```shell
php artisan queue:forget 91401d2c-0784-4f43-824c-34f94a33c24d
```

> [!注意]
> 当使用 [Horizon](/docs/laravel/12.x/horizon) 时，应使用 `horizon:forget` 命令来删除失败的作业，而不是使用 `queue:forget` 命令。

若要从 `failed_jobs` 表中删除所有失败的作业，可以使用 `queue:flush` 命令：

```shell
php artisan queue:flush
```

### 忽略缺失的模型

当将一个 Eloquent 模型注入到作业中时，该模型会在放入队列前自动序列化，并在作业被工作进程处理时从数据库中重新获取。
然而，如果在作业等待处理期间模型已被删除，那么该作业在执行时可能会因为找不到模型而抛出 `ModelNotFoundException` 异常。



为了方便起见，你可以通过将作业的 `deleteWhenMissingModels` 属性设置为 `true`，让系统在模型缺失时自动删除该作业。
当该属性被设置为 `true` 时，Laravel 会在不抛出异常的情况下静默丢弃该作业：

```php
/**
 * 如果模型不再存在，则删除该作业。
 *
 * @var bool
 */
public $deleteWhenMissingModels = true;
```

### 清理失败的作业

你可以通过执行 `queue:prune-failed` Artisan 命令来清理应用程序中 `failed_jobs` 表里的记录：

```shell
php artisan queue:prune-failed
```

默认情况下，所有超过 24 小时的失败作业记录都会被清理。
如果在命令中提供 `--hours` 选项，则只会保留最近 N 小时内插入的失败作业记录。
例如，下面的命令会删除所有在 48 小时之前插入的失败作业记录：

```shell
php artisan queue:prune-failed --hours=48
```

### 在 DynamoDB 中存储失败作业

Laravel 还支持将失败的作业记录存储在 [DynamoDB](https://aws.amazon.com/dynamodb) 中，而不是存储在关系型数据库表中。
不过，你必须手动创建一个 DynamoDB 表来存储所有的失败作业记录。
通常，这个表应命名为 `failed_jobs`，但你也可以根据应用程序 `queue` 配置文件中 `queue.failed.table` 配置项的值来命名。

`failed_jobs` 表应包含一个名为 `application` 的字符串类型主分区键（primary partition key），以及一个名为 `uuid` 的字符串类型主排序键（primary sort key）。
`application` 键的值将包含你应用程序的名称，该名称由应用配置文件 `app` 中的 `name` 配置项定义。
由于应用程序名称是 DynamoDB 表键的一部分，你可以使用同一个表来存储多个 Laravel 应用程序的失败作业记录。



此外，请确保你已安装 AWS SDK，以便 Laravel 应用程序能够与 Amazon DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

接着，将 `queue.failed.driver` 配置选项的值设置为 `dynamodb`。
另外，你还需要在失败作业（failed job）的配置数组中定义 `key`、`secret` 和 `region` 配置项。这些选项将用于与 AWS 进行身份验证。
当使用 `dynamodb` 驱动时，`queue.failed.database` 配置项将不再需要：

```php
'failed' => [
    'driver' => env('QUEUE_FAILED_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'failed_jobs',
],
```

### 禁用失败作业存储（Disabling Failed Job Storage）

你可以通过将 `queue.failed.driver` 配置项的值设置为 `null`，让 Laravel 在作业失败时直接丢弃它们，而不进行存储。
通常，可以通过设置环境变量 `QUEUE_FAILED_DRIVER` 来实现：

```ini
QUEUE_FAILED_DRIVER=null
```

### 失败作业事件（Failed Job Events）

如果你想注册一个在作业失败时会被调用的事件监听器，可以使用 `Queue` facade 的 `failing` 方法。
例如，我们可以在 Laravel 附带的 `AppServiceProvider` 的 `boot` 方法中为此事件附加一个闭包：

```php
<?php

namespace App\Providers;

use Illuminate\Support\Facades\Queue;
use Illuminate\Support\ServiceProvider;
use Illuminate\Queue\Events\JobFailed;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册任何应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动任何应用服务。
     */
    public function boot(): void
    {
        Queue::failing(function (JobFailed $event) {
            // $event->connectionName
            // $event->job
            // $event->exception
        });
    }
}
```



## 清空队列中的作业（Clearing Jobs From Queues）

> [!注意]
> 当使用 [Horizon](/docs/laravel/12.x/horizon) 时，应使用 `horizon:clear` 命令来清空队列中的作业，而不是使用 `queue:clear` 命令。

如果你想删除默认连接（default connection）中默认队列（default queue）的所有作业，可以使用以下 Artisan 命令：

```shell
php artisan queue:clear
```

你也可以提供 `connection` 参数和 `queue` 选项，以删除特定连接和特定队列中的作业：

```shell
php artisan queue:clear redis --queue=emails
```

> [!警告]
> 清空队列作业的功能仅适用于 SQS、Redis 和数据库（database）队列驱动。
> 另外，SQS 的消息删除过程最多可能需要 60 秒，因此在清空队列后 60 秒内发送到 SQS 队列的作业也可能会被一并删除。

## 监控你的队列（Monitoring Your Queues）

如果你的队列突然接收到大量作业，它可能会因此负载过重，导致作业执行等待时间过长。
如果需要，Laravel 可以在队列中的作业数量超过指定阈值时提醒你。

首先，你应该安排 `queue:monitor` 命令 [每分钟运行一次](/docs/laravel/12.x/scheduling)。
该命令需要传入你想监控的队列名称，以及希望的作业数量阈值：

```shell
php artisan queue:monitor redis:default,redis:deployments --max=100
```

仅安排此命令运行并不会自动触发通知来提醒你队列过载。
当该命令检测到某个队列中的作业数量超过你设定的阈值时，Laravel 会分发一个 `Illuminate\Queue\Events\QueueBusy` 事件。
你可以在应用程序的 `AppServiceProvider` 中监听此事件，以便在队列负载过高时向你或你的开发团队发送通知：

```php
use App\Notifications\QueueHasLongWaitTime;
use Illuminate\Queue\Events\QueueBusy;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Notification;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    Event::listen(function (QueueBusy $event) {
        Notification::route('mail', 'dev@example.com')
            ->notify(new QueueHasLongWaitTime(
                $event->connection,
                $event->queue,
                $event->size
            ));
    });
}
```



## 测试（Testing）

在测试分发作业（dispatch jobs）的代码时，你可能希望指示 Laravel 实际上**不要执行作业本身**，因为作业内部的代码可以单独直接测试，而无需依赖触发它的代码。
当然，如果你想测试作业本身的逻辑，可以在测试中直接实例化该作业类并调用其 `handle` 方法。

你可以使用 `Queue` facade 的 `fake` 方法，来防止队列中的作业实际被推送（执行）。
调用 `Queue::fake()` 方法后，你就可以断言应用程序是否尝试将作业推送到队列中。

```php tab=Pest
<?php

use App\Jobs\AnotherJob;
use App\Jobs\FinalJob;
use App\Jobs\ShipOrder;
use Illuminate\Support\Facades\Queue;

test('orders can be shipped', function () {
    Queue::fake();

    // 执行订单发货操作...

    // 断言没有任何作业被推送...
    Queue::assertNothingPushed();

    // 断言某个作业被推送到指定队列...
    Queue::assertPushedOn('queue-name', ShipOrder::class);

    // 断言某个作业被推送了两次...
    Queue::assertPushed(ShipOrder::class, 2);

    // 断言某个作业没有被推送...
    Queue::assertNotPushed(AnotherJob::class);

    // 断言一个闭包被推送到了队列...
    Queue::assertClosurePushed();

    // 断言被推送的作业总数...
    Queue::assertCount(3);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Jobs\AnotherJob;
use App\Jobs\FinalJob;
use App\Jobs\ShipOrder;
use Illuminate\Support\Facades\Queue;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_orders_can_be_shipped(): void
    {
        Queue::fake();

        // 执行订单发货操作...

        // 断言没有任何作业被推送...
        Queue::assertNothingPushed();

        // 断言某个作业被推送到指定队列...
        Queue::assertPushedOn('queue-name', ShipOrder::class);

        // 断言某个作业被推送了两次...
        Queue::assertPushed(ShipOrder::class, 2);

        // 断言某个作业没有被推送...
        Queue::assertNotPushed(AnotherJob::class);

        // 断言一个闭包被推送到了队列...
        Queue::assertClosurePushed();

        // 断言被推送的作业总数...
        Queue::assertCount(3);
    }
}
```



你可以向 `assertPushed` 或 `assertNotPushed` 方法传递一个闭包，以便断言某个通过特定“真值测试”的任务（job）已被推送。如果至少有一个任务通过了给定的真值测试，那么该断言就会被视为成功：

```php
Queue::assertPushed(function (ShipOrder $job) use ($order) {
    return $job->order->id === $order->id;
});
```

### 伪造（Fake）部分任务

如果你只需要伪造特定的任务，同时允许其他任务正常执行，可以将需要伪造的任务类名传递给 `fake` 方法：

```php tab=Pest
test('订单可以被发货', function () {
    Queue::fake([
        ShipOrder::class,
    ]);

    // 执行发货操作...

    // 断言任务被推送了两次...
    Queue::assertPushed(ShipOrder::class, 2);
});
```

```php tab=PHPUnit
public function test_orders_can_be_shipped(): void
{
    Queue::fake([
        ShipOrder::class,
    ]);

    // 执行发货操作...

    // 断言任务被推送了两次...
    Queue::assertPushed(ShipOrder::class, 2);
}
```

你也可以使用 `except` 方法来伪造**除指定任务之外的所有任务**：

```php
Queue::fake()->except([
    ShipOrder::class,
]);
```

### 测试任务链（Job Chains）

要测试任务链，你需要使用 `Bus` facade 的伪造功能。`Bus` facade 提供的 `assertChained` 方法可用于断言某个[任务链](/docs/laravel/12.x/queues#job-chaining)是否被调度。
`assertChained` 方法的第一个参数是一个由任务类组成的数组：

```php
use App\Jobs\RecordShipment;
use App\Jobs\ShipOrder;
use App\Jobs\UpdateInventory;
use Illuminate\Support\Facades\Bus;

Bus::fake();

// ...

Bus::assertChained([
    ShipOrder::class,
    RecordShipment::class,
    UpdateInventory::class
]);
```



正如上面的示例所示，任务链的数组可以是任务类名的数组。不过，你也可以提供一个由实际任务实例组成的数组。这样做时，Laravel 会确保这些任务实例的类名以及属性值与应用程序中被调度的任务链完全一致：

```php
Bus::assertChained([
    new ShipOrder,
    new RecordShipment,
    new UpdateInventory,
]);
```

你可以使用 `assertDispatchedWithoutChain` 方法来断言某个任务被推送时**没有附带任务链**：

```php
Bus::assertDispatchedWithoutChain(ShipOrder::class);
```

#### 测试任务链的修改

如果某个链式任务[在现有任务链前面或后面添加了任务](#adding-jobs-to-the-chain)，你可以使用该任务的 `assertHasChain` 方法来断言任务拥有预期的剩余任务链：

```php
$job = new ProcessPodcast;

$job->handle();

$job->assertHasChain([
    new TranscribePodcast,
    new OptimizePodcast,
    new ReleasePodcast,
]);
```

`assertDoesntHaveChain` 方法可用于断言该任务的剩余任务链为空：

```php
$job->assertDoesntHaveChain();
```

#### 测试链式批处理（Chained Batches）

如果你的任务链中[包含了一个任务批处理](#chains-and-batches)，你可以在链式断言中插入一个 `Bus::chainedBatch` 定义，用来断言该链式批处理是否符合预期：

```php
use App\Jobs\ShipOrder;
use App\Jobs\UpdateInventory;
use Illuminate\Bus\PendingBatch;
use Illuminate\Support\Facades\Bus;

Bus::assertChained([
    new ShipOrder,
    Bus::chainedBatch(function (PendingBatch $batch) {
        return $batch->jobs->count() === 3;
    }),
    new UpdateInventory,
]);
```

### 测试任务批处理（Job Batches）

`Bus` facade 的 `assertBatched` 方法可用于断言某个[任务批处理](/docs/laravel/12.x/queues#job-batching)是否被调度。传递给 `assertBatched` 方法的闭包会接收一个 `Illuminate\Bus\PendingBatch` 实例，你可以通过该实例检查批处理中的任务：

```php
use Illuminate\Bus\PendingBatch;
use Illuminate\Support\Facades\Bus;

Bus::fake();

// ...

Bus::assertBatched(function (PendingBatch $batch) {
    return $batch->name == 'import-csv' &&
           $batch->jobs->count() === 10;
});
```



你可以使用 `assertBatchCount` 方法来断言某个数量的批处理任务被调度：

```php
Bus::assertBatchCount(3);
```

你可以使用 `assertNothingBatched` 来断言没有任何批处理任务被调度：

```php
Bus::assertNothingBatched();
```

#### 测试任务与批处理的交互（Job / Batch Interaction）

此外，有时你可能需要测试单个任务与其底层批处理之间的交互。例如，你可能需要测试一个任务是否取消了其批处理的后续处理。
为此，你可以通过 `withFakeBatch` 方法为该任务分配一个伪造的批处理。
`withFakeBatch` 方法会返回一个包含任务实例和伪造批处理的元组（tuple）：

```php
[$job, $batch] = (new ShipOrder)->withFakeBatch();

$job->handle();

$this->assertTrue($batch->cancelled());
$this->assertEmpty($batch->added);
```

### 测试任务与队列的交互（Job / Queue Interactions）

有时，你可能需要测试一个排入队列的任务是否[将自己重新释放回队列中](#manually-releasing-a-job)，或者测试该任务是否将自己删除。
你可以通过实例化任务并调用 `withFakeQueueInteractions` 方法来测试这些队列交互。

在伪造了任务的队列交互后，你可以调用任务的 `handle` 方法。
调用任务后，你可以使用以下断言方法来验证队列交互是否符合预期：

-   `assertReleased`：断言任务被重新释放（可带延迟参数）
-   `assertDeleted`：断言任务被删除
-   `assertNotDeleted`：断言任务未被删除
-   `assertFailed`：断言任务失败
-   `assertFailedWith`：断言任务因指定异常失败
-   `assertNotFailed`：断言任务未失败

```php
use App\Exceptions\CorruptedAudioException;
use App\Jobs\ProcessPodcast;

$job = (new ProcessPodcast)->withFakeQueueInteractions();

$job->handle();

$job->assertReleased(delay: 30);
$job->assertDeleted();
$job->assertNotDeleted();
$job->assertFailed();
$job->assertFailedWith(CorruptedAudioException::class);
$job->assertNotFailed();
```

## 任务事件（Job Events）

通过在 `Queue` [facade](/docs/laravel/12.x/facades) 上使用 `before` 和 `after` 方法，你可以指定在队列任务被处理**之前**或**之后**执行的回调函数。
这些回调非常适合用于执行额外的日志记录或为仪表盘统计数据计数。
通常，你应在某个[服务提供者](/docs/laravel/12.x/providers)的 `boot` 方法中调用这些方法。
例如，可以使用 Laravel 自带的 `AppServiceProvider`：

```php
<?php

namespace App\Providers;

use Illuminate\Support\Facades\Queue;
use Illuminate\Support\ServiceProvider;
use Illuminate\Queue\Events\JobProcessed;
use Illuminate\Queue\Events\JobProcessing;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册应用的所有服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动应用的所有服务。
     */
    public function boot(): void
    {
        Queue::before(function (JobProcessing $event) {
            // $event->connectionName
            // $event->job
            // $event->job->payload()
        });

        Queue::after(function (JobProcessed $event) {
            // $event->connectionName
            // $event->job
            // $event->job->payload()
        });
    }
}
```



通过在 `Queue` [facade](/docs/laravel/12.x/facades) 上使用 `looping` 方法，你可以指定在工作进程尝试从队列中获取任务之前执行的回调函数。
例如，你可以注册一个闭包，用于回滚先前失败任务所遗留的未提交事务：

```php
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Queue;

Queue::looping(function () {
    while (DB::transactionLevel() > 0) {
        DB::rollBack();
    }
});
```

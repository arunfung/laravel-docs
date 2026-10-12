# 队列

- [简介](#introduction)
    - [连接与队列](#connections-vs-queues)
    - [驱动说明与前提条件](#driver-prerequisites)
- [创建任务](#creating-jobs)
    - [生成任务类](#generating-job-classes)
    - [类结构](#class-structure)
    - [唯一任务](#unique-jobs)
    - [防抖任务](#debounced-jobs)
    - [加密任务](#encrypted-jobs)
- [任务中间件](#job-middleware)
    - [速率限制](#rate-limiting)
    - [防止任务重叠执行](#preventing-job-overlaps)
    - [异常限流](#throttling-exceptions)
    - [释放任务](#releasing-jobs)
    - [跳过任务](#skipping-jobs)
- [分发任务](#dispatching-jobs)
    - [延迟分发](#delayed-dispatching)
    - [同步分发](#synchronous-dispatching)
    - [批量分发](#bulk-dispatching)
    - [分发前准备任务](#preparing-jobs-before-dispatch)
    - [任务与数据库事务](#jobs-and-database-transactions)
    - [任务链](#job-chaining)
    - [自定义队列与连接](#customizing-the-queue-and-connection)
    - [指定任务的最大尝试次数与超时时间](#max-job-attempts-and-timeout)
    - [SQS FIFO 队列与公平队列](#sqs-fifo-and-fair-queues)
    - [队列故障转移](#queue-failover)
    - [错误处理](#error-handling)
- [任务批处理](#job-batching)
    - [定义可批处理的任务](#defining-batchable-jobs)
    - [分发批次](#dispatching-batches)
    - [任务链与批次](#chains-and-batches)
    - [向批次添加任务](#adding-jobs-to-batches)
    - [检查批次](#inspecting-batches)
    - [取消批次](#cancelling-batches)
    - [批次失败](#batch-failures)
    - [清理批次](#pruning-batches)
    - [在 DynamoDB 中存储批次](#storing-batches-in-dynamodb)
- [将闭包加入队列](#queueing-closures)
- [运行队列工作进程](#running-the-queue-worker)
    - [`queue:work` 命令](#the-queue-work-command)
    - [队列优先级](#queue-priorities)
    - [队列工作进程与部署](#queue-workers-and-deployment)
    - [响应工作进程信号](#reacting-to-worker-signals)
    - [任务过期与超时](#job-expirations-and-timeouts)
    - [暂停与恢复队列工作进程](#pausing-and-resuming-queue-workers)
- [Supervisor 配置](#supervisor-configuration)
- [处理失败的任务](#dealing-with-failed-jobs)
    - [任务失败后的清理](#cleaning-up-after-failed-jobs)
    - [重试失败的任务](#retrying-failed-jobs)
    - [忽略缺失的模型](#ignoring-missing-models)
    - [清理失败的任务](#pruning-failed-jobs)
    - [在 DynamoDB 中存储失败的任务](#storing-failed-jobs-in-dynamodb)
    - [禁用失败任务存储](#disabling-failed-job-storage)
    - [任务失败事件](#failed-job-events)
- [清空队列中的任务](#clearing-jobs-from-queues)
- [监控队列](#monitoring-your-queues)
- [测试](#testing)
    - [模拟部分任务](#faking-a-subset-of-jobs)
    - [测试任务链](#testing-job-chains)
    - [测试任务批次](#testing-job-batches)
    - [测试任务与队列的交互](#testing-job-queue-interactions)
- [任务事件](#job-events)

<a name="introduction"></a>
## 简介

在构建 Web 应用时，你可能会遇到一些耗时较长、不适合在普通 Web 请求中执行的任务，例如解析并存储上传的 CSV 文件。好在 Laravel 让你能够轻松创建在后台处理的队列任务。将耗时任务移至队列后，应用就能快速响应 Web 请求，为用户提供更好的使用体验。

Laravel 队列为各种后端提供统一的队列 API，例如 [Amazon SQS](https://aws.amazon.com/sqs/)、[Redis](https://redis.io)，甚至关系型数据库。

Laravel 的队列配置选项位于应用的 `config/queue.php` 配置文件中。在这个文件中，你会找到框架自带的各个队列驱动的连接配置，包括数据库、[Amazon SQS](https://aws.amazon.com/sqs/)、[Redis](https://redis.io) 和 [Beanstalkd](https://beanstalkd.github.io/) 驱动，以及立即执行任务的同步驱动（适用于开发或测试）。此外，还有一个会丢弃队列任务的 `null` 队列驱动。

> [!NOTE]
> Laravel Horizon 为基于 Redis 的队列提供美观的仪表盘与配置系统。更多信息请参阅完整的 [Horizon 文档](/docs/{{version}}/horizon)。

<a name="connections-vs-queues"></a>
### 连接与队列

开始使用 Laravel 队列之前，理解「连接」与「队列」的区别很重要。`config/queue.php` 配置文件中有一个 `connections` 配置数组，用来定义与 Amazon SQS、Beanstalk 或 Redis 等后端队列服务的连接。不过，每个队列连接都可以包含多个「队列」，你可以将它们理解为不同的队列任务堆。

请注意，`queue` 配置文件中的每个连接配置示例都包含一个 `queue` 属性。这是发送到该连接的任务默认进入的队列。换句话说，如果分发任务时没有明确指定队列，任务就会进入连接配置的 `queue` 属性所定义的队列：

```php
use App\Jobs\ProcessPodcast;

// 此任务发送到默认连接的默认队列...
ProcessPodcast::dispatch();

// 此任务发送到默认连接的 emails 队列...
ProcessPodcast::dispatch()->onQueue('emails');
```

有些应用只需要一个简单的队列，不必将任务推送到多个队列。不过，对于希望区分任务处理方式或设置处理优先级的应用，使用多个队列尤其有用，因为 Laravel 队列工作进程允许你按优先级指定要处理的队列。例如，如果将任务推送到 `high` 队列，你可以运行一个优先处理这些任务的工作进程：

```shell
php artisan queue:work --queue=high,default
```

<a name="driver-prerequisites"></a>
### 驱动说明与前提条件

<a name="database"></a>
#### 数据库

要使用 `database` 队列驱动，你需要一个存放任务的数据库表。通常，Laravel 默认的 `0001_01_01_000002_create_jobs_table.php` [数据库迁移](/docs/{{version}}/migrations)已包含这个表；如果应用没有该迁移，可以使用 `make:queue-table` Artisan 命令创建它：

```shell
php artisan make:queue-table

php artisan migrate
```

<a name="redis"></a>
#### Redis

要使用 `redis` 队列驱动，应在 `config/database.php` 配置文件中配置 Redis 数据库连接。

> [!WARNING]
> `redis` 队列驱动不支持 Redis 的 `serializer` 和 `compression` 选项。

<a name="redis-cluster"></a>
##### Redis 集群

如果 Redis 队列连接使用 [Redis 集群](https://redis.io/docs/latest/operate/rs/databases/durability-ha/clustering)，队列名称必须包含[键哈希标签](https://redis.io/docs/latest/develop/using-commands/keyspace/#hashtags)，以确保同一队列的所有 Redis 键都位于同一个哈希槽中：

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

<a name="blocking"></a>
##### 阻塞

使用 Redis 队列时，可以通过 `block_for` 配置选项指定驱动等待可用任务的时长，之后才进入下一轮工作进程循环并重新轮询 Redis 数据库。

根据队列负载调整这个值，可能比持续轮询 Redis 数据库获取新任务更高效。例如，将其设为 `5`，表示驱动在等待可用任务时阻塞五秒：

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

> [!WARNING]
> 将 `block_for` 设为 `0` 会让队列工作进程无限阻塞，直到有任务可用。这也会导致 `SIGTERM` 等信号无法被处理，直到下一个任务处理完毕。

<a name="sqs-overflow-storage"></a>
#### SQS 溢出存储

Amazon SQS 对队列消息载荷的大小设有上限。如果需要分发载荷可能超过该限制的任务，可以配置 Laravel，将过大的 SQS 载荷存入缓存存储，再通过 SQS 发送指向载荷的引用。要启用该功能，请在 SQS 队列连接配置中添加 `overflow` 数组：

```php
'sqs' => [
    'driver' => 'sqs',
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'prefix' => env('SQS_PREFIX', 'https://sqs.us-east-1.amazonaws.com/your-account-id'),
    'queue' => env('SQS_QUEUE', 'default'),
    'suffix' => env('SQS_SUFFIX'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'after_commit' => false,
    'overflow' => [
        'enabled' => env('SQS_OVERFLOW_ENABLED', false),
        'store' => env('SQS_OVERFLOW_STORE'),
        'always' => false,
        'delete_after_processing' => true,
        'flush_on_clear' => env('SQS_OVERFLOW_FLUSH_ON_CLEAR', false),
    ],
],
```

启用溢出存储后，Laravel 会将大小至少为 1 MB 的载荷存入配置的缓存存储。如果 `always` 选项为 `true`，所有 SQS 载荷都会存入缓存，而不论大小。由于队列任务在处理时需要从缓存中获取载荷，应选择能保留载荷直至工作进程处理它们的存储。默认情况下，任务成功处理并从 SQS 删除后，其存储的载荷也会被删除。

如果 `flush_on_clear` 选项为 `true`，当 `queue:clear` 命令清空 SQS 队列时，配置的溢出缓存存储也会被清空。清空缓存存储可能会移除其中的所有条目，因此启用该选项时，应让 SQS 溢出存储使用专用的缓存存储。

<a name="other-driver-prerequisites"></a>
#### 其他驱动的前提条件

下列队列驱动需要相应的依赖，可通过 Composer 包管理器安装：

<div class="content-list" markdown="1">

- Amazon SQS: `aws/aws-sdk-php ~3.0`
- Beanstalkd: `pda/pheanstalk ^7.0|^8.0`
- Redis：`predis/predis ~3.0` 或 phpredis PHP 扩展
- [MongoDB](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/queues/): `mongodb/laravel-mongodb`

</div>

<a name="creating-jobs"></a>
## 创建任务

<a name="generating-job-classes"></a>
### 生成任务类

默认情况下，应用中所有可加入队列的任务都存放在 `app/Jobs` 目录中。如果该目录不存在，运行 `make:job` Artisan 命令时会创建它：

```shell
php artisan make:job ProcessPodcast
```

生成的类会实现 `Illuminate\Contracts\Queue\ShouldQueue` 接口，告诉 Laravel 应将任务推送到队列以异步执行。

> [!NOTE]
> 可以通过[发布桩文件](/docs/{{version}}/artisan#stub-customization)来自定义任务桩文件。

<a name="class-structure"></a>
### 类结构

任务类的结构很简单，通常只包含一个 `handle` 方法，队列处理任务时会调用它。我们先来看一个任务类示例。假设我们管理一个播客发布服务，需要在发布之前处理上传的播客文件：

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
        // 处理上传的播客...
    }
}
```

请注意，在这个示例中，我们可以将 [Eloquent 模型](/docs/{{version}}/eloquent)直接传入队列任务的构造函数。由于任务使用了 `Queueable` trait，Eloquent 模型及其已加载的关联关系会在任务处理过程中被妥善地序列化和反序列化。

如果队列任务在构造函数中接收 Eloquent 模型，只有模型的标识符会被序列化到队列中。实际处理任务时，队列系统会自动从数据库重新获取完整的模型实例及其已加载的关联关系。这种模型序列化方式大幅减小了发送给队列驱动的任务载荷。

<a name="handle-method-dependency-injection"></a>
#### `handle` 方法的依赖注入

队列处理任务时会调用 `handle` 方法。请注意，我们可以在任务的 `handle` 方法上使用类型提示声明依赖，Laravel 的[服务容器](/docs/{{version}}/container)会自动注入这些依赖。

如果希望完全控制容器如何向 `handle` 方法注入依赖，可以使用容器的 `bindMethod` 方法。它接收一个回调，回调会获得任务和容器。在回调中，你可以按需要调用 `handle` 方法。通常，应在 `App\Providers\AppServiceProvider` [服务提供者](/docs/{{version}}/providers)的 `boot` 方法中调用此方法：

```php
use App\Jobs\ProcessPodcast;
use App\Services\AudioProcessor;
use Illuminate\Contracts\Foundation\Application;

$this->app->bindMethod([ProcessPodcast::class, 'handle'], function (ProcessPodcast $job, Application $app) {
    return $job->handle($app->make(AudioProcessor::class));
});
```

> [!WARNING]
> 原始图像内容等二进制数据应先经过 `base64_encode` 函数处理，再传入队列任务。否则，任务加入队列时可能无法正确序列化为 JSON。

<a name="handling-relationships"></a>
#### 队列任务中的关联关系

任务加入队列时，Eloquent 模型所有已加载的关联关系也会被序列化，因此序列化后的任务字符串有时会很大。此外，任务反序列化并从数据库重新获取模型关联关系时，会获取完整的关联关系。在任务入队并序列化模型之前施加的任何关联约束，都不会在反序列化时重新应用。因此，如果只想处理某个关联关系的子集，应在队列任务中重新为该关联添加约束。

或者，为了避免序列化关联关系，可以在设置属性值时调用模型的 `withoutRelations` 方法。该方法会返回一个不包含已加载关联关系的模型实例：

```php
/**
 * 创建一个新的任务实例。
 */
public function __construct(
    Podcast $podcast,
) {
    $this->podcast = $podcast->withoutRelations();
}
```

如果只需要移除特定关联，同时保留其他关联，可以使用 `withoutRelation` 方法：

```php
$this->podcast = $podcast->withoutRelation('comments');
```

如果使用 [PHP 构造函数属性提升](https://www.php.net/manual/en/language.oop5.decon.php#language.oop5.decon.constructor.promotion)，并希望指定某个 Eloquent 模型的关联关系不被序列化，可以使用 `WithoutRelations` 属性：

```php
use Illuminate\Queue\Attributes\WithoutRelations;

/**
 * 创建一个新的任务实例。
 */
public function __construct(
    #[WithoutRelations]
    public Podcast $podcast,
) {}
```

为方便起见，如果希望所有模型都在不包含关联关系的情况下序列化，可以将 `WithoutRelations` 属性应用于整个类，而不必逐个应用于模型：

```php
<?php

namespace App\Jobs;

use App\Models\DistributionPlatform;
use App\Models\Podcast;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\Attributes\WithoutRelations;

#[WithoutRelations]
class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(
        public Podcast $podcast,
        public DistributionPlatform $platform,
    ) {}
}
```

如果任务接收的是 Eloquent 模型集合或数组，而非单个模型，那么任务反序列化并执行时，不会恢复其中模型的关联关系。这是为了避免处理大量模型的任务消耗过多资源。

<a name="unique-jobs"></a>
### 唯一任务

> [!WARNING]
> 唯一任务需要支持[锁](/docs/{{version}}/cache#atomic-locks)的缓存驱动。目前，`memcached`、`redis`、`dynamodb`、`database`、`file` 和 `array` 缓存驱动支持原子锁。

> [!WARNING]
> 唯一任务约束不适用于批次中的任务。

有时，你可能希望确保任意时刻队列中只有某个任务的一个实例。为此，可以让任务类实现 `ShouldBeUnique` 接口。该接口不要求你在类中定义任何额外方法：

```php
<?php

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUnique;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...
}
```

在上例中，`UpdateSearchIndex` 任务是唯一的。因此，如果队列中已有该任务的另一个实例且尚未处理完成，就不会再次分发该任务。

某些情况下，你可能希望通过特定的「键」来确定任务的唯一性，或指定唯一性失效的超时时间。为此，可以使用 `UniqueFor` 属性，并在任务类中定义 `uniqueId` 方法：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Queue\Attributes\UniqueFor;

#[UniqueFor(3600)]
class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    /**
     * 产品实例。
     *
     * @var \App\Models\Product
     */
    public $product;

    /**
     * 获取任务的唯一 ID。
     */
    public function uniqueId(): string
    {
        return $this->product->id;
    }
}
```
在上例中，`UpdateSearchIndex` 任务根据产品 ID 保持唯一。因此，在现有任务处理完成之前，同一产品 ID 的新分发请求都会被忽略。此外，如果现有任务在一小时内仍未被处理，唯一锁会被释放，此时就可以将具有相同唯一键的另一个任务分发到队列。

> [!WARNING]
> 如果应用从多个 Web 服务器或容器分发任务，应确保所有服务器都连接到同一个中央缓存服务器，以便 Laravel 准确判断任务是否唯一。

<a name="keeping-jobs-unique-until-processing-begins"></a>
#### 在开始处理前保持任务唯一

默认情况下，唯一任务在处理完成或所有重试尝试均失败后才会「解锁」。不过，有时你可能希望在任务即将开始处理时就解锁。为此，任务应实现 `ShouldBeUniqueUntilProcessing` 契约，而不是 `ShouldBeUnique` 契约：

```php
<?php

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Contracts\Queue\ShouldBeUniqueUntilProcessing;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUniqueUntilProcessing
{
    // ...
}
```

<a name="unique-job-locks"></a>
#### 唯一任务锁

分发 `ShouldBeUnique` 任务时，Laravel 会尝试以 `uniqueId` 为键获取一个[锁](/docs/{{version}}/cache#atomic-locks)。如果锁已被持有，就不会分发任务。任务处理完成或所有重试尝试均失败后，该锁会被释放。默认情况下，Laravel 使用默认缓存驱动获取锁。如果希望使用其他驱动，可以定义 `uniqueVia` 方法，返回应使用的缓存驱动：

```php
use Illuminate\Contracts\Cache\Repository;
use Illuminate\Support\Facades\Cache;

class UpdateSearchIndex implements ShouldQueue, ShouldBeUnique
{
    // ...

    /**
     * 获取唯一任务锁使用的缓存驱动。
     */
    public function uniqueVia(): Repository
    {
        return Cache::driver('redis');
    }
}
```

> [!NOTE]
> 如果只需要限制任务的并发处理，请改用 [WithoutOverlapping](/docs/{{version}}/queues#preventing-job-overlaps) 任务中间件。

<a name="debounced-jobs"></a>
### 防抖任务

有时，你可能希望同一个任务在短时间内多次分发时，只有最后一次分发真正执行。为此，可以在任务上添加 `DebounceFor` 属性：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\Attributes\DebounceFor;

#[DebounceFor(30)]
class UpdateSearchIndex implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(public int $productId)
    {
    }

    /**
     * 获取任务的防抖 ID。
     */
    public function debounceId(): string
    {
        return (string) $this->productId;
    }
}
```

在上例中，针对同一产品在 `30` 秒内反复分发 `UpdateSearchIndex` 时，会对任务进行防抖处理，只执行最后一次分发的任务。

如果希望限制频繁重复分发的任务最长可被推迟多久，可以为 `DebounceFor` 属性提供 `maxWait` 参数：

```php
#[DebounceFor(30, maxWait: 120)]
class UpdateSearchIndex implements ShouldQueue
{
    use Queueable;

    // ...
}
```

可以通过定义 `debounceVia` 方法，自定义用于跟踪防抖状态的缓存存储：

```php
use Illuminate\Contracts\Cache\Repository;
use Illuminate\Support\Facades\Cache;

public function debounceVia(): Repository
{
    return Cache::driver('redis');
}
```

如果防抖任务被较新的分发所取代，Laravel 会分发 `Illuminate\Queue\Events\JobDebounced` 事件，并从队列中移除被取代的任务。

> [!WARNING]
> 防抖任务与唯一任务互斥。使用 `DebounceFor` 属性的任务不应实现 `ShouldBeUnique`。

> [!WARNING]
> 如果应用从多个 Web 服务器或容器分发防抖任务，应确保所有服务器都连接到同一个中央缓存服务器。

<a name="encrypted-jobs"></a>
### 加密任务

Laravel 允许你通过[加密](/docs/{{version}}/encryption)确保任务数据的隐私与完整性。只需为任务类添加 `ShouldBeEncrypted` 接口，Laravel 就会在将任务推送到队列之前自动加密它：

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

任务中间件允许你在队列任务的执行前后加入自定义逻辑，减少任务本身的样板代码。例如，下面的 `handle` 方法利用 Laravel 的 Redis 限流功能，每五秒只允许处理一个任务：

```php
use Illuminate\Support\Facades\Redis;

/**
 * 执行任务。
 */
public function handle(): void
{
    Redis::throttle('key')->block(0)->allow(1)->every(5)->then(function () {
        info('Lock obtained...');

        // 处理任务...
    }, function () {
        // 无法获取锁...

        return $this->release(5);
    });
}
```

虽然这段代码可以正常工作，但 Redis 限流逻辑使 `handle` 方法变得杂乱，而且其他需要限流的任务也得重复这段逻辑。我们可以将限流逻辑移出 `handle` 方法，改为定义专门处理限流的任务中间件：

```php
<?php

namespace App\Jobs\Middleware;

use Closure;
use Illuminate\Support\Facades\Redis;

class RateLimited
{
    /**
     * 处理队列任务。
     *
     * @param  \Closure(object): void  $next
     */
    public function handle(object $job, Closure $next): void
    {
        Redis::throttle('key')
            ->block(0)->allow(1)->every(5)
            ->then(function () use ($job, $next) {
                // 已获取锁...

                $next($job);
            }, function () use ($job) {
                // 无法获取锁...

                $job->release(5);
            });
    }
}
```

如你所见，与[路由中间件](/docs/{{version}}/middleware)一样，任务中间件接收正在处理的任务，以及用于继续处理任务的回调。

可以使用 `make:job-middleware` Artisan 命令生成任务中间件类。创建后，在任务的 `middleware` 方法中返回中间件，即可将其附加到任务上。`make:job` Artisan 命令生成的任务类不包含这个方法，需要你手动添加：

```php
use App\Jobs\Middleware\RateLimited;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited];
}
```

> [!NOTE]
> 任务中间件也可以分配给[队列事件监听器](/docs/{{version}}/events#queued-event-listeners)、[邮件类](/docs/{{version}}/mail#queueing-mail)和[通知](/docs/{{version}}/notifications#queueing-notifications)。

<a name="rate-limiting"></a>
### 速率限制

虽然刚才演示了如何编写自己的任务限流中间件，但 Laravel 实际上已经内置了可用于任务限流的中间件。与[路由限流器](/docs/{{version}}/routing#defining-rate-limiters)一样，任务限流器通过 `RateLimiter` 门面的 `for` 方法定义。

例如，你可能希望用户每小时只能备份一次数据，而高级用户不受此限制。为此，可以在 `AppServiceProvider` 的 `boot` 方法中定义一个 `RateLimiter`：

```php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Support\Facades\RateLimiter;

/**
 * 引导应用服务。
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

上例定义了按小时计算的速率限制；也可以使用 `perMinute` 方法轻松定义按分钟计算的限制。此外，可以向限流规则的 `by` 方法传入任意值，不过该值通常用于按用户分别限流：

```php
return Limit::perMinute(50)->by($job->user->id);
```

定义速率限制后，可以通过 `Illuminate\Queue\Middleware\RateLimited` 中间件将限流器附加到任务。每当任务超过速率限制时，该中间件都会根据限流周期，以适当的延迟将任务释放回队列：

```php
use Illuminate\Queue\Middleware\RateLimited;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new RateLimited('backups')];
}
```

将被限流的任务释放回队列，仍会增加任务的总 `attempts` 次数。你可能需要相应调整任务类的 `Tries` 和 `MaxExceptions` 属性，或使用 [retryUntil 方法](#time-based-attempts)定义任务的尝试截止时间。

通过 `releaseAfter` 方法，还可以指定释放任务后需等待多少秒才能再次尝试：

```php
/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->releaseAfter(60)];
}
```

如果不希望任务被限流后重试，可以使用 `dontRelease` 方法：

```php
/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new RateLimited('backups'))->dontRelease()];
}
```

<a name="rate-limiting-with-redis"></a>
#### 使用 Redis 限流

如果使用 Redis，可以使用 `Illuminate\Queue\Middleware\RateLimitedWithRedis` 中间件。它针对 Redis 进行了优化，比基础限流中间件更高效：

```php
use Illuminate\Queue\Middleware\RateLimitedWithRedis;

public function middleware(): array
{
    return [new RateLimitedWithRedis('backups')];
}
```

可以使用 `connection` 方法指定中间件应使用的 Redis 连接：

```php
return [(new RateLimitedWithRedis('backups'))->connection('limiter')];
```

<a name="preventing-job-overlaps"></a>
### 防止任务重叠执行

Laravel 内置了 `Illuminate\Queue\Middleware\WithoutOverlapping` 中间件，可以根据任意键防止任务重叠执行。当队列任务修改的资源在同一时刻只能由一个任务修改时，这个中间件很有用。

例如，假设一个队列任务用于更新用户的信用分数，你希望避免同一用户 ID 的信用分数更新任务重叠执行。为此，可以在任务的 `middleware` 方法中返回 `WithoutOverlapping` 中间件：

```php
use Illuminate\Queue\Middleware\WithoutOverlapping;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new WithoutOverlapping($this->user->id)];
}
```

将重叠的任务释放回队列，仍会增加任务的总尝试次数。你可能需要相应调整任务类的 `Tries` 和 `MaxExceptions` 属性。例如，如果 `Tries` 保持默认值 1，任何发生重叠的任务都无法在稍后重试。

同一类型中发生重叠的任务都会被释放回队列。还可以指定释放任务后需等待多少秒才能再次尝试：

```php
/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->releaseAfter(60)];
}
```

如果希望立即删除发生重叠的任务，使其不再重试，可以使用 `dontRelease` 方法：

```php
/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->dontRelease()];
}
```

`WithoutOverlapping` 中间件依赖 Laravel 的原子锁功能。有时，任务意外失败或超时，可能导致锁未被释放。因此，可以使用 `expireAfter` 方法显式定义锁的过期时间。例如，下面的代码会让 Laravel 在任务开始处理三分钟后释放 `WithoutOverlapping` 锁：

```php
/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new WithoutOverlapping($this->order->id))->expireAfter(180)];
}
```

> [!WARNING]
> `WithoutOverlapping` 中间件需要支持[锁](/docs/{{version}}/cache#atomic-locks)的缓存驱动。目前，`memcached`、`redis`、`dynamodb`、`database`、`file` 和 `array` 缓存驱动支持原子锁。

<a name="sharing-lock-keys"></a>
#### 在任务类之间共享锁键

默认情况下，`WithoutOverlapping` 中间件只会防止同一类的任务重叠执行。因此，即使两个不同的任务类使用相同的锁键，它们也不会被阻止重叠执行。不过，可以通过 `shared` 方法让 Laravel 在不同任务类之间应用该锁键：

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

Laravel 内置了 `Illuminate\Queue\Middleware\ThrottlesExceptions` 中间件，可用于异常限流。任务抛出指定次数的异常后，后续执行尝试都会被推迟，直到指定的时间间隔结束。对于与不稳定的第三方服务交互的任务，这个中间件尤其有用。

例如，假设队列任务调用的第三方 API 开始抛出异常。为了限制异常发生的频率，可以在任务的 `middleware` 方法中返回 `ThrottlesExceptions` 中间件。通常，应将它与实现了[基于时间的尝试](#time-based-attempts)的任务配合使用：

```php
use DateTime;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [new ThrottlesExceptions(10, 5 * 60)];
}

/**
 * 确定任务的尝试截止时间。
 */
public function retryUntil(): DateTime
{
    return now()->plus(minutes: 30);
}
```

中间件构造函数的第一个参数是任务被限流前允许抛出的异常次数，第二个参数是限流后再次尝试任务前需要等待的秒数。在上例中，如果任务连续抛出 10 次异常，就会等待 5 分钟再尝试，同时受 30 分钟的总体时间限制。

当任务抛出异常但尚未达到异常阈值时，通常会立即重试。不过，在将中间件附加到任务时，可以调用 `backoff` 方法指定这类任务应延迟的分钟数：

```php
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 5 * 60))->backoff(5)];
}
```

`backoff` 方法也接受一个接收所抛异常的闭包，以便动态确定延迟时间：

```php
use App\Exceptions\RateLimitedException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;
use Throwable;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 5 * 60))->backoff(
        fn (Throwable $throwable) => $throwable instanceof RateLimitedException
            ? $throwable->retryAfterMinutes()
            : 5
    )];
}
```

该中间件在内部使用 Laravel 的缓存系统实现限流，并以任务类名作为缓存「键」。附加中间件时，可以调用 `by` 方法覆盖这个键。如果多个任务与同一第三方服务交互，你可能希望它们共享同一个限流「桶」，共同遵守同一个限制：

```php
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(10, 10 * 60))->by('key')];
}
```

默认情况下，中间件会对所有异常限流。可以在附加中间件时调用 `when` 方法修改这一行为。此时，只有传给 `when` 方法的闭包返回 `true`，才会对该异常限流：

```php
use Illuminate\Http\Client\HttpClientException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
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

`when` 方法会将任务释放回队列或抛出异常，而 `deleteWhen` 方法允许你在指定异常发生时直接删除任务：

```php
use App\Exceptions\CustomerDeletedException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(): array
{
    return [(new ThrottlesExceptions(2, 10 * 60))->deleteWhen(CustomerDeletedException::class)];
}
```

如果希望将被限流的异常报告给应用的异常处理器，可以在附加中间件时调用 `report` 方法。也可以为它提供一个闭包，只有闭包返回 `true` 时才报告异常：

```php
use Illuminate\Http\Client\HttpClientException;
use Illuminate\Queue\Middleware\ThrottlesExceptions;

/**
 * 获取任务应通过的中间件。
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

<a name="throttling-exceptions-with-redis"></a>
#### 使用 Redis 对异常限流

如果使用 Redis，可以使用 `Illuminate\Queue\Middleware\ThrottlesExceptionsWithRedis` 中间件。它针对 Redis 进行了优化，比基础异常限流中间件更高效：

```php
use Illuminate\Queue\Middleware\ThrottlesExceptionsWithRedis;

public function middleware(): array
{
    return [new ThrottlesExceptionsWithRedis(10, 10 * 60)];
}
```

可以使用 `connection` 方法指定中间件应使用的 Redis 连接：

```php
return [(new ThrottlesExceptionsWithRedis(10, 10 * 60))->connection('limiter')];
```

<a name="releasing-jobs"></a>
### 释放任务

`Release` 中间件允许你不执行任务，直接将其释放回队列。当给定条件为 `true` 时，`Release::when` 方法会释放任务；而条件为 `false` 时，`Release::unless` 方法会释放任务：

```php
use Illuminate\Queue\Middleware\Release;

/**
 * 获取任务应通过的中间件。
 */
public function middleware(): array
{
    return [
        Release::when($condition, releaseAfter: 60),
    ];
}
```

将任务释放回队列，仍会增加任务的总尝试次数。你可能需要相应调整任务类的 `Tries` 和 `MaxExceptions` 属性。

还可以向 `when` 和 `unless` 方法传入 `Closure`，进行更复杂的条件判断：

```php
use Illuminate\Queue\Middleware\Release;

/**
 * 获取任务应通过的中间件。
 */
public function middleware(): array
{
    return [
        Release::when(function (): bool {
            return ! $this->order->isPaid();
        }, releaseAfter: 60),
    ];
}
```

<a name="skipping-jobs"></a>
### 跳过任务

`Skip` 中间件允许你在不修改任务逻辑的情况下跳过或删除任务。当给定条件为 `true` 时，`Skip::when` 方法会删除任务；而条件为 `false` 时，`Skip::unless` 方法会删除任务：

```php
use Illuminate\Queue\Middleware\Skip;

/**
 * 获取任务应通过的中间件。
 */
public function middleware(): array
{
    return [
        Skip::when($condition),
    ];
}
```

还可以向 `when` 和 `unless` 方法传入 `Closure`，进行更复杂的条件判断：

```php
use Illuminate\Queue\Middleware\Skip;

/**
 * 获取任务应通过的中间件。
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
## 分发任务

编写好任务类后，可以通过任务自身的 `dispatch` 方法分发它。传给 `dispatch` 方法的参数会传入任务的构造函数：

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
     * 存储一个新的播客。
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

如果希望根据条件分发任务，可以使用 `dispatchIf` 和 `dispatchUnless` 方法：

```php
ProcessPodcast::dispatchIf($accountActive, $podcast);

ProcessPodcast::dispatchUnless($accountSuspended, $podcast);
```

在新的 Laravel 应用中，`database` 连接被定义为默认队列连接。可以修改应用 `.env` 文件中的 `QUEUE_CONNECTION` 环境变量来指定其他默认队列连接。

<a name="delayed-dispatching"></a>
### 延迟分发

如果希望任务暂时不能被队列工作进程处理，可以在分发时使用 `delay` 方法。例如，下面指定任务在分发 10 分钟后才能被处理：

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
     * 存储一个新的播客。
     */
    public function store(Request $request): RedirectResponse
    {
        $podcast = Podcast::create(/* ... */);

        // ...

        ProcessPodcast::dispatch($podcast)
            ->delay(now()->plus(minutes: 10));

        return redirect('/podcasts');
    }
}
```

某些任务可能配置了默认延迟。如果需要绕过此延迟，分发一个可立即处理的任务，可以使用 `withoutDelay` 方法：

```php
ProcessPodcast::dispatch($podcast)->withoutDelay();
```

> [!WARNING]
> Amazon SQS 队列服务允许的最大延迟时间为 15 分钟。

<a name="synchronous-dispatching"></a>
### 同步分发

如果希望立即（同步）分发任务，可以使用 `dispatchSync` 方法。该方法不会将任务加入队列，而是立即在当前进程中执行：

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
     * 存储一个新的播客。
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

<a name="deferred-dispatching"></a>
#### 推迟分发

使用推迟的同步分发，可以让任务在 HTTP 响应发送给用户之后，仍由当前进程处理。这样便能同步处理「队列」任务，而不会让用户感觉应用变慢。要推迟同步任务的执行，请将其分发到 `deferred` 连接：

```php
RecordDelivery::dispatch($order)->onConnection('deferred');
```

`deferred` 连接也是默认的[故障转移队列](#queue-failover)。

类似地，`background` 连接也会在 HTTP 响应发送给用户之后处理任务；不过，任务是在另外启动的 PHP 进程中处理的，因此 PHP-FPM / 应用工作进程可以继续处理其他传入的 HTTP 请求：

```php
RecordDelivery::dispatch($order)->onConnection('background');
```

<a name="bulk-dispatching"></a>
### 批量分发

如果需要一次分发大量独立任务，而不需要[批次](#job-batching)跟踪或回调，可以使用 `Bus` 门面的 `bulk` 方法。Laravel 会按任务配置的队列连接与队列名称分组，再将每组任务批量推送到对应队列：

```php
use App\Jobs\ProcessUser;
use Illuminate\Support\Facades\Bus;

Bus::bulk(
    $users->map(fn ($user) => new ProcessUser($user))
);
```

<a name="preparing-jobs-before-dispatch"></a>
### 分发前准备任务

如果任务需要在推送到队列之前准备或检查自身状态，可以实现 `Illuminate\Contracts\Queue\PreparesForDispatch` 接口。Laravel 会在分发前调用任务的 `prepareForDispatch` 方法。如果该方法返回 `false`，任务就不会被分发：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\PreparesForDispatch;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Cache;

class SyncPodcasts implements PreparesForDispatch, ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(
        public array $podcastIds,
    ) {}

    /**
     * 在分发之前准备任务。
     */
    public function prepareForDispatch(): bool
    {
        return collect($this->podcastIds)
            ->reject(fn (int $id) => Cache::has("podcast-syncing:{$id}"))
            ->isNotEmpty();
    }
}
```

<a name="jobs-and-database-transactions"></a>
### 任务与数据库事务

在数据库事务中分发任务完全可行，但需要特别注意，确保任务能够成功执行。在事务中分发任务时，工作进程可能会在外层事务提交之前就开始处理任务。此时，事务中对模型或数据库记录的更新可能尚未反映到数据库中，而事务中新建的模型或记录也可能尚不存在于数据库中。

好在 Laravel 提供了几种解决办法。首先，可以在队列连接的配置数组中设置 `after_commit` 选项：

```php
'redis' => [
    'driver' => 'redis',
    // ...
    'after_commit' => true,
],
```

当 `after_commit` 选项为 `true` 时，可以在数据库事务中分发任务，但 Laravel 会等到尚未结束的外层数据库事务提交后，才真正分发任务。当然，如果当前没有未结束的数据库事务，任务就会立即分发。

如果事务因执行过程中发生的异常而回滚，该事务中分发的任务也会被丢弃。

> [!NOTE]
> 将 `after_commit` 配置选项设为 `true` 后，队列事件监听器、邮件、通知及广播事件也会等到所有未结束的数据库事务提交后才分发。

<a name="specifying-commit-dispatch-behavior-inline"></a>
#### 在分发时指定事务提交行为

即使没有将队列连接的 `after_commit` 配置选项设为 `true`，仍然可以指定某个任务在所有未结束的数据库事务提交后才分发。为此，请在分发操作后链式调用 `afterCommit` 方法：

```php
use App\Jobs\ProcessPodcast;

ProcessPodcast::dispatch($podcast)->afterCommit();
```

同样，如果 `after_commit` 配置选项已设为 `true`，也可以指定某个任务立即分发，而不等待未结束的数据库事务提交：

```php
ProcessPodcast::dispatch($podcast)->beforeCommit();
```

<a name="job-chaining"></a>
### 任务链

任务链允许你指定一组队列任务，在首个任务成功执行后依次运行。如果其中一个任务失败，剩余任务就不会运行。要执行队列任务链，可以使用 `Bus` 门面提供的 `chain` 方法。Laravel 的命令总线是队列任务分发所依赖的底层组件：

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

除了任务类实例，还可以将闭包加入任务链：

```php
Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    function () {
        Podcast::update(/* ... */);
    },
])->dispatch();
```

> [!WARNING]
> 在任务中使用 `$this->delete()` 删除任务，不会阻止后续链式任务被处理。只有任务链中的任务失败，才会停止执行任务链。

<a name="chain-connection-queue"></a>
#### 任务链的连接与队列

如果希望指定链式任务使用的连接与队列，可以使用 `onConnection` 和 `onQueue` 方法。除非某个任务被显式分配了其他连接或队列，否则会使用这些方法指定的队列连接和队列名称：

```php
Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->onConnection('redis')->onQueue('podcasts')->dispatch();
```

<a name="adding-jobs-to-the-chain"></a>
#### 向任务链添加任务

有时，你可能需要在任务链中的某个任务里，向现有任务链的开头或末尾添加任务。可以使用 `prependToChain` 和 `appendToChain` 方法：

```php
/**
 * 执行任务。
 */
public function handle(): void
{
    // ...

    // 添加到当前任务链的开头，在当前任务之后立即运行...
    $this->prependToChain(new TranscribePodcast);

    // 添加到当前任务链的末尾，在任务链末尾运行...
    $this->appendToChain(new TranscribePodcast);
}
```

<a name="chain-failures"></a>
#### 任务链失败

定义任务链时，可以使用 `catch` 方法指定一个在链中任务失败时调用的闭包。该回调会接收导致任务失败的 `Throwable` 实例：

```php
use Illuminate\Support\Facades\Bus;
use Throwable;

Bus::chain([
    new ProcessPodcast,
    new OptimizePodcast,
    new ReleasePodcast,
])->catch(function (Throwable $e) {
    // 任务链中的一个任务已失败...
})->dispatch();
```

> [!WARNING]
> 任务链回调会被序列化，并在稍后由 Laravel 队列执行，因此不应在回调中使用 `$this` 变量。

<a name="customizing-the-queue-and-connection"></a>
### 自定义队列与连接

<a name="dispatching-to-a-particular-queue"></a>
#### 分发到特定队列

通过将任务推送到不同队列，可以对队列任务进行「分类」，甚至决定为各个队列优先分配多少个工作进程。请注意，这并不是将任务推送到队列配置文件中定义的不同「连接」，而是推送到同一个连接中的特定队列。要指定队列，请在分发任务时使用 `onQueue` 方法：

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
     * 存储一个新的播客。
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

也可以在任务的构造函数中调用 `onQueue` 方法，指定任务的队列：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct()
    {
        $this->onQueue('processing');
    }
}
```

<a name="dispatching-to-a-particular-connection"></a>
#### 分发到特定连接

如果应用与多个队列连接交互，可以使用 `onConnection` 方法指定任务应推送到的连接：

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
     * 存储一个新的播客。
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

可以链式调用 `onConnection` 和 `onQueue` 方法，同时指定任务的连接与队列：

```php
ProcessPodcast::dispatch($podcast)
    ->onConnection('sqs')
    ->onQueue('processing');
```

也可以在任务的构造函数中调用 `onConnection` 方法，指定任务的连接：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct()
    {
        $this->onConnection('sqs');
    }
}
```

<a name="queue-routing"></a>
#### 队列路由

可以使用 `Queue` 门面的 `route` 方法为特定任务类定义默认连接与队列。当你希望某些任务始终使用特定队列，而不必在任务中指定连接或队列时，这很有用。

除了具体任务类，还可以向 `route` 方法传入接口、trait 或父类。此时，所有实现该接口、使用该 trait 或继承该父类的任务，都会自动使用配置的连接与队列。

通常，应在服务提供者的 `boot` 方法中调用 `route` 方法：

```php
use App\Concerns\RequiresVideo;
use App\Jobs\ProcessPodcast;
use App\Jobs\ProcessVideo;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Support\Facades\Queue;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Queue::route(ProcessPodcast::class, connection: 'redis', queue: 'podcasts');
    Queue::route(RequiresVideo::class, queue: 'video');
    Queue::route(ShouldBroadcast::class, queue: 'events');
}
```

如果只指定连接而没有指定队列，任务会发送到默认队列：

```php
Queue::route(ProcessPodcast::class, connection: 'redis');
```

还可以向 `route` 方法传入数组，一次为多个任务类配置路由：

```php
Queue::route([
    ProcessPodcast::class => ['redis', 'podcasts'], // 连接与队列
    ProcessVideo::class => 'videos', // 仅指定队列（使用默认连接）
]);
```

> [!NOTE]
> 任务仍可逐个覆盖队列路由配置。

可以使用 `forward` 方法将任务从一个队列转发到另一个队列和 / 或连接。如果需要更换队列基础设施，又不想修改各个任务或分发位置，这很有用：

```php
Queue::forward('reports', 'reports.fifo', 'sqs');
Queue::forward('payments', connection: 'sqs');
Queue::forward('updates', 'notifications');
```

还可以传入数组，一次转发多个队列：

```php
Queue::forward([
    'reports' => 'reports.fifo',
    'emails' => 'emails.fifo',
], connection: 'sqs');
```

任务中显式配置的连接优先于转发指定的连接。

<a name="max-job-attempts-and-timeout"></a>
### 指定任务的最大尝试次数与超时时间

<a name="max-attempts"></a>
#### 最大尝试次数

任务尝试是 Laravel 队列系统的核心概念，也是许多高级功能的基础。虽然初看可能有些难懂，但在修改默认配置之前，理解它的工作方式很重要。

分发任务时，它会被推送到队列。随后工作进程取出任务并尝试执行，这就是一次任务尝试。

不过，一次尝试不一定意味着任务的 `handle` 方法已经执行。以下情况也会「消耗」尝试次数：

<div class="content-list" markdown="1">

- 任务在执行过程中遇到未处理的异常。
- 通过 `$this->release()` 手动将任务释放回队列。
- `WithoutOverlapping` 或 `RateLimited` 等中间件未能获取锁，并释放了任务。
- 任务超时。
- 任务的 `handle` 方法运行并完成，且未抛出异常。

</div>

你通常不会希望无限尝试一个任务。因此，Laravel 提供了多种方式来指定任务可尝试的次数或持续时间。

> [!NOTE]
> 默认情况下，Laravel 只会尝试任务一次。如果任务使用 `WithoutOverlapping` 或 `RateLimited` 等中间件，或者你手动释放任务，通常需要通过 `tries` 选项增加允许的尝试次数。

一种指定任务最大尝试次数的方式，是使用 Artisan 命令行的 `--tries` 选项。该值适用于工作进程处理的所有任务，除非任务自身指定了可尝试的次数：

```shell
php artisan queue:work --tries=3
```

任务超过最大尝试次数后，会被视为「失败」任务。更多信息请参阅[失败任务文档](#dealing-with-failed-jobs)。如果为 `queue:work` 命令提供 `--tries=0`，任务将无限重试。

也可以使用更精细的方式，通过任务类的 `Tries` 属性定义其最大尝试次数。任务自身指定的最大尝试次数优先于命令行提供的 `--tries` 值：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\Tries;

#[Tries(5)]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

如果需要动态控制某个任务的最大尝试次数，可以在任务中定义 `tries` 方法：

```php
/**
 * 确定任务可尝试的次数。
 */
public function tries(): int
{
    return 5;
}
```

<a name="time-based-attempts"></a>
#### 基于时间的尝试

除了定义任务失败前可尝试的次数，还可以定义不再尝试任务的截止时间。这样便能在给定时间内不限次数地尝试任务。要定义截止时间，请在任务类中添加 `retryUntil` 方法，并让它返回 `DateTime` 实例：

```php
use DateTime;

/**
 * 确定任务的尝试截止时间。
 */
public function retryUntil(): DateTime
{
    return now()->plus(minutes: 10);
}
```

如果同时定义 `retryUntil` 和 `tries`，Laravel 会优先使用 `retryUntil` 方法。

> [!NOTE]
> 也可以在[队列事件监听器](/docs/{{version}}/events#queued-event-listeners)和[队列通知](/docs/{{version}}/notifications#queueing-notifications)中定义 `Tries` 属性或 `retryUntil` 方法。

<a name="max-exceptions"></a>
#### 最大异常数

有时，你可能希望允许任务多次尝试，但在因未处理的异常触发重试达到指定次数时，就将任务标记为失败（而非直接通过 `release` 方法释放任务的情况）。为此，可以在任务类中使用 `Tries` 和 `MaxExceptions` 属性：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\Attributes\MaxExceptions;
use Illuminate\Queue\Attributes\Tries;
use Illuminate\Support\Facades\Redis;

#[Tries(25)]
#[MaxExceptions(3)]
class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    /**
     * 执行任务。
     */
    public function handle(): void
    {
        Redis::throttle('key')->allow(10)->every(60)->then(function () {
            // 已获取锁，处理播客...
        }, function () {
            // 无法获取锁...
            return $this->release(10);
        });
    }
}
```

在这个示例中，如果应用无法获取 Redis 锁，任务会被释放并延迟十秒，然后继续重试，最多尝试 25 次。不过，如果任务抛出三个未处理的异常，就会失败。

默认情况下，因工作进程崩溃或被终止而结束的尝试（例如内存耗尽），不会计入任务的最大异常数。如果希望将这些尝试计为异常，可以为任务类添加 `CountCrashesAsExceptions` 属性：

```php
use Illuminate\Queue\Attributes\CountCrashesAsExceptions;
use Illuminate\Queue\Attributes\MaxExceptions;
use Illuminate\Queue\Attributes\Tries;

#[Tries(25)]
#[MaxExceptions(3)]
#[CountCrashesAsExceptions]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

使用此属性后，工作进程会在处理任务时向应用缓存中写入一个标记。如果下次尝试任务时该标记仍然存在，上一次尝试就会被计为异常。

<a name="stopping-retries-by-exception"></a>
#### 遇到特定异常时停止重试

有时，异常意味着队列任务应立即失败，而不是被释放以供再次尝试。可以在应用的 `bootstrap/app.php` 文件中，通过异常配置的 `dontRetry` 方法指定遇到哪些异常类型时应停止重试任务：

```php
use App\Exceptions\InvalidPodcastSourceException;
use Illuminate\Foundation\Configuration\Exceptions;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontRetry([
        InvalidPodcastSourceException::class,
    ]);
})
```

如果需要更精细地控制何时停止重试，可以向 `dontRetryWhen` 方法提供闭包。闭包返回 `true` 时，任务会被标记为失败，且不再重试：

```php
use App\Exceptions\PodcastProcessingException;
use Illuminate\Foundation\Configuration\Exceptions;

->withExceptions(function (Exceptions $exceptions): void {
    $exceptions->dontRetryWhen(function (PodcastProcessingException $e) {
        return $e->reason() === 'Subscription expired';
    });
})
```

<a name="timeout"></a>
#### 超时

通常，你大致知道队列任务需要运行多久。因此，Laravel 允许指定「超时」值，默认是 60 秒。如果任务处理时间超过指定的秒数，处理任务的工作进程会以错误状态退出。通常，[服务器上配置的进程管理器](#supervisor-configuration)会自动重启该进程。

可以通过 Artisan 命令行的 `--timeout` 选项指定任务允许运行的最大秒数：

```shell
php artisan queue:work --timeout=30
```

如果任务因不断超时而超过最大尝试次数，就会被标记为失败。

也可以通过任务类的 `Timeout` 属性定义任务允许运行的最大秒数。任务自身指定的超时时间优先于命令行指定的任何超时时间：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\Timeout;

#[Timeout(120)]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

有时，套接字或对外 HTTP 连接等阻塞 I/O 操作可能不遵守你指定的超时时间。因此，使用这些功能时，还应尽量通过它们自身的 API 指定超时时间。例如，使用 [Guzzle](https://docs.guzzlephp.org) 时，应始终指定连接超时和请求超时。

> [!WARNING]
> 必须安装 PHP 的 [PCNTL](https://www.php.net/manual/en/book.pcntl.php) 扩展才能指定任务超时时间。此外，任务的「超时」值应始终小于其[「重试等待时间」](#job-expiration)。否则，任务可能在实际执行完成或超时之前就被再次尝试。使用 `--once` 选项调用 `queue:work` 命令时，`--timeout` 选项无效。

<a name="failing-on-timeout"></a>
#### 超时即失败

如果希望任务在超时时被标记为[失败](#dealing-with-failed-jobs)，可以在任务类中使用 `FailOnTimeout` 属性：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\FailOnTimeout;

#[FailOnTimeout]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

> [!NOTE]
> 默认情况下，任务超时会消耗一次尝试次数，并被释放回队列（如果允许重试）。不过，如果将任务配置为超时即失败，就不会再重试，而不论 tries 的设置值是多少。

<a name="sqs-fifo-and-fair-queues"></a>
### SQS FIFO 队列与公平队列

Laravel 支持 [Amazon SQS FIFO（先进先出）](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fifo-queues.html)队列与[公平](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues.html)队列。FIFO 队列允许你严格按发送顺序处理任务，并通过消息去重确保恰好处理一次。

FIFO 队列需要消息组 ID 来确定哪些任务可以并行处理。相同组 ID 的任务会按顺序处理，而不同组 ID 的消息可以并发处理。

Laravel 提供了可链式调用的 `onGroup` 方法，供你在分发任务时指定消息组 ID：

```php
ProcessOrder::dispatch($order)
    ->onGroup("customer-{$order->customer_id}");
```

如果将任务分发到 SQS FIFO 队列时未指定消息组，Laravel 会使用队列名称作为消息组 ID。

SQS FIFO 队列支持消息去重，以确保恰好处理一次。在任务类中实现 `deduplicationId` 方法，可以提供自定义的去重 ID：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessSubscriptionRenewal implements ShouldQueue
{
    use Queueable;

    // ...

    /**
     * 获取任务的去重 ID。
     */
    public function deduplicationId(): string
    {
        return "renewal-{$this->subscription->id}";
    }
}
```

<a name="fair-queues"></a>
#### 公平队列

如果使用 SQS 标准队列，设置消息组就会启用公平排队。换句话说，分配组之后，SQS 会利用这些组在不同租户或工作负载之间保持公平的消息投递，无需额外的 Laravel 配置。

除了在分发时调用 `onGroup`，还可以直接在任务中定义 `messageGroup` 方法：

```php
<?php

namespace App\Jobs;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessOrder implements ShouldQueue
{
    use Queueable;

    // ...

    /**
     * 获取任务的消息组。
     */
    public function messageGroup(): string
    {
        return "customer-{$this->order->customer_id}";
    }
}
```

<a name="fifo-listeners-mail-and-notifications"></a>
#### FIFO 监听器、邮件与通知

使用 FIFO 队列时，还需要为监听器、邮件和通知定义消息组。也可以将这些对象的队列实例分发到非 FIFO 队列。

要为[队列事件监听器](/docs/{{version}}/events#queued-event-listeners)定义消息组，请在监听器中定义 `messageGroup` 方法。也可以定义一个可选的 `deduplicator` 方法，它接收事件，并应返回一个生成去重 ID 的闭包：

```php
<?php

namespace App\Listeners;

use App\Events\OrderShipped;
use Closure;

class SendShipmentNotification
{
    // ...

    /**
     * 获取任务的消息组。
     */
    public function messageGroup(): string
    {
        return 'shipments';
    }

    /**
     * 获取任务的去重器。
     */
    public function deduplicator(OrderShipped $event): Closure
    {
        return fn () => "shipment-notification-{$event->order->id}";
    }
}
```

发送将加入 FIFO 队列的[邮件](/docs/{{version}}/mail)时，应调用 `onGroup` 方法，并可选择调用 `withDeduplicator` 方法：

```php
use App\Mail\InvoicePaid;
use Illuminate\Support\Facades\Mail;

$invoicePaid = (new InvoicePaid($invoice))
    ->onGroup('invoices')
    ->withDeduplicator(fn () => 'invoices-'.$invoice->id);

Mail::to($request->user())->send($invoicePaid);
```

发送将加入 FIFO 队列的[通知](/docs/{{version}}/notifications)时，应调用 `onGroup` 方法，并可选择调用 `withDeduplicator` 方法：

```php
use App\Notifications\InvoicePaid;

$invoicePaid = (new InvoicePaid($invoice))
    ->onGroup('invoices')
    ->withDeduplicator(fn () => 'invoices-'.$invoice->id);

$user->notify($invoicePaid);
```

<a name="queue-failover"></a>
### 队列故障转移

`failover` 队列驱动在推送任务时提供自动故障转移功能。如果故障转移配置中的主队列连接因任何原因失败，Laravel 会自动尝试将任务推送到列表中的下一个连接。这对于队列可靠性至关重要的生产环境尤其有用，有助于确保高可用性。

要配置故障转移队列连接，请指定 `failover` 驱动，并提供一个按尝试顺序排列的连接名称数组。默认情况下，Laravel 已在应用的 `config/queue.php` 配置文件中提供了故障转移配置示例：

```php
'failover' => [
    'driver' => 'failover',
    'connections' => [
        'redis',
        'database',
        'sync',
    ],
],
```

配置好使用 `failover` 驱动的连接后，需要在应用的 `.env` 文件中将其设为默认队列连接，才能使用故障转移功能：

```ini
QUEUE_CONNECTION=failover
```

接着，为故障转移连接列表中的每个连接至少启动一个工作进程：

```shell
php artisan queue:work redis
php artisan queue:work database
```

> [!NOTE]
> 使用 `sync`、`background` 或 `deferred` 队列驱动的连接不需要运行工作进程，因为这些驱动会在当前 PHP 进程内处理任务。

队列连接操作失败并触发故障转移时，Laravel 会分发 `Illuminate\Queue\Events\QueueFailedOver` 事件，以便你报告或记录队列连接失败的情况。

> [!NOTE]
> 如果使用 Laravel Horizon，请记住 Horizon 仅管理 Redis 队列。如果故障转移列表包含 `database`，应在运行 Horizon 的同时运行常规的 `php artisan queue:work database` 进程。

<a name="error-handling"></a>
### 错误处理

处理任务时如果抛出异常，任务会自动释放回队列，以供再次尝试。任务会不断被释放，直到达到应用允许的最大尝试次数。可以通过 `queue:work` Artisan 命令的 `--tries` 选项定义最大尝试次数，也可以在任务类自身定义。更多运行队列工作进程的信息[见下文](#running-the-queue-worker)。

<a name="manually-releasing-a-job"></a>
#### 手动释放任务

有时，你可能希望手动将任务释放回队列，稍后再次尝试。可以调用 `release` 方法：

```php
/**
 * 执行任务。
 */
public function handle(): void
{
    // ...

    $this->release();
}
```

默认情况下，`release` 方法会将任务释放回队列，使其可立即处理。不过，可以传入整数或日期实例，指定经过一定秒数后才允许再次处理任务：

```php
$this->release(10);

$this->release(now()->plus(seconds: 10));
```

<a name="manually-failing-a-job"></a>
#### 手动将任务标记为失败

有时，你可能需要手动将任务标记为「失败」。为此，可以调用 `fail` 方法：

```php
/**
 * 执行任务。
 */
public function handle(): void
{
    // ...

    $this->fail();
}
```

如果希望因捕获的异常而将任务标记为失败，可以将异常传给 `fail` 方法。为方便起见，也可以传入错误消息字符串，Laravel 会将其转换为异常：

```php
$this->fail($exception);

$this->fail('Something went wrong.');
```

> [!NOTE]
> 更多信息请参阅[处理失败任务的文档](#dealing-with-failed-jobs)。

<a name="fail-jobs-on-exceptions"></a>
#### 遇到特定异常时将任务标记为失败

`FailOnException` [任务中间件](#job-middleware)允许你在抛出指定异常时停止重试。这样，遇到外部 API 错误等暂时性异常时仍可重试，而遇到用户权限被撤销等持续性异常时，则永久将任务标记为失败：

```php
<?php

namespace App\Jobs;

use App\Models\User;
use Illuminate\Auth\Access\AuthorizationException;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Queue\Attributes\Tries;
use Illuminate\Queue\Middleware\FailOnException;
use Illuminate\Support\Facades\Http;

#[Tries(3)]
class SyncChatHistory implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(
        public User $user,
    ) {}

    /**
     * 执行任务。
     */
    public function handle(): void
    {
        $this->user->authorize('sync-chat-history');

        $response = Http::throw()->get(
            "https://chat.laravel.test/?user={$this->user->uuid}"
        );

        // ...
    }

    /**
     * 获取任务应通过的中间件。
     */
    public function middleware(): array
    {
        return [
            new FailOnException([AuthorizationException::class])
        ];
    }
}
```

<a name="job-batching"></a>
## 任务批处理

Laravel 的任务批处理功能让你能够轻松并行执行一组任务，并在整个批次完成后执行某些操作。

开始之前，应创建数据库迁移，建立一个存放任务批次元信息（例如完成百分比）的表。可以使用 `make:queue-batches-table` Artisan 命令生成迁移：

```shell
php artisan make:queue-batches-table

php artisan migrate
```

<a name="defining-batchable-jobs"></a>
### 定义可批处理的任务

要定义可批处理的任务，请按常规方式[创建队列任务](#creating-jobs)，并为任务类添加 `Illuminate\Bus\Batchable` trait。该 trait 提供的 `batch` 方法可用于获取任务当前所属的批次：

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
     * 执行任务。
     */
    public function handle(): void
    {
        if ($this->batch()->cancelled()) {
            // 判断批次是否已取消...

            return;
        }

        // 导入 CSV 文件的一部分...
    }
}
```

<a name="dispatching-batches"></a>
### 分发批次

要分发一批任务，应使用 `Bus` 门面的 `batch` 方法。批处理通常需要结合完成回调才能发挥作用，因此可以通过 `then`、`catch` 和 `finally` 方法为批次定义完成回调。每个回调在调用时都会接收一个 `Illuminate\Bus\Batch` 实例。

运行多个队列工作进程时，批次中的任务会并行处理。因此，任务完成的顺序可能不同于加入批次的顺序。有关如何按顺序运行一组任务，请参阅[任务链与批次](#chains-and-batches)文档。

在这个示例中，假设我们将一批任务加入队列，每个任务负责处理 CSV 文件中一定数量的行：

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
    // 批次已创建，但尚未添加任务...
})->progress(function (Batch $batch) {
    // 单个任务已成功完成...
})->then(function (Batch $batch) {
    // 所有任务已成功完成...
})->catch(function (Batch $batch, Throwable $e) {
    // 检测到批次任务失败...
})->finally(function (Batch $batch) {
    // 批次已执行完毕...
})->dispatch();

return $batch->id;
```

可以通过 `$batch->id` 属性访问批次 ID，并在分发后使用该 ID [查询 Laravel 命令总线](#inspecting-batches)，获取批次信息。

> [!WARNING]
> 批次回调会被序列化，并在稍后由 Laravel 队列执行，因此不应在回调中使用 `$this` 变量。此外，批次任务会被包裹在数据库事务中，因此不应在任务中执行触发隐式提交的数据库语句。

<a name="naming-batches"></a>
#### 命名批次

对于已命名的批次，[Laravel Horizon](/docs/{{version}}/horizon) 和 [Laravel Telescope](/docs/{{version}}/telescope) 等工具会提供更友好的调试信息。要为批次指定名称，可以在定义批次时调用 `name` 方法：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务已成功完成...
})->name('Import CSV')->dispatch();
```

<a name="batch-connection-queue"></a>
#### 批次的连接与队列

如果希望指定批次任务使用的连接与队列，可以使用 `onConnection` 和 `onQueue` 方法。同一批次中的所有任务必须在同一个连接和队列中执行：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务已成功完成...
})->onConnection('redis')->onQueue('imports')->dispatch();
```

<a name="chains-and-batches"></a>
### 任务链与批次

将[链式任务](#job-chaining)放入数组，即可在批次中定义任务链。例如，可以并行执行两个任务链，并在两个任务链都处理完成后执行回调：

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
    // 所有任务已成功完成...
})->dispatch();
```

反过来，也可以在[任务链](#job-chaining)中定义并运行任务批次。例如，先运行一批发布多个播客的任务，再运行一批发送发布通知的任务：

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
### 向批次添加任务

有时，在批次中的某个任务内向该批次添加更多任务会很有用。例如，需要批处理数千个任务时，在 Web 请求期间分发所有任务可能耗时过长。因此，可以先分发一批「加载器」任务，再由它们向批次中填充更多任务：

```php
$batch = Bus::batch([
    new LoadImportBatch,
    new LoadImportBatch,
    new LoadImportBatch,
])->then(function (Batch $batch) {
    // 所有任务已成功完成...
})->name('Import Contacts')->dispatch();
```

在这个示例中，我们使用 `LoadImportBatch` 任务向批次添加更多任务。为此，可以通过任务的 `batch` 方法获取批次实例，再调用它的 `add` 方法：

```php
use App\Jobs\ImportContacts;
use Illuminate\Support\Collection;

/**
 * 执行任务。
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

> [!WARNING]
> 只能在属于同一批次的任务中，向该批次添加任务。

<a name="inspecting-batches"></a>
### 检查批次

传给批次完成回调的 `Illuminate\Bus\Batch` 实例提供了多种属性和方法，可用于与批次交互及检查批次：

```php
// 批次的 UUID...
$batch->id;

// 批次的名称（如果已设置）...
$batch->name;

// 分配给批次的任务数量...
$batch->totalJobs;

// 尚未被队列处理的任务数量...
$batch->pendingJobs;

// 失败的任务数量...
$batch->failedJobs;

// 截至目前已处理的任务数量...
$batch->processedJobs();

// 批次的完成百分比（0-100）...
$batch->progress();

// 表示批次是否已执行完毕...
$batch->finished();

// 取消批次的执行...
$batch->cancel();

// 表示批次是否已取消...
$batch->cancelled();
```

<a name="returning-batches-from-routes"></a>
#### 从路由返回批次

所有 `Illuminate\Bus\Batch` 实例都可以序列化为 JSON，因此可以直接从应用的路由返回它们，获取包含批次信息及完成进度的 JSON 载荷。这样便能方便地在应用界面中显示批次的完成进度。

要通过 ID 获取批次，可以使用 `Bus` 门面的 `findBatch` 方法：

```php
use Illuminate\Support\Facades\Bus;
use Illuminate\Support\Facades\Route;

Route::get('/batch/{batchId}', function (string $batchId) {
    return Bus::findBatch($batchId);
});
```

<a name="cancelling-batches"></a>
### 取消批次

有时，你可能需要取消某个批次的执行。可以调用 `Illuminate\Bus\Batch` 实例的 `cancel` 方法：

```php
/**
 * 执行任务。
 */
public function handle(): void
{
    if ($this->user->exceedsImportLimit()) {
        $this->batch()->cancel();

        return;
    }

    if ($this->batch()->cancelled()) {
        return;
    }
}
```

正如之前的示例所示，批次任务通常应先判断其所属批次是否已取消，再继续执行。为方便起见，也可以为任务分配 `SkipIfBatchCancelled` [中间件](#job-middleware)。顾名思义，该中间件会在任务所属批次已取消时，指示 Laravel 不处理该任务：

```php
use Illuminate\Queue\Middleware\SkipIfBatchCancelled;

/**
 * 获取任务应通过的中间件。
 */
public function middleware(): array
{
    return [new SkipIfBatchCancelled];
}
```

<a name="batch-failures"></a>
### 批次失败

批次任务失败时，会调用 `catch` 回调（如果已定义）。这个回调只会针对批次中第一个失败的任务调用。

<a name="allowing-failures"></a>
#### 允许失败

当批次中的任务失败时，Laravel 会自动将批次标记为「已取消」。如果需要，可以禁用该行为，避免任务失败时自动取消批次。为此，请在分发批次时调用 `allowFailures` 方法：

```php
$batch = Bus::batch([
    // ...
])->then(function (Batch $batch) {
    // 所有任务已成功完成...
})->allowFailures()->dispatch();
```

还可以向 `allowFailures` 方法提供一个可选闭包，它会在每次任务失败时执行：

```php
$batch = Bus::batch([
    // ...
])->allowFailures(function (Batch $batch, $exception) {
    // 处理单个任务的失败...
})->dispatch();
```

<a name="retrying-failed-batch-jobs"></a>
#### 重试批次中失败的任务

为方便起见，Laravel 提供了 `queue:retry-batch` Artisan 命令，供你轻松重试指定批次中所有失败的任务。该命令接收需要重试其失败任务的批次 UUID：

```shell
php artisan queue:retry-batch 32dbc76c-4f82-4749-b610-a639fe0099b5
```

<a name="pruning-batches"></a>
### 清理批次

如果不清理，`job_batches` 表会很快积累大量记录。为避免这种情况，应[调度](/docs/{{version}}/scheduling) `queue:prune-batches` Artisan 命令每天运行：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches')->daily();
```

默认情况下，所有完成超过 24 小时的批次都会被清理。可以在调用命令时使用 `hours` 选项指定批次数据的保留时长。例如，以下命令会删除所有完成超过 48 小时的批次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48')->daily();
```

有时，`job_batches` 表会积累从未成功完成的批次记录，例如某个任务失败后一直未成功重试的批次。可以通过 `unfinished` 选项让 `queue:prune-batches` 命令清理这些未完成的批次记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48 --unfinished=72')->daily();
```

同样，`job_batches` 表也可能积累已取消批次的记录。可以通过 `cancelled` 选项让 `queue:prune-batches` 命令清理这些记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('queue:prune-batches --hours=48 --cancelled=72')->daily();
```

<a name="storing-batches-in-dynamodb"></a>
### 在 DynamoDB 中存储批次

Laravel 也支持将批次元信息存储在 [DynamoDB](https://aws.amazon.com/dynamodb) 中，而不是关系型数据库。不过，需要手动创建 DynamoDB 表来存放所有批次记录。

通常，该表应命名为 `job_batches`，但具体名称应与应用 `queue` 配置文件中的 `queue.batching.table` 配置值一致。

<a name="dynamodb-batch-table-configuration"></a>
#### DynamoDB 批次表配置

`job_batches` 表应具有名为 `application` 的字符串主分区键，以及名为 `id` 的字符串主排序键。键中的 `application` 部分会包含应用名称，该名称由应用 `app` 配置文件中的 `name` 配置值定义。由于应用名称是 DynamoDB 表键的一部分，因此可以用同一张表存储多个 Laravel 应用的任务批次。

此外，如果希望使用[自动批次清理](#pruning-batches-in-dynamodb)，可以为表定义 `ttl` 属性。

<a name="dynamodb-configuration"></a>
#### DynamoDB 配置

接着，安装 AWS SDK，以便 Laravel 应用与 Amazon DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

然后，将 `queue.batching.driver` 配置选项设为 `dynamodb`。还应在 `batching` 配置数组中定义 `key`、`secret` 和 `region` 选项，用于向 AWS 进行身份验证。使用 `dynamodb` 驱动时，不需要 `queue.batching.database` 配置选项：

```php
'batching' => [
    'driver' => env('QUEUE_BATCHING_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'job_batches',
],
```

<a name="pruning-batches-in-dynamodb"></a>
#### 清理 DynamoDB 中的批次

使用 [DynamoDB](https://aws.amazon.com/dynamodb) 存储任务批次信息时，通常用于清理关系型数据库批次的命令不再适用。此时，可以使用 [DynamoDB 原生 TTL 功能](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)自动移除旧批次记录。

如果为 DynamoDB 表定义了 `ttl` 属性，可以通过配置参数告知 Laravel 如何清理批次记录。`queue.batching.ttl_attribute` 定义存放 TTL 的属性名，`queue.batching.ttl` 则定义自记录最后更新起，经过多少秒后可以将其从 DynamoDB 表中删除：

```php
'batching' => [
    'driver' => env('QUEUE_BATCHING_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'job_batches',
    'ttl_attribute' => 'ttl',
    'ttl' => 60 * 60 * 24 * 7, // 7 天...
],
```

<a name="queueing-closures"></a>
## 将闭包加入队列

除了将任务类分发到队列，还可以分发闭包。这很适合需要在当前请求周期之外执行的简短任务。将闭包分发到队列时，其代码内容会经过密码学签名，以防在传输过程中被篡改：

```php
use App\Models\Podcast;

$podcast = Podcast::find(1);

dispatch(function () use ($podcast) {
    $podcast->publish();
});
```

如果希望为队列中的闭包指定名称，以供队列监控仪表盘使用，并在 `queue:work` 命令中显示，可以使用 `name` 方法：

```php
dispatch(function () {
    // ...
})->name('Publish Podcast');
```

通过 `catch` 方法，可以提供一个闭包，当队列中的闭包耗尽所有[配置的重试次数](#max-job-attempts-and-timeout)后仍未成功完成时，执行该闭包：

```php
use Throwable;

dispatch(function () use ($podcast) {
    $podcast->publish();
})->catch(function (Throwable $e) {
    // 此任务已失败...
});
```

> [!WARNING]
> `catch` 回调会被序列化，并在稍后由 Laravel 队列执行，因此不应在回调中使用 `$this` 变量。

<a name="running-the-queue-worker"></a>
## 运行队列工作进程

<a name="the-queue-work-command"></a>
### `queue:work` 命令

Laravel 提供了一个 Artisan 命令，用于启动队列工作进程，并处理新推送到队列中的任务。可以通过 `queue:work` Artisan 命令运行工作进程。请注意，该命令一旦启动，就会持续运行，直到手动停止或关闭终端：

```shell
php artisan queue:work
```

> [!NOTE]
> 要让 `queue:work` 进程在后台持续运行，应使用 [Supervisor](#supervisor-configuration) 等进程监控工具，确保队列工作进程不会停止运行。

如果希望命令输出包含已处理任务的 ID、连接名称和队列名称，可以在调用 `queue:work` 命令时添加 `-v` 标志：

```shell
php artisan queue:work -v
```

请记住，队列工作进程是长期运行的进程，会将启动后的应用状态保存在内存中。因此，它们在启动后不会察觉代码库的变化。部署时，请务必[重启队列工作进程](#queue-workers-and-deployment)。此外，应用创建或修改的静态状态不会在不同任务之间自动重置。

也可以运行 `queue:listen` 命令。使用该命令时，重新加载更新后的代码或重置应用状态不需要手动重启工作进程；不过，它的效率明显低于 `queue:work` 命令：

```shell
php artisan queue:listen
```

<a name="running-multiple-queue-workers"></a>
#### 运行多个队列工作进程

要为同一队列分配多个工作进程并发处理任务，只需启动多个 `queue:work` 进程。本地可以通过终端的多个标签页实现，生产环境则可以通过进程管理器的配置实现。[使用 Supervisor 时](#supervisor-configuration)，可以使用 `numprocs` 配置值。

<a name="specifying-the-connection-queue"></a>
#### 指定连接与队列

还可以指定工作进程使用的队列连接。传给 `work` 命令的连接名称应与 `config/queue.php` 配置文件中定义的某个连接对应：

```shell
php artisan queue:work redis
```

默认情况下，`queue:work` 命令只处理指定连接的默认队列中的任务。不过，可以进一步定制工作进程，让它只处理该连接中的特定队列。例如，如果所有邮件都在 `redis` 队列连接的 `emails` 队列中处理，可以运行以下命令启动仅处理该队列的工作进程：

```shell
php artisan queue:work redis --queue=emails
```

<a name="processing-a-specified-number-of-jobs"></a>
#### 处理指定数量的任务

通过 `--once` 选项，可以让工作进程只处理队列中的一个任务：

```shell
php artisan queue:work --once
```

通过 `--max-jobs` 选项，可以让工作进程处理指定数量的任务后退出。配合 [Supervisor](#supervisor-configuration) 使用时，这个选项很有用，可以在处理一定数量的任务后自动重启工作进程，释放可能积累的内存：

```shell
php artisan queue:work --max-jobs=1000
```

<a name="processing-all-queued-jobs-then-exiting"></a>
#### 处理所有队列任务后退出

通过 `--stop-when-empty` 选项，可以让工作进程处理完所有任务后优雅退出。在 Docker 容器中处理 Laravel 队列，并希望队列清空后关闭容器时，这个选项很有用：

```shell
php artisan queue:work --stop-when-empty
```

<a name="processing-jobs-for-a-given-number-of-seconds"></a>
#### 在指定时间内处理任务

通过 `--max-time` 选项，可以让工作进程在指定秒数内处理任务，然后退出。配合 [Supervisor](#supervisor-configuration) 使用时，这个选项很有用，可以在运行一定时间后自动重启工作进程，释放可能积累的内存：

```shell
# 处理任务一小时后退出...
php artisan queue:work --max-time=3600
```

<a name="worker-sleep-duration"></a>
#### 工作进程的休眠时间

队列中有可用任务时，工作进程会连续处理任务，任务之间没有延迟。而 `sleep` 选项决定了没有可用任务时，工作进程应「休眠」多少秒。当然，休眠期间工作进程不会处理新任务：

```shell
php artisan queue:work --sleep=3
```

<a name="maintenance-mode-queues"></a>
#### 维护模式与队列

应用处于[维护模式](/docs/{{version}}/configuration#maintenance-mode)时，不会处理任何队列任务。退出维护模式后，任务会恢复正常处理。

要强制队列工作进程在维护模式下仍然处理任务，可以使用 `--force` 选项：

```shell
php artisan queue:work --force
```

<a name="resource-considerations"></a>
#### 资源使用注意事项

`--memory` 选项指定工作进程应退出时的内存上限，单位为 MB，默认是 128 MB。也可以指定 PHP 配置的 `memory_limit` 的百分比：

```shell
php artisan queue:work --memory=60%
```

按百分比设置上限时，PHP 的 `memory_limit` 必须为有限值。如果 PHP 内存限制为无限（`-1`），请改用 MB 设置上限。[Supervisor](#supervisor-configuration) 等进程监控工具可以在工作进程退出后自动重启它。

守护模式的队列工作进程不会在每次处理任务前「重新启动」框架。因此，应在每个任务完成后释放占用较多资源的对象。例如，使用 [GD 库](https://www.php.net/manual/en/book.image.php)进行[图像处理](/docs/{{version}}/images)时，应在处理完图像后调用 `imagedestroy` 释放内存。

<a name="queue-priorities"></a>
### 队列优先级

有时，你可能希望设置队列的处理优先级。例如，在 `config/queue.php` 中将 `redis` 连接的默认 `queue` 设为 `low`，但偶尔又希望将任务推送到 `high` 高优先级队列：

```php
dispatch((new Job)->onQueue('high'));
```

要让工作进程先处理完 `high` 队列中的所有任务，再处理 `low` 队列的任务，请向 `work` 命令传入以逗号分隔的队列名称列表：

```shell
php artisan queue:work --queue=high,low
```

<a name="queue-workers-and-deployment"></a>
### 队列工作进程与部署

队列工作进程长期运行，不重启就无法察觉代码变化。因此，部署使用队列工作进程的应用时，最简单的方式就是在部署过程中重启工作进程。可以通过 `queue:restart` 命令优雅地重启所有工作进程：

```shell
php artisan queue:restart
```

该命令会指示所有队列工作进程在处理完当前任务后优雅退出，确保不会丢失正在执行的任务。由于执行 `queue:restart` 后工作进程会退出，应运行 [Supervisor](#supervisor-configuration) 等进程管理器来自动重启它们。

> [!NOTE]
> 队列使用[缓存](/docs/{{version}}/cache)存放重启信号，因此使用此功能前，应确认应用已正确配置缓存驱动。

<a name="reacting-to-worker-signals"></a>
### 响应工作进程信号

队列工作进程处理任务时，如果收到 `SIGQUIT`、`SIGTERM` 或 `SIGINT` 等终止信号，会先完成当前任务再退出。不过，你的任务可能需要在服务器或容器编排器停止进程之前就响应信号。例如，长时间运行的导入任务可能需要停止获取新记录，并保存当前进度。

要在任务内响应工作进程信号，请实现 `Illuminate\Contracts\Queue\Interruptible` 接口，并在任务中定义 `interrupted` 方法。工作进程收到的信号编号会传入该方法：

```php
<?php

namespace App\Jobs;

use App\Models\Import;
use Illuminate\Contracts\Queue\Interruptible;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ImportProducts implements ShouldQueue, Interruptible
{
    use Queueable;

    protected bool $shouldStop = false;

    /**
     * 创建一个新的任务实例。
     */
    public function __construct(
        public Import $import,
    ) {}

    /**
     * 执行任务。
     */
    public function handle(): void
    {
        foreach ($this->import->pendingRows() as $row) {
            if ($this->shouldStop) {
                break;
            }

            // 导入该产品行...
        }

        $this->import->saveProgress();
    }

    /**
     * 处理队列工作进程收到的信号。
     */
    public function interrupted(int $signal): void
    {
        $this->shouldStop = true;
    }
}
```

只有在任务正在运行、且工作进程收到进程信号时，才会调用 `interrupted` 方法。它不能替代[超时](#worker-timeouts)机制或任务的 [`failed` 方法](#cleaning-up-after-failed-jobs)。

<a name="job-expirations-and-timeouts"></a>
### 任务过期与超时

<a name="job-expiration"></a>
#### 任务过期

在 `config/queue.php` 配置文件中，每个队列连接都定义了 `retry_after` 选项，指定连接应等待多少秒再重试正在处理的任务。例如，将 `retry_after` 设为 `90` 后，任务如果处理了 90 秒仍未被释放或删除，就会被释放回队列。通常，应将该值设为任务合理情况下完成处理所需的最长秒数。

> [!WARNING]
> 唯一没有 `retry_after` 值的队列连接是 Amazon SQS。SQS 会根据 AWS 控制台中管理的[默认可见性超时](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/AboutVT.html)来重试任务。

<a name="worker-timeouts"></a>
#### 工作进程超时

`queue:work` Artisan 命令提供了 `--timeout` 选项，默认是 60 秒。如果任务处理时间超过该值，处理任务的工作进程会以错误状态退出。通常，[服务器上配置的进程管理器](#supervisor-configuration)会自动重启该进程：

```shell
php artisan queue:work --timeout=60
```

`retry_after` 配置选项与 `--timeout` 命令行选项有所不同，但会共同确保任务不丢失，并且只被成功处理一次。

> [!WARNING]
> `--timeout` 值应始终比 `retry_after` 配置值至少短几秒，以确保处理卡死任务的工作进程在任务被重试之前终止。如果 `--timeout` 大于 `retry_after`，任务可能被处理两次。

<a name="pausing-and-resuming-queue-workers"></a>
### 暂停与恢复队列工作进程

有时，你可能需要暂时阻止工作进程处理新任务，而不完全停止进程。例如，在系统维护期间暂停任务处理。Laravel 提供了 `queue:pause` 和 `queue:continue` Artisan 命令来暂停与恢复队列工作进程。

要暂停特定队列，请提供队列连接名称和队列名称：

```shell
php artisan queue:pause database:default
```

上例中，`database` 是队列连接名称，`default` 是队列名称。暂停队列后，正在处理该队列任务的工作进程会继续完成当前任务，但在队列恢复之前不会获取新任务。

要暂停所有连接上的所有队列的任务处理，请使用 `--all` 选项：

```shell
php artisan queue:pause --all
```

要恢复已暂停队列的任务处理，请使用 `queue:continue` 命令：

```shell
php artisan queue:continue database:default
```

要恢复所有连接上的所有队列的任务处理，请在 `queue:resume` 命令中使用 `--all` 选项：

```shell
php artisan queue:resume --all
```

恢复队列后，工作进程会立即开始处理其中的新任务。恢复所有队列并不会恢复单独暂停的队列。请注意，暂停队列不会停止工作进程本身，只会阻止它处理指定队列中的新任务。

<a name="worker-restart-and-pause-signals"></a>
#### 工作进程的重启与暂停信号

默认情况下，队列工作进程在每轮任务循环中都会轮询缓存驱动，检查重启与暂停信号。虽然这是响应 `queue:restart` 和 `queue:pause` 命令所必需的，但也会带来少量性能开销。

如果需要优化性能且不需要这些中断功能，可以调用 `Queue` 门面的 `withoutInterruptionPolling` 方法，全局禁用此轮询。通常，应在 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Queue;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Queue::withoutInterruptionPolling();
}
```

也可以通过设置 `Illuminate\Queue\Worker` 类的静态属性 `$restartable` 或 `$pausable`，分别禁用重启或暂停轮询：

```php
use Illuminate\Queue\Worker;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Worker::$restartable = false;
    Worker::$pausable = false;
}
```

> [!WARNING]
> 禁用中断轮询后，工作进程将不再响应 `queue:restart` 或 `queue:pause` 命令，具体取决于禁用的功能。

<a name="supervisor-configuration"></a>
## Supervisor 配置

在生产环境中，你需要让 `queue:work` 进程持续运行。该进程可能因多种原因停止，例如工作进程超时，或执行了 `queue:restart` 命令。

因此，需要配置一个进程监控工具，在检测到 `queue:work` 进程退出时自动重启它。此外，进程监控工具还可以指定并发运行的 `queue:work` 进程数量。Supervisor 是 Linux 环境中常用的进程监控工具，下面将介绍如何配置它。

<a name="installing-supervisor"></a>
#### 安装 Supervisor

Supervisor 是 Linux 操作系统的进程监控工具，能够在 `queue:work` 进程失败时自动重启它们。在 Ubuntu 上，可以使用以下命令安装 Supervisor：

```shell
sudo apt-get install supervisor
```

> [!NOTE]
> 如果觉得自行配置和管理 Supervisor 太复杂，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com)，它提供了运行 Laravel 队列工作进程的全托管平台。

<a name="configuring-supervisor"></a>
#### 配置 Supervisor

Supervisor 配置文件通常位于 `/etc/supervisor/conf.d` 目录中。可以在此目录创建任意数量的配置文件，告知 Supervisor 如何监控进程。例如，创建一个 `laravel-worker.conf` 文件来启动并监控 `queue:work` 进程：

```ini
[program:laravel-worker]
process_name=%(program_name)s_%(process_num)02d
command=php /home/forge/app.com/artisan queue:work --sleep=3 --tries=3 --max-time=3600
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

在上例中，`numprocs` 指令会让 Supervisor 运行并监控八个 `queue:work` 进程，并在它们失败时自动重启。应根据需要的队列连接与工作进程选项，修改配置中的 `command` 指令。

> [!WARNING]
> 应确保 `stopwaitsecs` 的值大于耗时最长的任务所需的秒数。否则，Supervisor 可能在任务处理完成之前就终止它。

<a name="starting-supervisor"></a>
#### 启动 Supervisor

创建配置文件后，可以使用以下命令更新 Supervisor 配置并启动进程：

```shell
sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl start "laravel-worker:*"
```

更多信息请参阅 [Supervisor 文档](http://supervisord.org/index.html)。

<a name="dealing-with-failed-jobs"></a>
## 处理失败的任务

队列任务有时会失败。别担心，事情不总是按计划进行！Laravel 提供了[指定任务最大尝试次数](#max-job-attempts-and-timeout)的便捷方式。异步任务超过此次数后，会被插入 `failed_jobs` 数据库表。[同步分发的任务](/docs/{{version}}/queues#synchronous-dispatching)失败时不会存入该表，而是立即由应用处理其异常。

新的 Laravel 应用通常已包含创建 `failed_jobs` 表的迁移。如果应用没有该迁移，可以使用 `make:queue-failed-table` 命令创建：

```shell
php artisan make:queue-failed-table

php artisan migrate
```

运行[队列工作进程](#running-the-queue-worker)时，可以通过 `queue:work` 命令的 `--tries` 选项指定任务的最大尝试次数。如果不指定 `--tries` 值，任务只会尝试一次，或按任务类的 `Tries` 属性指定的次数尝试：

```shell
php artisan queue:work redis --tries=3
```

通过 `--backoff` 选项，可以指定 Laravel 在重试遇到异常的任务前应等待的秒数。默认情况下，任务会立即释放回队列，以供再次尝试：

```shell
php artisan queue:work redis --tries=3 --backoff=3
```

如果希望按任务分别配置遇到异常后的重试等待秒数，可以在任务类中使用 `Backoff` 属性：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\Backoff;

#[Backoff(3)]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

如果需要更复杂的逻辑来确定任务的重试等待时间，可以在任务类中定义 `backoff` 方法：

```php
/**
 * 计算重试任务前应等待的秒数。
 */
public function backoff(): int
{
    return 3;
}
```

通过定义重试等待时间数组，可以轻松配置「指数型」退避。在这个示例中，第一次重试等待 1 秒，第二次等待 5 秒，第三次等待 10 秒；如果还有剩余尝试次数，此后的每次重试都等待 10 秒：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\Backoff;

#[Backoff([1, 5, 10])]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

<a name="cleaning-up-after-failed-jobs"></a>
### 任务失败后的清理

某个任务失败时，你可能希望向用户发送提醒，或撤销任务已部分完成的操作。为此，可以在任务类中定义 `failed` 方法，导致任务失败的 `Throwable` 实例会传入该方法：

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
        // 处理上传的播客...
    }

    /**
     * 处理任务失败。
     */
    public function failed(?Throwable $exception): void
    {
        // 向用户发送失败通知等...
    }
}
```

> [!WARNING]
> 调用 `failed` 方法之前，会重新实例化一个任务对象。因此，在 `handle` 方法中对类属性所做的任何修改都会丢失。

失败的任务不一定遇到了未处理的异常。耗尽所有允许的尝试次数时，任务也会被视为失败。以下情况会消耗尝试次数：

<div class="content-list" markdown="1">

- 任务超时。
- 任务在执行过程中遇到未处理的异常。
- 手动或通过中间件将任务释放回队列。

</div>

如果最后一次尝试因任务执行时抛出的异常而失败，该异常会传入任务的 `failed` 方法。如果任务是因达到最大允许尝试次数而失败，`$exception` 则会是 `Illuminate\Queue\MaxAttemptsExceededException` 实例。同样，如果任务因超过配置的超时时间而失败，`$exception` 会是 `Illuminate\Queue\TimeoutExceededException` 实例。

<a name="retrying-failed-jobs"></a>
### 重试失败的任务

要查看已插入 `failed_jobs` 数据库表的所有失败任务，可以使用 `queue:failed` Artisan 命令：

```shell
php artisan queue:failed
```

`queue:failed` 命令会列出任务 ID、连接、队列、失败时间及其他任务信息。可以使用任务 ID 重试失败的任务。例如，重试 ID 为 `ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece` 的失败任务，请运行以下命令：

```shell
php artisan queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece
```

如果需要，可以向命令传入多个 ID：

```shell
php artisan queue:retry ce7bb17c-cdd8-41f0-a8ec-7b4fef4e5ece 91401d2c-0784-4f43-824c-34f94a33c24d
```

也可以重试某个队列中的所有失败任务：

```shell
php artisan queue:retry --queue=name
```

要重试所有失败任务，请运行 `queue:retry` 命令，并传入 `all` 作为 ID：

```shell
php artisan queue:retry all
```

如果希望删除某个失败任务，可以使用 `queue:forget` 命令：

```shell
php artisan queue:forget 91401d2c-0784-4f43-824c-34f94a33c24d
```

> [!NOTE]
> 使用 [Horizon](/docs/{{version}}/horizon) 时，应使用 `horizon:forget` 命令删除失败任务，而不是 `queue:forget`。

要从 `failed_jobs` 表中删除所有失败任务，可以使用 `queue:flush` 命令：

```shell
php artisan queue:flush
```

`queue:flush` 命令会移除所有失败任务记录，不论失败发生在多久之前。通过 `--hours` 选项，可以只删除在指定小时数之前或更早失败的任务：

```shell
php artisan queue:flush --hours=48
```

<a name="ignoring-missing-models"></a>
### 忽略缺失的模型

将 Eloquent 模型注入任务时，模型会在加入队列前自动序列化，并在处理任务时从数据库重新获取。不过，如果模型在任务等待工作进程处理期间被删除，任务可能会因 `ModelNotFoundException` 而失败。

为方便起见，可以在任务类中使用 `DeleteWhenMissingModels` 属性，自动删除模型缺失的任务。使用该属性后，Laravel 会悄悄丢弃任务，而不抛出异常：

```php
<?php

namespace App\Jobs;

use Illuminate\Queue\Attributes\DeleteWhenMissingModels;

#[DeleteWhenMissingModels]
class ProcessPodcast implements ShouldQueue
{
    // ...
}
```

<a name="pruning-failed-jobs"></a>
### 清理失败的任务

可以调用 `queue:prune-failed` Artisan 命令，清理应用 `failed_jobs` 表中的记录：

```shell
php artisan queue:prune-failed
```

默认情况下，所有超过 24 小时的失败任务记录都会被清理。如果为命令提供 `--hours` 选项，则只会保留最近 N 小时内插入的失败任务记录。例如，以下命令会删除所有在 48 小时之前插入的失败任务记录：

```shell
php artisan queue:prune-failed --hours=48
```

<a name="storing-failed-jobs-in-dynamodb"></a>
### 在 DynamoDB 中存储失败的任务

Laravel 也支持将失败任务记录存储在 [DynamoDB](https://aws.amazon.com/dynamodb) 中，而不是关系型数据库表。不过，需要手动创建一个 DynamoDB 表来存储所有失败任务记录。通常，该表应命名为 `failed_jobs`，但具体名称应与应用 `queue` 配置文件中的 `queue.failed.table` 配置值一致。

`failed_jobs` 表应具有名为 `application` 的字符串主分区键，以及名为 `uuid` 的字符串主排序键。键中的 `application` 部分会包含应用名称，该名称由应用 `app` 配置文件中的 `name` 配置值定义。由于应用名称是 DynamoDB 表键的一部分，因此可以用同一张表存储多个 Laravel 应用的失败任务。

此外，请确保安装 AWS SDK，以便 Laravel 应用与 Amazon DynamoDB 通信：

```shell
composer require aws/aws-sdk-php
```

接着，将 `queue.failed.driver` 配置选项设为 `dynamodb`。还应在失败任务配置数组中定义 `key`、`secret` 和 `region` 选项，用于向 AWS 进行身份验证。使用 `dynamodb` 驱动时，不需要 `queue.failed.database` 配置选项：

```php
'failed' => [
    'driver' => env('QUEUE_FAILED_DRIVER', 'dynamodb'),
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'table' => 'failed_jobs',
],
```

<a name="disabling-failed-job-storage"></a>
### 禁用失败任务存储

将 `queue.failed.driver` 配置选项设为 `null`，可以让 Laravel 丢弃失败任务而不存储。通常，可通过 `QUEUE_FAILED_DRIVER` 环境变量进行设置：

```ini
QUEUE_FAILED_DRIVER=null
```

<a name="failed-job-events"></a>
### 任务失败事件

如果希望注册任务失败时调用的事件监听器，可以使用 `Queue` 门面的 `failing` 方法。例如，在 Laravel 自带的 `AppServiceProvider` 的 `boot` 方法中，为该事件附加闭包：

```php
<?php

namespace App\Providers;

use Illuminate\Support\Facades\Queue;
use Illuminate\Support\ServiceProvider;
use Illuminate\Queue\Events\JobFailed;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 引导应用服务。
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

<a name="clearing-jobs-from-queues"></a>
## 清空队列中的任务

> [!NOTE]
> 使用 [Horizon](/docs/{{version}}/horizon) 时，应使用 `horizon:clear` 命令清空队列中的任务，而不是 `queue:clear`。

如果希望删除默认连接的默认队列中的所有任务，可以使用 `queue:clear` Artisan 命令：

```shell
php artisan queue:clear
```

也可以提供 `connection` 参数和 `queue` 选项，删除指定连接与队列中的任务：

```shell
php artisan queue:clear redis --queue=emails
```

> [!WARNING]
> 清空队列任务仅适用于 SQS、Redis 和数据库队列驱动。此外，SQS 消息删除过程最多需要 60 秒，因此清空队列后 60 秒内发送到 SQS 队列的任务也可能被删除。

<a name="monitoring-your-queues"></a>
## 监控队列

如果队列突然收到大量任务，可能会不堪重负，导致任务等待时间过长。如果需要，Laravel 可以在队列任务数量超过指定阈值时提醒你。

首先，应将 `queue:monitor` 命令调度为[每分钟运行一次](/docs/{{version}}/scheduling)。该命令接收要监控的队列名称，以及任务数量阈值：

```shell
php artisan queue:monitor redis:default,redis:deployments --max=100
```

仅调度此命令并不足以触发队列过载通知。当命令检测到某个队列的任务数量超过阈值时，会分发 `Illuminate\Queue\Events\QueueBusy` 事件。可以在应用的 `AppServiceProvider` 中监听该事件，向你或开发团队发送通知：

```php
use App\Notifications\QueueHasLongWaitTime;
use Illuminate\Queue\Events\QueueBusy;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Notification;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Event::listen(function (QueueBusy $event) {
        Notification::route('mail', 'dev@example.com')
            ->notify(new QueueHasLongWaitTime(
                $event->connectionName,
                $event->queue,
                $event->size
            ));
    });
}
```

<a name="testing"></a>
## 测试

测试分发任务的代码时，你可能希望让 Laravel 不实际执行任务本身，因为任务代码可以与分发代码分开直接测试。当然，要测试任务本身，可以在测试中实例化任务，并直接调用其 `handle` 方法。

可以使用 `Queue` 门面的 `fake` 方法，阻止队列任务被真正推送到队列。调用该方法后，就可以断言应用是否尝试将任务推送到队列：

```php tab=Pest
<?php

use App\Jobs\AnotherJob;
use App\Jobs\ShipOrder;
use Illuminate\Support\Facades\Queue;

test('orders can be shipped', function () {
    Queue::fake();

    // 执行订单发货操作...

    // 断言没有任务被推送...
    Queue::assertNothingPushed();

    // 断言任务被推送到指定队列...
    Queue::assertPushedOn('queue-name', ShipOrder::class);

    // 断言任务已被推送
    Queue::assertPushed(ShipOrder::class);

    // 断言任务恰好被推送一次...
    Queue::assertPushedOnce(ShipOrder::class);

    // 断言任务被推送两次...
    Queue::assertPushedTimes(ShipOrder::class, 2);

    // 断言任务未被推送...
    Queue::assertNotPushed(AnotherJob::class);

    // 断言闭包已被推送到队列...
    Queue::assertClosurePushed();

    // 断言闭包未被推送...
    Queue::assertClosureNotPushed();

    // 断言已推送任务的总数...
    Queue::assertCount(3);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Jobs\AnotherJob;
use App\Jobs\ShipOrder;
use Illuminate\Support\Facades\Queue;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_orders_can_be_shipped(): void
    {
        Queue::fake();

        // 执行订单发货操作...

        // 断言没有任务被推送...
        Queue::assertNothingPushed();

        // 断言任务被推送到指定队列...
        Queue::assertPushedOn('queue-name', ShipOrder::class);

        // 断言任务已被推送
        Queue::assertPushed(ShipOrder::class);

        // 断言任务恰好被推送一次...
        Queue::assertPushedOnce(ShipOrder::class);

        // 断言任务被推送两次...
        Queue::assertPushedTimes(ShipOrder::class, 2);

        // 断言任务未被推送...
        Queue::assertNotPushed(AnotherJob::class);

        // 断言闭包已被推送到队列...
        Queue::assertClosurePushed();

        // 断言闭包未被推送...
        Queue::assertClosureNotPushed();

        // 断言已推送任务的总数...
        Queue::assertCount(3);
    }
}
```

可以向 `assertPushed`、`assertNotPushed`、`assertClosurePushed` 或 `assertClosureNotPushed` 方法传入闭包，根据给定的「真值测试」判断任务是否被推送。如果至少有一个已推送的任务通过此测试，断言就会成功：

```php
use Illuminate\Queue\CallQueuedClosure;

Queue::assertPushed(function (ShipOrder $job) use ($order) {
    return $job->order->id === $order->id;
});

Queue::assertClosurePushed(function (CallQueuedClosure $job) {
    return $job->name === 'validate-order';
});
```

也可以将预期属性值数组作为 `assertPushed` 或 `assertNotPushed` 的第二个参数，或作为 `assertPushedOn` 的第三个参数传入：

```php
Queue::assertPushed(ShipOrder::class, ['order' => $order]);

Queue::assertPushedOn('shipping', ShipOrder::class, ['order' => $order]);
```

所有指定属性都必须匹配。普通值使用严格相等进行比较，Eloquent 模型则使用其 `is` 方法比较。`Bus` 门面的 `assertDispatched`、`assertNotDispatched`、`assertDispatchedSync` 和 `assertDispatchedAfterResponse` 方法也接受预期属性值数组作为第二个参数。

<a name="faking-a-subset-of-jobs"></a>
### 模拟部分任务

如果只需模拟特定任务，同时让其他任务正常执行，可以将需要模拟的任务类名传给 `fake` 方法：

```php tab=Pest
test('orders can be shipped', function () {
    Queue::fake([
        ShipOrder::class,
    ]);

    // 执行订单发货操作...

    // 断言任务被推送两次...
    Queue::assertPushedTimes(ShipOrder::class, 2);
});
```

```php tab=PHPUnit
public function test_orders_can_be_shipped(): void
{
    Queue::fake([
        ShipOrder::class,
    ]);

    // 执行订单发货操作...

    // 断言任务被推送两次...
    Queue::assertPushedTimes(ShipOrder::class, 2);
}
```

通过 `except` 方法，可以模拟除指定任务之外的所有任务：

```php
Queue::fake()->except([
    ShipOrder::class,
]);
```

<a name="testing-job-chains"></a>
### 测试任务链

要测试任务链，需要使用 `Bus` 门面的模拟功能。其 `assertChained` 方法可用于断言[任务链](/docs/{{version}}/queues#job-chaining)已被分发。该方法接收链式任务数组作为第一个参数：

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

如上例所示，链式任务数组可以由任务类名组成，也可以由实际的任务实例组成。传入任务实例时，Laravel 会确保它们与应用分发的链式任务属于同一个类，且属性值相同：

```php
Bus::assertChained([
    new ShipOrder,
    new RecordShipment,
    new UpdateInventory,
]);
```

通过 `assertDispatchedWithoutChain` 方法，可以断言任务被推送时没有附带任务链：

```php
Bus::assertDispatchedWithoutChain(ShipOrder::class);
```

<a name="testing-chain-modifications"></a>
#### 测试任务链的修改

如果链式任务[向现有任务链的开头或末尾添加任务](#adding-jobs-to-the-chain)，可以使用任务的 `assertHasChain` 方法，断言剩余任务链符合预期：

```php
$job = new ProcessPodcast;

$job->handle();

$job->assertHasChain([
    new TranscribePodcast,
    new OptimizePodcast,
    new ReleasePodcast,
]);
```

通过 `assertDoesntHaveChain` 方法，可以断言任务的剩余任务链为空：

```php
$job->assertDoesntHaveChain();
```

<a name="testing-chained-batches"></a>
#### 测试任务链中的批次

如果任务链[包含一批任务](#chains-and-batches)，可以在任务链断言中插入 `Bus::chainedBatch` 定义，断言链中的批次符合预期：

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

<a name="testing-job-batches"></a>
### 测试任务批次

`Bus` 门面的 `assertBatched` 方法可用于断言[任务批次](/docs/{{version}}/queues#job-batching)已被分发。传给该方法的闭包会接收 `Illuminate\Bus\PendingBatch` 实例，可用于检查批次中的任务：

```php
use Illuminate\Bus\PendingBatch;
use Illuminate\Support\Facades\Bus;

Bus::fake();

// ...

Bus::assertBatched(function (PendingBatch $batch) {
    return $batch->name == 'Import CSV' &&
           $batch->jobs->count() === 10;
});
```

可以在待分发的批次上使用 `hasJobs` 方法，验证批次包含预期的任务。该方法接受任务实例、类名或闭包组成的数组：

```php
Bus::assertBatched(function (PendingBatch $batch) {
    return $batch->hasJobs([
        new ProcessCsvRow(row: 1),
        new ProcessCsvRow(row: 2),
        new ProcessCsvRow(row: 3),
    ]);
});
```

使用闭包时，闭包会接收任务实例。预期的任务类型会根据闭包的类型提示推断：

```php
Bus::assertBatched(function (PendingBatch $batch) {
    return $batch->hasJobs([
        fn (ProcessCsvRow $job) => $job->row === 1,
        fn (ProcessCsvRow $job) => $job->row === 2,
        fn (ProcessCsvRow $job) => $job->row === 3,
    ]);
});
```

通过 `assertBatchCount` 方法，可以断言已分发指定数量的批次：

```php
Bus::assertBatchCount(3);
```

通过 `assertNothingBatched` 方法，可以断言没有分发任何批次：

```php
Bus::assertNothingBatched();
```

<a name="testing-job-batch-interaction"></a>
#### 测试任务与批次的交互

此外，有时还需要测试单个任务与其所属批次的交互，例如测试任务是否取消了批次的后续处理。为此，可以通过 `withFakeBatch` 方法为任务分配一个模拟批次。该方法会返回包含任务实例和模拟批次的元组：

```php
[$job, $batch] = (new ShipOrder)->withFakeBatch();

$job->handle();

$this->assertTrue($batch->cancelled());
$this->assertEmpty($batch->added);
```

<a name="testing-job-queue-interactions"></a>
### 测试任务与队列的交互

有时，你可能需要测试队列任务是否[将自身释放回队列](#manually-releasing-a-job)，或是否删除了自身。可以实例化任务，并调用 `withFakeQueueInteractions` 方法来测试这些队列交互。

模拟任务的队列交互后，可以调用任务的 `handle` 方法。随后，可使用多种断言方法验证任务的队列交互：

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

<a name="job-events"></a>
## 任务事件

通过 `Queue` [门面](/docs/{{version}}/facades)的 `before` 和 `after` 方法，可以指定在队列任务处理前后执行的回调。这些回调很适合记录额外日志或增加仪表盘统计数据。通常，应在[服务提供者](/docs/{{version}}/providers)的 `boot` 方法中调用这些方法。例如，使用 Laravel 自带的 `AppServiceProvider`：

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
     * 注册应用服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 引导应用服务。
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

通过 `Queue` [门面](/docs/{{version}}/facades)的 `looping` 方法，可以指定工作进程尝试从队列获取任务之前执行的回调。例如，可以注册一个闭包，回滚先前失败任务遗留的未结束事务：

```php
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Queue;

Queue::looping(function () {
    while (DB::transactionLevel() > 0) {
        DB::rollBack();
    }
});
```

当队列工作进程无法从队列获取任务时，Laravel 还会分发 `Illuminate\Queue\Events\WorkerIdle` 事件：

```php
use Illuminate\Queue\Events\WorkerIdle;
use Illuminate\Support\Facades\Event;

Event::listen(function (WorkerIdle $event) {
    // $event->connectionName
    // $event->queue
    // $event->workerOptions
});
```

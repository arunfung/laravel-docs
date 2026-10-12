# 请求限流

- [简介](#introduction)
    - [缓存配置](#cache-configuration)
- [基本用法](#basic-usage)
    - [手动增加尝试次数](#manually-incrementing-attempts)
    - [清除尝试次数](#clearing-attempts)

<a name="introduction"></a>
## 简介

Laravel 提供了一个易于使用的限流抽象，它结合应用程序的[缓存](cache)，让你可以轻松限制指定时间段内任何操作的执行次数。

> [!NOTE]
> 如果你希望对传入的 HTTP 请求进行限流，请参阅[限流中间件文档](/docs/{{version}}/routing#rate-limiting)。

<a name="cache-configuration"></a>
### 缓存配置

通常，限流器会使用应用程序的默认缓存，即应用程序的 `cache` 配置文件中 `default` 键指定的缓存。不过，你可以在应用程序的 `cache` 配置文件中定义 `limiter` 键，指定限流器应使用的缓存驱动：

```php
'default' => env('CACHE_STORE', 'database'),

'limiter' => 'redis', // [tl! add]
```

<a name="basic-usage"></a>
## 基本用法

你可以使用 `Illuminate\Support\Facades\RateLimiter` 门面来操作限流器。限流器提供的最简单的方法是 `attempt`，它会限制给定回调在指定秒数内的执行次数。

当回调的剩余尝试次数为零时，`attempt` 方法会返回 `false`；否则，`attempt` 方法会返回回调的结果或 `true`。`attempt` 方法接受的第一个参数是限流器的「键」，你可以使用任意字符串来标识需要限流的操作：

```php
use Illuminate\Support\Facades\RateLimiter;

$executed = RateLimiter::attempt(
    'send-message:'.$user->id,
    $perMinute = 5,
    function() {
        // 发送消息...
    }
);

if (! $executed) {
    return 'Too many messages sent!';
}
```

如有需要，你可以向 `attempt` 方法传入第四个参数，即「衰减时间」，表示可用尝试次数重置前需要经过的秒数。例如，我们可以修改上面的示例，允许每两分钟尝试五次：

```php
$executed = RateLimiter::attempt(
    'send-message:'.$user->id,
    $perTwoMinutes = 5,
    function() {
        // 发送消息...
    },
    $decayRate = 120,
);
```

<a name="manually-incrementing-attempts"></a>
### 手动增加尝试次数

如果你想手动操作限流器，还可以使用其他多种方法。例如，你可以调用 `tooManyAttempts` 方法，判断给定限流器键的尝试次数是否已达到每分钟允许的最大次数：

```php
use Illuminate\Support\Facades\RateLimiter;

if (RateLimiter::tooManyAttempts('send-message:'.$user->id, $perMinute = 5)) {
    return 'Too many attempts!';
}

RateLimiter::increment('send-message:'.$user->id);

// 发送消息...
```

对可能同时收到大量请求的端点进行限流时，你可以检查 `increment` 方法的返回值，避免将 `tooManyAttempts` 和 `increment` 作为两个独立操作。使用 `redis`、`memcached` 或 `database` 缓存存储时，该值会以原子方式递增，确保每个并发请求获得不同的计数值：

```php
use Illuminate\Support\Facades\RateLimiter;

$perMinute = 5;

if (RateLimiter::increment('send-message:'.$user->id) > $perMinute) {
    return 'Too many attempts!';
}

// 发送消息...
```

或者，你可以使用 `remaining` 方法获取给定键的剩余尝试次数。如果该键仍有可用的尝试次数，你可以调用 `increment` 方法增加已记录的总尝试次数：

```php
use Illuminate\Support\Facades\RateLimiter;

if (RateLimiter::remaining('send-message:'.$user->id, $perMinute = 5)) {
    RateLimiter::increment('send-message:'.$user->id);

    // 发送消息...
}
```

如果你想让给定限流器键对应的值一次增加多个计数，可以向 `increment` 方法传入需要增加的数量：

```php
RateLimiter::increment('send-message:'.$user->id, amount: 5);
```

<a name="determining-limiter-availability"></a>
#### 确定限流器可用性

当一个键的剩余尝试次数为零时，`availableIn` 方法会返回再次获得可用尝试次数前需要等待的秒数：

```php
use Illuminate\Support\Facades\RateLimiter;

if (RateLimiter::tooManyAttempts('send-message:'.$user->id, $perMinute = 5)) {
    $seconds = RateLimiter::availableIn('send-message:'.$user->id);

    return 'You may try again in '.$seconds.' seconds.';
}

RateLimiter::increment('send-message:'.$user->id);

// 发送消息...
```

<a name="clearing-attempts"></a>
### 清除尝试次数

你可以使用 `clear` 方法重置给定限流器键的尝试次数。例如，当接收者读取某条消息时，你可以重置尝试次数：

```php
use App\Models\Message;
use Illuminate\Support\Facades\RateLimiter;

/**
 * 将消息标记为已读。
 */
public function read(Message $message): Message
{
    $message->markAsRead();

    RateLimiter::clear('send-message:'.$message->user_id);

    return $message;
}
```

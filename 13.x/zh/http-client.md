# HTTP 客户端

- [介绍](#introduction)
- [发送请求](#making-requests)
    - [请求数据](#request-data)
    - [请求头](#headers)
    - [认证](#authentication)
    - [超时](#timeout)
    - [重试](#retries)
    - [错误处理](#error-handling)
    - [Guzzle 中间件](#guzzle-middleware)
    - [Guzzle 选项](#guzzle-options)
- [并发请求](#concurrent-requests)
    - [请求池](#request-pooling)
    - [批量请求](#request-batching)
- [宏](#macros)
- [测试](#testing)
    - [伪造响应](#faking-responses)
    - [检查请求](#inspecting-requests)
    - [防止意外请求](#preventing-stray-requests)
- [事件](#events)

<a name="introduction"></a>
## 介绍

Laravel 围绕 [Guzzle HTTP 客户端](http://docs.guzzlephp.org/en/stable/) 提供了一套简洁、富有表现力的 API，使你能够快速发起 HTTP 请求，与其他 Web 应用进行通信。Laravel 对 Guzzle 的封装专注于最常用的场景，并提供了极佳的开发者体验。

<a name="making-requests"></a>
## 发送请求

要发送请求，你可以使用 `Http` 门面提供的 `head`、`get`、`post`、`put`、`patch` 和 `delete` 方法。首先，我们来看如何向另一个 URL 发起一个基本的 `GET` 请求：

```php
use Illuminate\Support\Facades\Http;

$response = Http::get('http://example.com');
```

`get` 方法返回一个 `Illuminate\Http\Client\Response` 实例，该实例提供了多种用于检查响应的方法：

```php
$response->body() : string;
$response->json($key = null, $default = null, $flags = null) : mixed;
$response->object() : object;
$response->collect($key = null) : Illuminate\Support\Collection;
$response->resource() : resource;
$response->status() : int;
$response->successful() : bool;
$response->redirect(): bool;
$response->failed() : bool;
$response->clientError() : bool;
$response->header($header) : string;
$response->headers() : array;
```

`Illuminate\Http\Client\Response` 对象还实现了 PHP 的 `ArrayAccess` 接口，允许你直接在响应上访问 JSON 响应数据：

```php
return Http::get('http://example.com/users/1')['name'];
```

除了上面列出的响应方法外，你还可以使用以下方法判断响应是否具有特定的状态码：

```php
$response->ok() : bool;                  // 200 OK
$response->created() : bool;             // 201 Created
$response->accepted() : bool;            // 202 Accepted
$response->noContent() : bool;           // 204 No Content
$response->movedPermanently() : bool;    // 301 Moved Permanently
$response->found() : bool;               // 302 Found
$response->badRequest() : bool;          // 400 Bad Request
$response->unauthorized() : bool;        // 401 Unauthorized
$response->paymentRequired() : bool;     // 402 Payment Required
$response->forbidden() : bool;           // 403 Forbidden
$response->notFound() : bool;            // 404 Not Found
$response->requestTimeout() : bool;      // 408 Request Timeout
$response->conflict() : bool;            // 409 Conflict
$response->unprocessableEntity() : bool; // 422 Unprocessable Entity
$response->tooManyRequests() : bool;     // 429 Too Many Requests
$response->serverError() : bool;         // >= 500 Server Error
```

<a name="uri-templates"></a>
#### URI 模板

HTTP 客户端还允许你使用 [URI 模板规范](https://www.rfc-editor.org/rfc/rfc6570)构建请求 URL。你可以使用 `withUrlParameters` 方法定义可由 URI 模板展开的 URL 参数：

```php
Http::withUrlParameters([
    'endpoint' => 'https://laravel.com',
    'page' => 'docs',
    'version' => '13.x',
    'topic' => 'validation',
])->get('{+endpoint}/{page}/{version}/{topic}');
```

<a name="dumping-requests"></a>
#### 打印请求信息

如果你希望在发送请求之前打印待发送的请求实例并终止脚本执行，可以在请求定义的开头添加 `dd` 方法：

```php
return Http::dd()->get('http://example.com');
```

<a name="request-data"></a>
### 请求数据

当然，发起 `POST`、`PUT` 和 `PATCH` 请求时，通常需要随请求发送额外的数据，因此这些方法接受一个数据数组作为第二个参数。默认情况下，数据将使用 `application/json` 内容类型发送：

```php
use Illuminate\Support\Facades\Http;

$response = Http::post('http://example.com/users', [
    'name' => 'Steve',
    'role' => 'Network Administrator',
]);
```

<a name="get-request-query-parameters"></a>
#### GET 请求查询参数

发起 `GET` 请求时，你可以直接在 URL 后追加查询字符串，或者将一个键值对数组作为第二个参数传递给 `get` 方法：

```php
$response = Http::get('http://example.com/users', [
    'name' => 'Taylor',
    'page' => 1,
]);
```

或者，你也可以使用 `withQueryParameters` 方法：

```php
Http::retry(3, 100)->withQueryParameters([
    'name' => 'Taylor',
    'page' => 1,
])->get('http://example.com/users');
```

<a name="sending-form-url-encoded-requests"></a>
#### 发送表单 URL 编码请求

如果你希望使用 `application/x-www-form-urlencoded` 内容类型发送数据，应在发起请求前调用 `asForm` 方法：

```php
$response = Http::asForm()->post('http://example.com/users', [
    'name' => 'Sara',
    'role' => 'Privacy Consultant',
]);
```

<a name="sending-a-raw-request-body"></a>
#### 发送原始请求体

如果你希望在发起请求时提供原始请求体，可以使用 `withBody` 方法。内容类型可以通过该方法的第二个参数提供：

```php
$response = Http::withBody(
    base64_encode($photo), 'image/jpeg'
)->post('http://example.com/photo');
```

<a name="multi-part-requests"></a>
#### 多部分请求

如果你希望通过多部分请求发送文件，应在发起请求前调用 `attach` 方法。该方法接受文件字段的名称及文件内容。如果需要，你可以提供第三个参数作为文件名，第四个参数则可用于提供与该文件相关的请求头：

```php
$response = Http::attach(
    'attachment', file_get_contents('photo.jpg'), 'photo.jpg', ['Content-Type' => 'image/jpeg']
)->post('http://example.com/attachments');
```

除了传递文件的原始内容，你也可以传递一个流资源：

```php
$photo = fopen('photo.jpg', 'r');

$response = Http::attach(
    'attachment', $photo, 'photo.jpg'
)->post('http://example.com/attachments');
```

<a name="headers"></a>
### 请求头

你可以使用 `withHeaders` 方法为请求添加请求头。`withHeaders` 方法接受一个键值对数组：

```php
$response = Http::withHeaders([
    'X-First' => 'foo',
    'X-Second' => 'bar'
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

你可以使用 `accept` 方法指定应用程序期望在请求响应中接收的内容类型：

```php
$response = Http::accept('application/json')->get('http://example.com/users');
```

为了方便起见，你可以使用 `acceptJson` 方法快速指定应用程序期望请求响应的内容类型为 `application/json`：

```php
$response = Http::acceptJson()->get('http://example.com/users');
```

`withHeaders` 方法会将新的请求头合并到请求现有的请求头中。如果需要，你可以使用 `replaceHeaders` 方法完全替换所有请求头：

```php
$response = Http::withHeaders([
    'X-Original' => 'foo',
])->replaceHeaders([
    'X-Replacement' => 'bar',
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

<a name="authentication"></a>
### 认证

你可以使用 `withBasicAuth` 和 `withDigestAuth` 方法分别指定基本认证和摘要认证的凭据：

```php
// 基本认证...
$response = Http::withBasicAuth('taylor@laravel.com', 'secret')->post(/* ... */);

// 摘要认证...
$response = Http::withDigestAuth('taylor@laravel.com', 'secret')->post(/* ... */);
```

<a name="bearer-tokens"></a>
#### Bearer 令牌

如果你希望快速将 Bearer 令牌添加到请求的 `Authorization` 请求头中，可以使用 `withToken` 方法：

```php
$response = Http::withToken('token')->post(/* ... */);
```

<a name="timeout"></a>
### 超时

你可以使用 `timeout` 方法指定等待响应的最大秒数。默认情况下，HTTP 客户端会在 30 秒后超时：

```php
$response = Http::timeout(3)->get(/* ... */);
```

如果超过了指定的超时时间，将会抛出一个 `Illuminate\Http\Client\ConnectionException` 实例。

你可以使用 `connectTimeout` 方法指定尝试连接服务器时的最大等待秒数。默认值为 10 秒：

```php
$response = Http::connectTimeout(3)->get(/* ... */);
```

<a name="retries"></a>
### 重试

如果你希望 HTTP 客户端在发生客户端或服务器错误时自动重试请求，可以使用 `retry` 方法。`retry` 方法接受请求的最大尝试次数，以及 Laravel 在每次尝试之间应等待的毫秒数：

```php
$response = Http::retry(3, 100)->post(/* ... */);
```

如果你希望手动计算每次尝试之间等待的毫秒数，可以将一个闭包作为第二个参数传递给 `retry` 方法：

```php
use Exception;

$response = Http::retry(3, function (int $attempt, Exception $exception) {
    return $attempt * 100;
})->post(/* ... */);
```

为了方便起见，你也可以将一个数组作为第一个参数传递给 `retry` 方法。该数组用于确定后续每次尝试之间等待的毫秒数：

```php
$response = Http::retry([100, 200])->post(/* ... */);
```

如果需要，你可以向 `retry` 方法传递第三个参数。第三个参数应是一个可调用对象，用于决定是否实际执行重试。例如，你可能只希望在初始请求遇到 `ConnectionException` 时重试该请求：

```php
use Illuminate\Http\Client\PendingRequest;
use Throwable;

$response = Http::retry(3, 100, function (Throwable $exception, PendingRequest $request) {
    return $exception instanceof ConnectionException;
})->post(/* ... */);
```

如果一次请求尝试失败，你可能希望在新的尝试之前修改请求。你可以通过修改传递给 `retry` 方法的可调用对象所接收的请求参数来实现这一点。例如，如果第一次尝试返回了认证错误，你可能希望使用新的授权令牌重试该请求：

```php
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\RequestException;
use Throwable;

$response = Http::withToken($this->getToken())->retry(2, 0, function (Throwable $exception, PendingRequest $request) {
    if (! $exception instanceof RequestException || $exception->response->status() !== 401) {
        return false;
    }

    $request->withToken($this->getNewToken());

    return true;
})->post(/* ... */);
```

如果所有请求都失败，将会抛出一个 `Illuminate\Http\Client\RequestException` 实例。如果你希望禁用此行为，可以提供一个值为 `false` 的 `throw` 参数。禁用后，客户端会在所有重试尝试完成后返回最后一次接收到的响应：

```php
$response = Http::retry(3, 100, throw: false)->post(/* ... */);
```

> [!WARNING]
> 如果所有请求都因连接问题而失败，即使 `throw` 参数设置为 `false`，仍然会抛出 `Illuminate\Http\Client\ConnectionException`。

<a name="error-handling"></a>
### 错误处理

与 Guzzle 的默认行为不同，Laravel 的 HTTP 客户端封装不会在客户端或服务器错误时抛出异常（即服务器返回 `400` 和 `500` 级别的响应）。你可以使用 `successful`、`clientError` 或 `serverError` 方法判断是否返回了这些错误：

```php
// 判断状态码是否 >= 200 且 < 300...
$response->successful();

// 判断状态码是否 >= 400...
$response->failed();

// 判断响应是否具有 400 级别的状态码...
$response->clientError();

// 判断响应是否具有 500 级别的状态码...
$response->serverError();

// 如果存在客户端或服务器错误，立即执行给定的回调...
$response->onError(callable $callback);
```

<a name="throwing-exceptions"></a>
#### 抛出异常

如果你有一个响应实例，并且希望在响应状态码表示客户端或服务器错误时抛出一个 `Illuminate\Http\Client\RequestException` 实例，可以使用 `throw` 或 `throwIf` 方法：

```php
use Illuminate\Http\Client\Response;

$response = Http::post(/* ... */);

// 如果发生了客户端或服务器错误，则抛出异常...
$response->throw();

// 如果发生错误并且给定条件为 true，则抛出异常...
$response->throwIf($condition);

// 如果发生错误并且给定闭包的返回值为 true，则抛出异常...
$response->throwIf(fn (Response $response) => true);

// 如果发生错误并且给定条件为 false，则抛出异常...
$response->throwUnless($condition);

// 如果发生错误并且给定闭包的返回值为 false，则抛出异常...
$response->throwUnless(fn (Response $response) => false);

// 如果响应具有特定状态码，则抛出异常...
$response->throwIfStatus(403);

// 如果响应不具有特定状态码，则抛出异常...
$response->throwUnlessStatus(200);

// 如果发生了服务器错误（状态码 >= 500），则抛出异常...
$response->throwIfServerError();

// 如果发生了客户端错误（状态码 >= 400 且 < 500），则抛出异常...
$response->throwIfClientError();

return $response['user']['id'];
```

`Illuminate\Http\Client\RequestException` 实例具有一个公共的 `$response` 属性，允许你检查返回的响应。

如果没有发生错误，`throw` 方法将返回响应实例，允许你在 `throw` 方法后链式调用其他操作：

```php
return Http::post(/* ... */)->throw()->json();
```

如果你希望在抛出异常之前执行一些额外的逻辑，可以将一个闭包传递给 `throw` 方法。闭包调用后会自动抛出异常，因此你不需要在闭包内部重新抛出异常：

```php
use Illuminate\Http\Client\Response;
use Illuminate\Http\Client\RequestException;

return Http::post(/* ... */)->throw(function (Response $response, RequestException $e) {
    // ...
})->json();
```

默认情况下，`RequestException` 消息在被记录或报告时会被截断为 120 个字符。要自定义或禁用此行为，你可以在 `bootstrap/app.php` 文件中配置应用程序的注册行为时，使用 `truncateAt` 和 `dontTruncate` 方法：

```php
use Illuminate\Http\Client\RequestException;

->registered(function (): void {
    // 将请求异常消息截断为 240 个字符...
    RequestException::truncateAt(240);

    // 禁用请求异常消息截断...
    RequestException::dontTruncate();
})
```

或者，你可以使用 `truncateExceptionsAt` 方法为单个请求自定义异常消息截断行为：

```php
return Http::truncateExceptionsAt(240)->post(/* ... */);
```

<a name="guzzle-middleware"></a>
### Guzzle 中间件

由于 Laravel 的 HTTP 客户端由 Guzzle 驱动，你可以利用 [Guzzle 中间件](https://docs.guzzlephp.org/en/stable/handlers-and-middleware.html)修改发出的请求或检查收到的响应。要修改发出的请求，可以通过 `withRequestMiddleware` 方法注册一个 Guzzle 中间件：

```php
use Illuminate\Support\Facades\Http;
use Psr\Http\Message\RequestInterface;

$response = Http::withRequestMiddleware(
    function (RequestInterface $request) {
        return $request->withHeader('X-Example', 'Value');
    }
)->get('http://example.com');
```

同样，你可以通过 `withResponseMiddleware` 方法注册一个中间件来检查收到的 HTTP 响应：

```php
use Illuminate\Support\Facades\Http;
use Psr\Http\Message\ResponseInterface;

$response = Http::withResponseMiddleware(
    function (ResponseInterface $response) {
        $header = $response->getHeader('X-Example');

        // ...

        return $response;
    }
)->get('http://example.com');
```

<a name="global-middleware"></a>
#### 全局中间件

有时，你可能希望注册一个适用于每一个发出的请求和收到的响应的中间件。为此，可以使用 `globalRequestMiddleware` 和 `globalResponseMiddleware` 方法。通常，这些方法应在应用程序的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Http;

Http::globalRequestMiddleware(fn ($request) => $request->withHeader(
    'User-Agent', 'Example Application/1.0'
));

Http::globalResponseMiddleware(fn ($response) => $response->withHeader(
    'X-Finished-At', now()->toDateTimeString()
));
```

<a name="guzzle-options"></a>
### Guzzle 选项

你可以使用 `withOptions` 方法为发出的请求指定额外的 [Guzzle 请求选项](http://docs.guzzlephp.org/en/stable/request-options.html)。`withOptions` 方法接受一个键值对数组：

```php
$response = Http::withOptions([
    'debug' => true,
])->get('http://example.com/users');
```

<a name="global-options"></a>
#### 全局选项

要为每一个发出的请求配置默认选项，你可以使用 `globalOptions` 方法。通常，该方法应在应用程序的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Http;

/**
 * 启动应用程序服务。
 */
public function boot(): void
{
    Http::globalOptions([
        'allow_redirects' => false,
    ]);
}
```

<a name="concurrent-requests"></a>
## 并发请求

有时，你可能希望并发发起多个 HTTP 请求。换句话说，你希望同时派发多个请求，而不是按顺序逐个发送。与响应缓慢的 HTTP API 交互时，这可以显著提升性能。

<a name="request-pooling"></a>
### 请求池

你可以使用 `pool` 方法实现这一点。`pool` 方法接受一个闭包，该闭包接收一个 `Illuminate\Http\Client\Pool` 实例，让你能够轻松地将请求添加到请求池中进行派发：

```php
use Illuminate\Http\Client\Pool;
use Illuminate\Support\Facades\Http;

$responses = Http::pool(fn (Pool $pool) => [
    $pool->get('http://localhost/first'),
    $pool->get('http://localhost/second'),
    $pool->get('http://localhost/third'),
]);

return $responses[0]->ok() &&
       $responses[1]->ok() &&
       $responses[2]->ok();
```

如你所见，你可以按照请求被添加到请求池中的顺序访问各个响应实例。如果需要，你可以使用 `as` 方法为请求命名，从而通过名称访问对应的响应：

```php
use Illuminate\Http\Client\Pool;
use Illuminate\Support\Facades\Http;

$responses = Http::pool(fn (Pool $pool) => [
    $pool->as('first')->get('http://localhost/first'),
    $pool->as('second')->get('http://localhost/second'),
    $pool->as('third')->get('http://localhost/third'),
]);

return $responses['first']->ok();
```

你可以通过向 `pool` 方法提供 `concurrency` 参数来控制请求池的最大并发数。该值决定了处理请求池时可以同时进行的 HTTP 请求的最大数量：

```php
$responses = Http::pool(fn (Pool $pool) => [
    // ...
], concurrency: 5);
```

如果请求池中的某个请求在连接层面失败（例如超时或 DNS 解析失败），`$responses` 数组中的对应项将是一个 `Illuminate\Http\Client\ConnectionException` 实例，而不是 `Response` 实例：

```php
foreach ($responses as $response) {
    if ($response instanceof Throwable) {
        // 请求连接失败...
    } elseif ($response->failed()) {
        // 请求连接成功，但收到了错误响应...
    }
}
```

<a name="customizing-concurrent-requests"></a>
#### 自定义并发请求

`pool` 方法不能与 `withHeaders` 或 `middleware` 等其他 HTTP 客户端方法链式调用。如果你希望为请求池中的请求应用自定义请求头或中间件，应在池中的每个请求上分别配置这些选项：

```php
use Illuminate\Http\Client\Pool;
use Illuminate\Support\Facades\Http;

$headers = [
    'X-Example' => 'example',
];

$responses = Http::pool(fn (Pool $pool) => [
    $pool->withHeaders($headers)->get('http://laravel.test/test'),
    $pool->withHeaders($headers)->get('http://laravel.test/test'),
    $pool->withHeaders($headers)->get('http://laravel.test/test'),
]);
```

<a name="request-batching"></a>
### 批量请求

在 Laravel 中处理并发请求的另一种方式是使用 `batch` 方法。与 `pool` 方法一样，它接受一个接收 `Illuminate\Http\Client\Batch` 实例的闭包，让你能够轻松地将请求添加到请求池中进行派发，同时还允许你定义完成回调：

```php
use Illuminate\Http\Client\Batch;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\RequestException;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;

$responses = Http::batch(fn (Batch $batch) => [
    $batch->get('http://localhost/first'),
    $batch->get('http://localhost/second'),
    $batch->get('http://localhost/third'),
])->before(function (Batch $batch) {
    // 批次已创建，但尚未初始化任何请求...
})->progress(function (Batch $batch, int|string $key, Response $response) {
    // 单个请求已成功完成...
})->then(function (Batch $batch, array $results) {
    // 所有请求均已成功完成...
})->catch(function (Batch $batch, int|string $key, Response|RequestException|ConnectionException $response) {
    // 检测到批次中的请求失败...
})->finally(function (Batch $batch, array $results) {
    // 批次已执行完毕...
})->send();
```

与 `pool` 方法一样，你可以使用 `as` 方法为请求命名：

```php
$responses = Http::batch(fn (Batch $batch) => [
    $batch->as('first')->get('http://localhost/first'),
    $batch->as('second')->get('http://localhost/second'),
    $batch->as('third')->get('http://localhost/third'),
])->send();
```

通过调用 `send` 方法启动 `batch` 后，你不能再向其中添加新请求。尝试这样做会抛出 `Illuminate\Http\Client\BatchInProgressException` 异常。

你可以通过 `concurrency` 方法控制请求批次的最大并发数。该值决定了处理请求批次时可以同时进行的 HTTP 请求的最大数量：

```php
$responses = Http::batch(fn (Batch $batch) => [
    // ...
])->concurrency(5)->send();
```

<a name="inspecting-batches"></a>
#### 检查批次

传递给批次完成回调的 `Illuminate\Http\Client\Batch` 实例提供了多种属性和方法，帮助你与给定的请求批次交互并检查该批次：

```php
// 分配给批次的请求数量...
$batch->totalRequests;

// 尚未处理的请求数量...
$batch->pendingRequests;

// 失败的请求数量...
$batch->failedRequests;

// 目前已处理的请求数量...
$batch->processedRequests();

// 判断批次是否已执行完毕...
$batch->finished();

// 判断批次中是否有失败的请求...
$batch->hasFailures();
```
<a name="deferring-batches"></a>
#### 延迟执行批次

调用 `defer` 方法时，请求批次不会立即执行。Laravel 会在当前应用请求的 HTTP 响应发送给用户后执行该批次，让你的应用程序保持快速、灵敏的响应体验：

```php
use Illuminate\Http\Client\Batch;
use Illuminate\Support\Facades\Http;

$responses = Http::batch(fn (Batch $batch) => [
    $batch->get('http://localhost/first'),
    $batch->get('http://localhost/second'),
    $batch->get('http://localhost/third'),
])->then(function (Batch $batch, array $results) {
    // 所有请求均已成功完成...
})->defer();
```

<a name="macros"></a>
## 宏

Laravel HTTP 客户端允许你定义「宏」，以一种流畅、富有表现力的方式，为应用程序中与服务的交互配置常用的请求路径和请求头。首先，你可以在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中定义宏：

```php
use Illuminate\Support\Facades\Http;

/**
 * 启动应用程序服务。
 */
public function boot(): void
{
    Http::macro('github', function () {
        return Http::withHeaders([
            'X-Example' => 'example',
        ])->baseUrl('https://github.com');
    });
}
```

配置宏后，你可以在应用程序的任何地方调用它，以指定的配置创建一个待发送的请求：

```php
$response = Http::github()->get('/');
```

<a name="testing"></a>
## 测试

许多 Laravel 服务都提供了帮助你轻松、清晰地编写测试的功能，Laravel 的 HTTP 客户端也不例外。`Http` 门面的 `fake` 方法允许你指示 HTTP 客户端在发起请求时返回存根或模拟响应。

<a name="faking-responses"></a>
### 伪造响应

例如，要指示 HTTP 客户端为每个请求返回内容为空、状态码为 `200` 的响应，你可以在不传递任何参数的情况下调用 `fake` 方法：

```php
use Illuminate\Support\Facades\Http;

Http::fake();

$response = Http::post(/* ... */);
```

<a name="faking-specific-urls"></a>
#### 伪造特定 URL

或者，你可以向 `fake` 方法传递一个数组。数组的键应表示你希望伪造响应的 URL 模式，值则是对应的响应。`*` 字符可以用作通配符。你可以使用 `Http` 门面的 `response` 方法为这些端点构造存根或伪造响应：

```php
Http::fake([
    // 为 GitHub 端点伪造一个 JSON 响应...
    'github.com/*' => Http::response(['foo' => 'bar'], 200, $headers),

    // 为 Google 端点伪造一个字符串响应...
    'google.com/*' => Http::response('Hello World', 200, $headers),
]);
```

向未伪造响应的 URL 发起的请求会实际执行。如果你希望指定一个兜底 URL 模式，为所有未匹配的 URL 提供存根响应，可以使用单个 `*` 字符：

```php
Http::fake([
    // 为 GitHub 端点伪造一个 JSON 响应...
    'github.com/*' => Http::response(['foo' => 'bar'], 200, ['Headers']),

    // 为所有其他端点伪造一个字符串响应...
    '*' => Http::response('Hello World', 200, ['Headers']),
]);
```

为了方便起见，你可以通过提供字符串、数组或整数作为响应，生成简单的字符串响应、JSON 响应或空响应：

```php
Http::fake([
    'google.com/*' => 'Hello World',
    'github.com/*' => ['foo' => 'bar'],
    'chatgpt.com/*' => 200,
]);
```

<a name="faking-connection-exceptions"></a>
#### 伪造异常

有时，你可能需要测试 HTTP 客户端尝试发起请求时遇到 `Illuminate\Http\Client\ConnectionException` 的情况下，应用程序的行为。你可以使用 `failedConnection` 方法指示 HTTP 客户端抛出一个连接异常：

```php
Http::fake([
    'github.com/*' => Http::failedConnection(),
]);
```

要测试抛出 `Illuminate\Http\Client\RequestException` 时应用程序的行为，你可以使用 `failedRequest` 方法：

```php
$this->mock(GithubService::class)
    ->shouldReceive('getUser')
    ->andThrow(
        Http::failedRequest(['code' => 'not_found'], 404)
    );
```

<a name="faking-response-sequences"></a>
#### 伪造响应序列

有时，你可能需要指定某个 URL 按特定顺序返回一系列伪造响应。你可以使用 `Http::sequence` 方法构建这些响应：

```php
Http::fake([
    // 为 GitHub 端点伪造一系列响应...
    'github.com/*' => Http::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->pushStatus(404),
]);
```

当响应序列中的所有响应都已被使用后，任何后续请求都会导致该响应序列抛出异常。如果你希望指定序列为空时应返回的默认响应，可以使用 `whenEmpty` 方法：

```php
Http::fake([
    // 为 GitHub 端点伪造一系列响应...
    'github.com/*' => Http::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->whenEmpty(Http::response()),
]);
```

如果你希望伪造一系列响应，但不需要指定要伪造响应的特定 URL 模式，可以使用 `Http::fakeSequence` 方法：

```php
Http::fakeSequence()
    ->push('Hello World', 200)
    ->whenEmpty(Http::response());
```

<a name="fake-callback"></a>
#### 伪造回调

如果你需要更复杂的逻辑来决定某些端点应返回什么响应，可以向 `fake` 方法传递一个闭包。该闭包接收一个 `Illuminate\Http\Client\Request` 实例，并应返回一个响应实例。在闭包中，你可以执行所需的逻辑来决定返回哪种响应：

```php
use Illuminate\Http\Client\Request;

Http::fake(function (Request $request) {
    return Http::response('Hello World', 200);
});
```

<a name="inspecting-requests"></a>
### 检查请求

伪造响应时，你可能希望检查客户端收到的请求，以确保应用程序发送了正确的数据或请求头。你可以在调用 `Http::fake` 后调用 `Http::assertSent` 方法来实现这一点。

`assertSent` 方法接受一个闭包，该闭包接收一个 `Illuminate\Http\Client\Request` 实例，并应返回一个布尔值，表示请求是否符合你的预期。要使测试通过，至少必须发送过一个符合给定预期的请求：

```php
use Illuminate\Http\Client\Request;
use Illuminate\Support\Facades\Http;

Http::fake();

Http::withHeaders([
    'X-First' => 'foo',
])->post('http://example.com/users', [
    'name' => 'Taylor',
    'role' => 'Developer',
]);

Http::assertSent(function (Request $request) {
    return $request->hasHeader('X-First', 'foo') &&
           $request->url() == 'http://example.com/users' &&
           $request['name'] == 'Taylor' &&
           $request['role'] == 'Developer';
});
```

如果需要，你可以使用 `assertNotSent` 方法断言未发送某个特定请求：

```php
use Illuminate\Http\Client\Request;
use Illuminate\Support\Facades\Http;

Http::fake();

Http::post('http://example.com/users', [
    'name' => 'Taylor',
    'role' => 'Developer',
]);

Http::assertNotSent(function (Request $request) {
    return $request->url() === 'http://example.com/posts';
});
```

你可以使用 `assertSentCount` 方法断言测试期间「发送」的请求数量：

```php
Http::fake();

Http::assertSentCount(5);
```

或者，你可以使用 `assertNothingSent` 方法断言没有发送任何请求：

```php
Http::fake();

Http::assertNothingSent();
```

<a name="recording-requests-and-responses"></a>
#### 记录请求与响应

你可以使用 `recorded` 方法收集所有请求及其对应的响应。`recorded` 方法返回一个数组集合，每个数组都包含 `Illuminate\Http\Client\Request` 和 `Illuminate\Http\Client\Response` 实例：

```php
Http::fake([
    'https://laravel.com' => Http::response(status: 500),
    'https://nova.laravel.com/' => Http::response(),
]);

Http::get('https://laravel.com');
Http::get('https://nova.laravel.com/');

$recorded = Http::recorded();

[$request, $response] = $recorded[0];
```

此外，`recorded` 方法接受一个闭包，该闭包接收 `Illuminate\Http\Client\Request` 和 `Illuminate\Http\Client\Response` 实例，可用于根据你的预期筛选请求与响应对：

```php
use Illuminate\Http\Client\Request;
use Illuminate\Http\Client\Response;

Http::fake([
    'https://laravel.com' => Http::response(status: 500),
    'https://nova.laravel.com/' => Http::response(),
]);

Http::get('https://laravel.com');
Http::get('https://nova.laravel.com/');

$recorded = Http::recorded(function (Request $request, Response $response) {
    return $request->url() !== 'https://laravel.com' &&
           $response->successful();
});
```

<a name="preventing-stray-requests"></a>
### 防止意外请求

如果你希望确保在单个测试或整个测试套件中，通过 HTTP 客户端发送的所有请求都已伪造响应，可以调用 `preventStrayRequests` 方法。调用该方法后，任何没有对应伪造响应的请求都会抛出异常，而不会实际发起 HTTP 请求：

```php
use Illuminate\Support\Facades\Http;

Http::preventStrayRequests();

Http::fake([
    'github.com/*' => Http::response('ok'),
]);

// 返回 "ok" 响应...
Http::get('https://github.com/laravel/framework');

// 抛出异常...
Http::get('https://laravel.com');
```

有时，你可能希望阻止大多数意外请求，同时仍允许执行特定请求。为此，你可以向 `allowStrayRequests` 方法传递一个 URL 模式数组。任何匹配给定模式的请求都将被允许执行，其他所有请求则仍会抛出异常：

```php
use Illuminate\Support\Facades\Http;

Http::preventStrayRequests();

Http::allowStrayRequests([
    'http://127.0.0.1:5000/*',
]);

// 此请求会实际执行...
Http::get('http://127.0.0.1:5000/generate');

// 抛出异常...
Http::get('https://laravel.com');
```

<a name="events"></a>
## 事件

Laravel 在发送 HTTP 请求的过程中会触发三个事件。`RequestSending` 事件在请求发送前触发，`ResponseReceived` 事件在收到给定请求的响应后触发。如果未收到给定请求的响应，则会触发 `ConnectionFailed` 事件。

`RequestSending` 和 `ConnectionFailed` 事件都包含一个公共的 `$request` 属性，可用于检查 `Illuminate\Http\Client\Request` 实例。同样，`ResponseReceived` 事件包含一个 `$request` 属性和一个 `$response` 属性，后者可用于检查 `Illuminate\Http\Client\Response` 实例。你可以在应用程序中为这些事件创建[事件监听器](/docs/{{version}}/events)：

```php
use Illuminate\Http\Client\Events\RequestSending;

class LogRequest
{
    /**
     * 处理事件。
     */
    public function handle(RequestSending $event): void
    {
        // $event->request ...
    }
}
```

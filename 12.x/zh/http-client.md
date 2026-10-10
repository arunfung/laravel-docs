
# HTTP 客户端

-   [介绍](#introduction)
-   [发送请求](#making-requests)
    -   [请求数据](#request-data)
    -   [请求头](#headers)
    -   [认证](#authentication)
    -   [超时](#timeout)
    -   [重试](#retries)
    -   [错误处理](#error-handling)
    -   [Guzzle 中间件](#guzzle-middleware)
    -   [Guzzle 选项](#guzzle-options)
-   [并发请求](#concurrent-requests)
-   [宏](#macros)
-   [测试](#testing)
    -   [伪造响应](#faking-responses)
    -   [检查请求](#inspecting-requests)
    -   [防止意外请求](#preventing-stray-requests)
-   [事件](#events)

## 介绍

Laravel 提供了一个围绕 [Guzzle HTTP 客户端](http://docs.guzzlephp.org/en/stable/) 的简洁、表达式化 API，使你能够快速发起 HTTP 请求，与其他 Web 应用进行通信。Laravel 对 Guzzle 的封装专注于最常用的场景，并提供了极佳的开发者体验。

## 发送请求

要发送请求，你可以使用 `Http` facade 提供的 `head`、`get`、`post`、`put`、`patch` 和 `delete` 方法。首先，我们来看如何向另一个 URL 发起一个基础的 `GET` 请求：

```php
use Illuminate\Support\Facades\Http;

$response = Http::get('http://example.com');
```

`get` 方法返回一个 `Illuminate\Http\Client\Response` 实例，该实例提供了多种方法，用于检查响应：

```php
$response->body() : string;
$response->json($key = null, $default = null) : mixed;
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

`Illuminate\Http\Client\Response` 对象还实现了 PHP 的 `ArrayAccess` 接口，允许你直接在响应上访问 JSON 数据：

```php
return Http::get('http://example.com/users/1')['name'];
```



除了上面列出的响应方法外，还可以使用以下方法来确定响应是否具有给定的状态代码：

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
$response->serverError() : bool;         // 500 Internal Server Error
```

<a name="uri-templates"></a>
#### URI 模板
HTTP 客户端还允许你使用 [URI 模板规范](https://www.rfc-editor.org/rfc/rfc6570)构建请求 URL。如果要通过 URI 模板展开 URL 参数，可以使用 `withUrlParameters` 方法：
```php
Http::withUrlParameters([
    'endpoint' => 'https://laravel.com',
    'page' => 'docs',
    'version' => '11.x',
    'topic' => 'validation',
])->get('{+endpoint}/{page}/{version}/{topic}');
```

<a name="dumping-requests"></a>
#### 打印请求信息

如果要在发送请求之前打印输出请求信息并且结束脚本运行，你应该在创建请求前调用 `dd` 方法：

```php
return Http::dd()->get('http://example.com');
```

<a name="request-data"></a>
### 请求数据

大多数情况下，`POST`、`PUT` 和 `PATCH` 携带着额外的请求数据是相当常见的。所以，这些方法的第二个参数接受一个包含着请求数据的数组。默认情况下，这些数据会使用 `application/json` 类型随请求发送：

```php
use Illuminate\Support\Facades\Http;

$response = Http::post('http://example.com/users', [
    'name' => 'Steve',
    'role' => 'Network Administrator',
]);
```



<a name="get-request-query-parameters"></a>
#### GET 请求查询参数

发出 `GET` 请求时，您可以直接在 URL 后追加查询字符串，或者将键/值对数组作为第二个参数传递给 `get` 方法：

```php
$response = Http::get('http://example.com/users', [
    'name' => 'Taylor',
    'page' => 1,
]);
```

或者，可以使用 `withQueryParameters` 方法：

```php
Http::retry(3, 100)->withQueryParameters([
    'name' => 'Taylor',
    'page' => 1,
])->get('http://example.com/users')
```

<a name="sending-form-url-encoded-requests"></a>
#### 发送表单 URL 编码请求

如果您想使用 `application/x-www-form-urlencoded` 内容类型发送数据，应该在发出请求前调用 `asForm` 方法：

```php
$response = Http::asForm()->post('http://example.com/users', [
    'name' => 'Sara',
    'role' => 'Privacy Consultant',
]);
```

<a name="sending-a-raw-request-body"></a>
#### 发送原始请求体

如果您想在发出请求时提供原始请求体，可以使用 `withBody` 方法。内容类型可以通过该方法的第二个参数提供：

```php
$response = Http::withBody(
    base64_encode($photo), 'image/jpeg'
)->post('http://example.com/photo');
```

<a name="multi-part-requests"></a>
#### 多部分请求

如果您想发送多部分请求文件，应该在发出请求前调用 `attach` 方法。此方法接受文件名和文件内容。如果需要，您可以提供第三个参数作为文件名，而第四个参数可用于提供与文件相关的标头：

```php
$response = Http::attach(
    'attachment', file_get_contents('photo.jpg'), 'photo.jpg', ['Content-Type' => 'image/jpeg']
)->post('http://example.com/attachments');
```



在传递文件内容时，你可以不必传递文件的原始内容，而是传递一个 **stream（流）资源**：

```php
$photo = fopen('photo.jpg', 'r');

$response = Http::attach(
    'attachment', $photo, 'photo.jpg'
)->post('http://example.com/attachments');
```

### 请求头（Headers）

可以使用 `withHeaders` 方法为请求添加请求头。`withHeaders` 方法接收一个键值对数组：

```php
$response = Http::withHeaders([
    'X-First' => 'foo',
    'X-Second' => 'bar'
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

你可以使用 `accept` 方法来指定应用程序在响应中期望的内容类型：

```php
$response = Http::accept('application/json')->get('http://example.com/users');
```

为了方便起见，你也可以使用 `acceptJson` 方法快速指定应用程序期望响应的内容类型为 `application/json`：

```php
$response = Http::acceptJson()->get('http://example.com/users');
```

`withHeaders` 方法会将新的请求头 **合并** 到现有请求头中。
如果需要，你也可以使用 `replaceHeaders` 方法完全替换所有请求头：

```php
$response = Http::withHeaders([
    'X-Original' => 'foo',
])->replaceHeaders([
    'X-Replacement' => 'bar',
])->post('http://example.com/users', [
    'name' => 'Taylor',
]);
```

### 认证

你可以通过 `withBasicAuth` 和 `withDigestAuth` 方法分别指定 **基本认证** 和 **摘要认证** 的凭据：

```php
// 基本认证...
$response = Http::withBasicAuth('taylor@laravel.com', 'secret')->post(/* ... */);

// 摘要认证...
$response = Http::withDigestAuth('taylor@laravel.com', 'secret')->post(/* ... */);
```

#### Bearer Token

如果你希望快速将 **Bearer Token** 添加到请求的 `Authorization` 请求头中，可以使用 `withToken` 方法：

```php
$response = Http::withToken('token')->post(/* ... */);
```



### 超时（Timeout）

你可以使用 `timeout` 方法来指定 **等待响应的最大秒数**。默认情况下，HTTP 客户端会在 **30 秒** 后超时：

```php
$response = Http::timeout(3)->get(/* ... */);
```

如果超过了指定的超时时间，将会抛出 `Illuminate\Http\Client\ConnectionException` 异常。

你还可以使用 `connectTimeout` 方法来指定 **连接服务器时的最大等待秒数**。默认是 **10 秒**：

```php
$response = Http::connectTimeout(3)->get(/* ... */);
```

### 重试（Retries）

如果你希望 HTTP 客户端在遇到 **客户端或服务器错误** 时自动重试请求，可以使用 `retry` 方法。
`retry` 方法接收两个参数：
1.  请求的最大尝试次数
2.  每次尝试之间 Laravel 应该等待的毫秒数

```php
$response = Http::retry(3, 100)->post(/* ... */);
```

如果你想要 **手动计算** 每次重试之间的休眠时间，可以将一个闭包作为第二个参数传递给 `retry` 方法：

```php
use Exception;

$response = Http::retry(3, function (int $attempt, Exception $exception) {
    return $attempt * 100;
})->post(/* ... */);
```

为了方便起见，你还可以将一个数组作为第一个参数传递给 `retry` 方法。这个数组会依次指定每次重试之间的等待时间（毫秒）：

```php
$response = Http::retry([100, 200])->post(/* ... */);
```

如果需要，你还可以传递一个 **第三个参数** 给 `retry` 方法。
第三个参数应当是一个可调用（callable），用于决定是否真正执行重试。
例如，你可能只希望在请求遇到 `ConnectionException` 时才进行重试：

```php
use Exception;
use Illuminate\Http\Client\PendingRequest;

$response = Http::retry(3, 100, function (Exception $exception, PendingRequest $request) {
    return $exception instanceof ConnectionException;
})->post(/* ... */);
```



如果一次请求尝试失败，你可能希望在新的尝试之前对请求做出更改。
你可以通过修改传递给 `retry` 方法的回调所提供的 `request` 参数来实现这一点。
例如，如果第一次尝试返回了认证错误，你可能希望使用一个新的授权令牌来重试该请求：

```php
use Exception;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\RequestException;

$response = Http::withToken($this->getToken())->retry(2, 0, function (Exception $exception, PendingRequest $request) {
    if (! $exception instanceof RequestException || $exception->response->status() !== 401) {
        return false;
    }

    $request->withToken($this->getNewToken());

    return true;
})->post(/* ... */);
```

如果所有请求都失败，将会抛出 `Illuminate\Http\Client\RequestException` 实例。
如果你希望禁用此行为，可以提供一个值为 `false` 的 `throw` 参数。
当禁用时，在所有重试尝试完成后，客户端将返回最后一次接收到的响应：

```php
$response = Http::retry(3, 100, throw: false)->post(/* ... */);
```

> [!警告]
> 如果所有请求由于连接问题而失败，即使 `throw` 参数设置为 `false`，仍然会抛出 `Illuminate\Http\Client\ConnectionException`。

### 错误处理（Error Handling）

与 Guzzle 的默认行为不同，Laravel 的 HTTP 客户端包装器不会在客户端或服务器错误时抛出异常（即服务器返回 `400` 和 `500` 级别响应）。
你可以使用 `successful`、`clientError` 或 `serverError` 方法来判断是否返回了这些错误：

```php
// 判断状态码是否 >= 200 且 < 300...
$response->successful();

// 判断状态码是否 >= 400...
$response->failed();

// 判断响应是否为 400 级别状态码...
$response->clientError();

// 判断响应是否为 500 级别状态码...
$response->serverError();

// 如果存在客户端或服务器错误，立即执行给定的回调...
$response->onError(callable $callback);
```



#### 抛出异常（Throwing Exceptions）

如果你有一个响应实例，并且希望在响应状态码表示客户端或服务器错误时抛出一个 `Illuminate\Http\Client\RequestException` 实例，你可以使用 `throw` 或 `throwIf` 方法：

```php
use Illuminate\Http\Client\Response;

$response = Http::post(/* ... */);

// 如果发生了客户端或服务器错误，则抛出异常...
$response->throw();

// 如果发生错误并且给定条件为 true，则抛出异常...
$response->throwIf($condition);

// 如果发生错误并且给定闭包解析为 true，则抛出异常...
$response->throwIf(fn (Response $response) => true);

// 如果发生错误并且给定条件为 false，则抛出异常...
$response->throwUnless($condition);

// 如果发生错误并且给定闭包解析为 false，则抛出异常...
$response->throwUnless(fn (Response $response) => false);

// 如果响应具有特定的状态码，则抛出异常...
$response->throwIfStatus(403);

// 除非响应具有特定的状态码，否则抛出异常...
$response->throwUnlessStatus(200);

return $response['user']['id'];
```

`Illuminate\Http\Client\RequestException` 实例具有一个公共的 `$response` 属性，允许你检查返回的响应。

如果没有错误发生，`throw` 方法将返回响应实例，从而允许你在 `throw` 方法后链式调用其他操作：

```php
return Http::post(/* ... */)->throw()->json();
```

如果你希望在异常被抛出之前执行一些额外的逻辑，可以将一个闭包传递给 `throw` 方法。
在闭包被调用之后，异常将会自动抛出，因此你不需要在闭包内部重新抛出异常：

```php
use Illuminate\Http\Client\Response;
use Illuminate\Http\Client\RequestException;

return Http::post(/* ... */)->throw(function (Response $response, RequestException $e) {
    // ...
})->json();
```



默认情况下，`RequestException` 消息在被记录或报告时会被截断为 120 个字符。
要自定义或禁用这种行为，你可以在应用的 `bootstrap/app.php` 文件中配置异常处理行为时，使用 `truncateRequestExceptionsAt` 和 `dontTruncateRequestExceptions` 方法：

```php
use Illuminate\Foundation\Configuration\Exceptions;

->withExceptions(function (Exceptions $exceptions) {
    // 将请求异常消息截断为 240 个字符...
    $exceptions->truncateRequestExceptionsAt(240);

    // 禁用请求异常消息截断...
    $exceptions->dontTruncateRequestExceptions();
})
```

### Guzzle 中间件（Guzzle Middleware）

由于 Laravel 的 HTTP 客户端是由 Guzzle 驱动的，因此你可以利用 [Guzzle Middleware](https://docs.guzzlephp.org/en/stable/handlers-and-middleware.html) 来操作发出的请求或检查传入的响应。
要操作发出的请求，可以通过 `withRequestMiddleware` 方法注册一个 Guzzle 中间件：

```php
use Illuminate\Support\Facades\Http;
use Psr\Http\Message\RequestInterface;

$response = Http::withRequestMiddleware(
    function (RequestInterface $request) {
        return $request->withHeader('X-Example', 'Value');
    }
)->get('http://example.com');
```

同样地，你可以通过 `withResponseMiddleware` 方法注册一个中间件来检查传入的 HTTP 响应：

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

#### 全局中间件（Global Middleware）

有时，你可能希望注册一个适用于**每一个**发出的请求和传入的响应的中间件。
要实现这一点，可以使用 `globalRequestMiddleware` 和 `globalResponseMiddleware` 方法。
通常，这些方法应该在应用的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Http;

Http::globalRequestMiddleware(fn ($request) => $request->withHeader(
    'User-Agent', 'Example Application/1.0'
));

Http::globalResponseMiddleware(fn ($response) => $response->withHeader(
    'X-Finished-At', now()->toDateTimeString()
));
```



### Guzzle 选项（Guzzle Options）

你可以使用 `withOptions` 方法为发出的请求指定额外的 [Guzzle 请求选项](http://docs.guzzlephp.org/en/stable/request-options.html)。
`withOptions` 方法接收一个键/值对数组：

```php
$response = Http::withOptions([
    'debug' => true,
])->get('http://example.com/users');
```

#### 全局选项（Global Options）

要为每一个发出的请求配置默认选项，你可以使用 `globalOptions` 方法。
通常，这个方法应该在应用的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Http;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Http::globalOptions([
        'allow_redirects' => false,
    ]);
}
```

## 并发请求（Concurrent Requests）

有时，你可能希望同时发出多个 HTTP 请求。换句话说，你希望在同一时间派发多个请求，而不是顺序一个接一个地发出。
这样做在与缓慢的 HTTP API 交互时，可以带来显著的性能提升。

幸运的是，你可以通过 `pool` 方法实现。
`pool` 方法接收一个闭包，该闭包会接收一个 `Illuminate\Http\Client\Pool` 实例，使你可以轻松地将请求加入请求池进行派发：

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

如你所见，每个响应实例都可以根据它被添加到请求池的顺序来访问。
如果你愿意，你可以使用 `as` 方法为请求命名，这样你就可以通过名称来访问对应的响应：

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



#### 自定义并发请求（Customizing Concurrent Requests）

`pool` 方法不能与其他 HTTP 客户端方法（例如 `withHeaders` 或 `middleware` 方法）进行链式调用。
如果你想为池中的请求应用自定义头部或中间件，你应该在池中的每个请求上单独配置这些选项：

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

## 宏（Macros）

Laravel 的 HTTP 客户端允许你定义 “宏”（macros），它可以作为一种流畅、富有表现力的机制，在应用中与服务交互时配置常见的请求路径和头部。
首先，你可以在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中定义宏：

```php
use Illuminate\Support\Facades\Http;

/**
 * 启动任何应用服务
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

一旦宏被配置，你就可以在应用的任何地方调用它，用指定的配置创建一个待发送请求：

```php
$response = Http::github()->get('/');
```

## 测试（Testing）

许多 Laravel 服务都提供了帮助你轻松、富有表现力地编写测试的功能，Laravel 的 HTTP 客户端也不例外。
`Http` facade 的 `fake` 方法允许你指示 HTTP 客户端在发出请求时返回伪造/虚拟响应。



### 伪造响应（Faking Responses）

例如，要指示 HTTP 客户端对每一个请求都返回空的 `200` 状态码响应，你可以在不传递任何参数的情况下调用 `fake` 方法：

```php
use Illuminate\Support\Facades\Http;

Http::fake();

$response = Http::post(/* ... */);
```

#### 伪造特定 URL（Faking Specific URLs）

或者，你也可以向 `fake` 方法传递一个数组。
数组的键应该表示你想要伪造的 URL 模式，值则是对应的响应。
`*` 字符可以用作通配符。
任何未被伪造的 URL 请求将会实际执行。
你可以使用 `Http` facade 的 `response` 方法为这些端点构造存根 / 伪造响应：

```php
Http::fake([
    // 为 GitHub 端点伪造一个 JSON 响应...
    'github.com/*' => Http::response(['foo' => 'bar'], 200, $headers),

    // 为 Google 端点伪造一个字符串响应...
    'google.com/*' => Http::response('Hello World', 200, $headers),
]);
```

如果你想指定一个后备的 URL 模式来为所有未匹配的 URL 提供存根，你可以使用单个 `*` 字符：

```php
Http::fake([
    // 为 GitHub 端点伪造一个 JSON 响应...
    'github.com/*' => Http::response(['foo' => 'bar'], 200, ['Headers']),

    // 为所有其他端点伪造一个字符串响应...
    '*' => Http::response('Hello World', 200, ['Headers']),
]);
```

为了方便起见，你也可以通过直接传递字符串、数组或整数作为响应来生成简单的字符串、JSON 或空响应：

```php
Http::fake([
    'google.com/*' => 'Hello World',
    'github.com/*' => ['foo' => 'bar'],
    'chatgpt.com/*' => 200,
]);
```

#### 伪造异常（Faking Exceptions）

有时候你可能需要测试应用在 HTTP 客户端尝试发起请求时遇到 `Illuminate\Http\Client\ConnectionException` 的行为。
你可以使用 `failedConnection` 方法指示 HTTP 客户端抛出一个连接异常：

```php
Http::fake([
    'github.com/*' => Http::failedConnection(),
]);
```



要测试应用在抛出 `Illuminate\Http\Client\RequestException` 时的行为，你可以使用 `failedRequest` 方法：

```php
Http::fake([
    'github.com/*' => Http::failedRequest(['code' => 'not_found'], 404),
]);
```

#### 伪造响应序列（Faking Response Sequences）

有时你可能需要指定某个 URL 在特定顺序下返回一系列伪造的响应。
你可以使用 `Http::sequence` 方法来构建这些响应：

```php
Http::fake([
     // 为 GitHub 端点存根一系列响应...
    'github.com/*' => Http::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->pushStatus(404),
]);
```

当一个响应序列中的所有响应都被消耗完后，任何进一步的请求都会导致该响应序列抛出异常。
如果你想指定一个在序列为空时应返回的默认响应，可以使用 `whenEmpty` 方法：

```php
Http::fake([
    // 为 GitHub 端点存根一系列响应...
    'github.com/*' => Http::sequence()
        ->push('Hello World', 200)
        ->push(['foo' => 'bar'], 200)
        ->whenEmpty(Http::response()),
]);
```

如果你想伪造一系列响应，但又不需要指定一个特定的 URL 模式，可以使用 `Http::fakeSequence` 方法：

```php
Http::fakeSequence()
    ->push('Hello World', 200)
    ->whenEmpty(Http::response());
```

#### 伪造回调（Fake Callback）

如果你需要更复杂的逻辑来决定某些端点应返回什么响应，你可以向 `fake` 方法传递一个闭包。
这个闭包会接收一个 `Illuminate\Http\Client\Request` 实例，并且需要返回一个响应实例。
在闭包中，你可以执行任何必要的逻辑来决定返回哪种响应：

```php
use Illuminate\Http\Client\Request;

Http::fake(function (Request $request) {
    return Http::response('Hello World', 200);
});
```



### 防止未预期的请求（Preventing Stray Requests）

如果你想确保在单个测试或整个测试套件中，通过 HTTP 客户端发送的所有请求都被伪造，可以调用 `preventStrayRequests` 方法。
调用此方法后，任何没有对应伪造响应的请求都会抛出异常，而不会进行实际的 HTTP 请求：

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

### 检查请求（Inspecting Requests）

在伪造响应时，你有时希望检查客户端收到的请求，以确保你的应用发送了正确的数据或请求头。
你可以在调用 `Http::fake` 之后，通过调用 `Http::assertSent` 方法实现这一点。

`assertSent` 方法接受一个闭包，该闭包会接收一个 `Illuminate\Http\Client\Request` 实例，并应该返回布尔值，表示请求是否符合你的期望。
为了让测试通过，至少必须有一个请求匹配给定的期望：

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

如果需要，你也可以使用 `assertNotSent` 方法来断言某个特定请求未被发送：

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



你可以使用 `assertSentCount` 方法来断言在测试期间“发送”的请求数量：

```php
Http::fake();

Http::assertSentCount(5);
```

或者，你可以使用 `assertNothingSent` 方法来断言在测试期间没有请求被发送：

```php
Http::fake();

Http::assertNothingSent();
```

#### 记录请求 / 响应（Recording Requests / Responses）

你可以使用 `recorded` 方法收集所有请求及其对应的响应。
`recorded` 方法返回一个数组集合，每个数组包含 `Illuminate\Http\Client\Request` 和 `Illuminate\Http\Client\Response` 实例：

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

此外，`recorded` 方法也可以接受一个闭包，该闭包会接收 `Illuminate\Http\Client\Request` 和 `Illuminate\Http\Client\Response` 实例，并可用于根据你的期望筛选请求 / 响应对：

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

## 事件（Events）

Laravel 在发送 HTTP 请求的过程中会触发三个事件：
1.  `RequestSending` — 请求发送前触发。
2.  `ResponseReceived` — 收到响应后触发。
3.  `ConnectionFailed` — 如果请求未收到响应则触发。
-   `RequestSending` 和 `ConnectionFailed` 事件都包含公共 `$request` 属性，可用于检查 `Illuminate\Http\Client\Request` 实例。
-   `ResponseReceived` 事件包含 `$request` 和 `$response` 属性，可用于检查 `Illuminate\Http\Client\Response` 实例。
你可以在应用中为这些事件创建 [事件监听器](/docs/laravel/12.x/events)：

```php
use Illuminate\Http\Client\Events\RequestSending;

class LogRequest
{
    /**
     * 处理事件
     */
    public function handle(RequestSending $event): void
    {
        // $event->request ...
    }
}
```

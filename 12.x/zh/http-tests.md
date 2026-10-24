
# HTTP 测试

- [简介](#introduction)
- [发起请求](#making-requests)
    - [自定义请求头](#customizing-request-headers)
    - [Cookies](#cookies)
    - [会话 / 身份验证](#session-and-authentication)
    - [调试响应](#debugging-responses)
    - [异常处理](#exception-handling)
- [测试 JSON API](#testing-json-apis)
    - [流式 JSON 测试](#fluent-json-testing)
- [测试文件上传](#testing-file-uploads)
- [测试视图](#testing-views)
    - [渲染 Blade 与组件](#rendering-blade-and-components)
- [可用断言](#available-assertions)
    - [响应断言](#response-assertions)
    - [身份验证断言](#authentication-assertions)
    - [验证断言](#validation-assertions)
## 简介

Laravel 提供了非常流畅的 API，用于对你的应用发起 HTTP 请求并检查响应结果。例如，以下是一个基础功能测试的示例：

```php tab=Pest
<?php

test('the application returns a successful response', function () {
    $response = $this->get('/');

    $response->assertStatus(200);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基础测试示例。
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }
}
```

这里的 `get` 方法是向应用程序发起一个 GET 请求，而 `assertStatus` 方法断言返回的响应状态码应为 200。

除了这个简单的断言外，Laravel 还提供了多种用于检查响应头、响应内容、JSON 结构等的断言方法。

## 发起请求

在测试中你可以使用 `get`、`post`、`put`、`patch` 或 `delete` 方法向应用发起请求。

这些方法并不会真正通过网络发送 HTTP 请求，而是 **在内部模拟整个请求流程**，因此测试非常快速且不依赖外部服务。



Laravel 中的测试请求方法并不会返回 `Illuminate\Http\Response` 实例，而是返回 `Illuminate\Testing\TestResponse` 实例。这个类提供了[多种有用的断言方法](#available-assertions)，便于你检查应用程序的响应内容：

```php tab=Pest
<?php

test('basic request', function () {
    $response = $this->get('/');

    $response->assertStatus(200);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基础的测试示例。
     */
    public function test_a_basic_request(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }
}
```

通常来说，每个测试方法中应该只对应用发起一次请求。如果在一个测试方法中发起多个请求，可能会导致意料之外的行为。

> 为了测试方便，Laravel 在运行测试时会自动禁用 CSRF 中间件。

### 自定义请求头

你可以使用 `withHeaders` 方法，在请求发送前自定义请求头。这允许你为请求添加任何你想要的自定义 Header：

```php tab=Pest
<?php

test('interacting with headers', function () {
    $response = $this->withHeaders([
        'X-Header' => 'Value',
    ])->post('/user', ['name' => 'Sally']);

    $response->assertStatus(201);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个带有请求头的功能测试。
     */
    public function test_interacting_with_headers(): void
    {
        $response = $this->withHeaders([
            'X-Header' => 'Value',
        ])->post('/user', ['name' => 'Sally']);

        $response->assertStatus(201);
    }
}
```

<a name="cookies"></a>
### Cookies

你可以使用 `withCookie` 或 `withCookies` 方法，在发起请求前设置 Cookie。
-   `withCookie(name, value)` 方法接收 Cookie 名称和值两个参数；
-   `withCookies([key => value])` 方法则接收一个键值对数组：

```php tab=Pest
<?php

test('interacting with cookies', function () {
    $response = $this->withCookie('color', 'blue')->get('/');

    $response = $this->withCookies([
        'color' => 'blue',
        'name' => 'Taylor',
    ])->get('/');

    //
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_interacting_with_cookies(): void
    {
        $response = $this->withCookie('color', 'blue')->get('/');

        $response = $this->withCookies([
            'color' => 'blue',
            'name' => 'Taylor',
        ])->get('/');

        //
    }
}
```



### 会话 / 身份验证

Laravel 提供了多个辅助方法，用于在 HTTP 测试期间与会话进行交互。首先，你可以使用 `withSession` 方法设置会话数据。这个方法在你发起请求之前，预先将数据写入会话非常有用：

```php tab=Pest
<?php

test('interacting with the session', function () {
    $response = $this->withSession(['banned' => false])->get('/');

    //
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_interacting_with_the_session(): void
    {
        $response = $this->withSession(['banned' => false])->get('/');

        //
    }
}
```

Laravel 的会话通常用于维护当前已认证用户的状态。因此，`actingAs` 辅助方法提供了一个简单的方式，用于将指定用户设置为当前登录用户。例如，我们可以使用 [模型工厂](/docs/laravel/12.x/eloquent-factories) 来生成并认证一个用户：

```php tab=Pest
<?php

use App\Models\User;

test('an action that requires authentication', function () {
    $user = User::factory()->create();

    $response = $this->actingAs($user)
        ->withSession(['banned' => false])
        ->get('/');

    //
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Models\User;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_an_action_that_requires_authentication(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)
            ->withSession(['banned' => false])
            ->get('/');

        //
    }
}
```

你还可以通过 `actingAs` 方法的第二个参数指定使用的 guard 名称。指定的 guard 会在当前测试生命周期内成为默认 guard：

```php
$this->actingAs($user, 'web')
```



### 调试响应

在向应用程序发起测试请求之后，可以使用 `dump`、`dumpHeaders` 和 `dumpSession` 方法来查看和调试响应的内容：

```php tab=Pest
<?php

test('basic test', function () {
    $response = $this->get('/');

    $response->dumpHeaders();

    $response->dumpSession();

    $response->dump();
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基本的测试示例。
     */
    public function test_basic_test(): void
    {
        $response = $this->get('/');

        $response->dumpHeaders();

        $response->dumpSession();

        $response->dump();
    }
}
```

你也可以使用 `dd` 系列方法来输出响应信息并立即终止测试执行：
-   `dd()`：输出整个响应
-   `ddHeaders()`：输出响应头
-   `ddBody()`：输出原始响应体
-   `ddJson()`：格式化输出 JSON 响应体
-   `ddSession()`：输出当前会话内容

```php tab=Pest
<?php

test('basic test', function () {
    $response = $this->get('/');

    $response->dd();
    $response->ddHeaders();
    $response->ddBody();
    $response->ddJson();
    $response->ddSession();
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基本的测试示例。
     */
    public function test_basic_test(): void
    {
        $response = $this->get('/');

        $response->dd();
        $response->ddHeaders();
        $response->ddBody();
        $response->ddJson();
        $response->ddSession();
    }
}
```

### 异常处理

有时，你可能需要测试你的应用程序是否抛出了某个特定的异常。你可以通过 Laravel 提供的 `Exceptions` facade 来“伪造”异常处理器，从而捕获异常并断言它的内容。

一旦异常处理器被伪造，你就可以使用 `assertReported` 或 `assertNotReported` 方法断言某个异常是否已被抛出并报告：

```php tab=Pest
<?php

use App\Exceptions\InvalidOrderException;
use Illuminate\Support\Facades\Exceptions;

test('exception is thrown', function () {
    Exceptions::fake();

    $response = $this->get('/order/1');

    // 断言已抛出指定类型的异常
    Exceptions::assertReported(InvalidOrderException::class);

    // 使用闭包断言异常详情
    Exceptions::assertReported(function (InvalidOrderException $e) {
        return $e->getMessage() === 'The order was invalid.';
    });
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Exceptions\InvalidOrderException;
use Illuminate\Support\Facades\Exceptions;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基本的测试示例。
     */
    public function test_exception_is_thrown(): void
    {
        Exceptions::fake();

        $response = $this->get('/');

        // 断言已抛出指定类型的异常
        Exceptions::assertReported(InvalidOrderException::class);

         // 使用闭包断言异常内容
        Exceptions::assertReported(function (InvalidOrderException $e) {
            return $e->getMessage() === 'The order was invalid.';
        });
    }
}
```



`assertNotReported` 和 `assertNothingReported` 方法可用于断言请求期间未抛出给定异常或没有抛出任何异常：

```php
Exceptions::assertNotReported(InvalidOrderException::class);

Exceptions::assertNothingReported();
```

你可以通过在发出请求之前调用 `withoutExceptionHandling` 方法来完全禁用给定请求的异常处理：

```php
$response = $this->withoutExceptionHandling()->get('/');
```

此外，如果你希望确保你的应用程序未使用 PHP 语言或其使用的库中已弃用的功能，你可以在发出请求之前调用 `withoutDeprecationHandling` 方法。禁用弃用处理时，弃用警告将被转换为异常，从而导致你的测试失败：

```php
$response = $this->withoutDeprecationHandling()->get('/');
```

`assertThrows` 方法可用于断言给定闭包中的代码抛出了指定类型的异常：

```php
$this->assertThrows(
    fn () => (new ProcessOrder)->execute(),
    OrderInvalid::class
);
```

如果你希望检查并对所抛出的异常进行断言，可以将闭包作为 `assertThrows` 方法的第二个参数传入：

```php
$this->assertThrows(
    fn () => (new ProcessOrder)->execute(),
    fn (OrderInvalid $e) => $e->orderId() === 123;
);
```

`assertDoesntThrow` 方法可用于断言给定闭包中的代码未抛出任何异常：

```php
$this->assertDoesntThrow(fn () => (new ProcessOrder)->execute());
```

## 测试 JSON API

Laravel 还提供了一些辅助方法用于测试 JSON API 及其响应。例如，`json`、`getJson`、`postJson`、`putJson`、`patchJson`、`deleteJson` 和 `optionsJson` 方法可用于使用不同的 HTTP 动词发出 JSON 请求。你还可以轻松地向这些方法传递数据和头信息。让我们从编写一个测试开始，该测试向 `/api/user` 发出 `POST` 请求，并断言返回了预期的 JSON 数据：

```php tab=Pest
<?php

test('making an api request', function () {
    $response = $this->postJson('/api/user', ['name' => 'Sally']);

    $response
        ->assertStatus(201)
        ->assertJson([
            'created' => true,
        ]);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基本的功能测试示例。
     */
    public function test_making_an_api_request(): void
    {
        $response = $this->postJson('/api/user', ['name' => 'Sally']);

        $response
            ->assertStatus(201)
            ->assertJson([
                'created' => true,
            ]);
    }
}
```



此外，JSON 响应数据可以像数组变量一样在响应中访问，这让你可以方便地检查 JSON 响应中返回的各个值：

```php tab=Pest
expect($response['created'])->toBeTrue();
```

```php tab=PHPUnit
$this->assertTrue($response['created']);
```

> `assertJson` 方法会将响应转换为数组，以验证所提供的数组是否存在于应用返回的 JSON 响应中。因此，即使 JSON 响应中还有其他属性，只要提供的片段存在，测试也会通过。

#### 断言精确的 JSON 匹配

如前所述，`assertJson` 方法可用于断言 JSON 响应中包含某个 JSON 片段。如果你希望验证指定数组 **与应用返回的 JSON 完全一致**，则应使用 `assertExactJson` 方法：

```php tab=Pest
<?php

test('asserting an exact json match', function () {
    $response = $this->postJson('/user', ['name' => 'Sally']);

    $response
        ->assertStatus(201)
        ->assertExactJson([
            'created' => true,
        ]);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基础功能测试示例。
     */
    public function test_asserting_an_exact_json_match(): void
    {
        $response = $this->postJson('/user', ['name' => 'Sally']);

        $response
            ->assertStatus(201)
            ->assertExactJson([
                'created' => true,
            ]);
    }
}
```

#### 断言 JSON 路径的值

如果你希望验证 JSON 响应中指定路径上的数据值，可以使用 `assertJsonPath` 方法：

```php tab=Pest
<?php

test('asserting a json path value', function () {
    $response = $this->postJson('/user', ['name' => 'Sally']);

    $response
        ->assertStatus(201)
        ->assertJsonPath('team.owner.name', 'Darian');
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基础功能测试示例。
     */
    public function test_asserting_a_json_paths_value(): void
    {
        $response = $this->postJson('/user', ['name' => 'Sally']);

        $response
            ->assertStatus(201)
            ->assertJsonPath('team.owner.name', 'Darian');
    }
}
```



`assertJsonPath` 方法也接受闭包，该闭包可用于动态判断断言是否应通过：

```php
$response->assertJsonPath('team.owner.name', fn (string $name) => strlen($name) >= 3);
```

### Fluent JSON 测试

Laravel 也提供了一种优雅的方式来以链式方式测试应用程序的 JSON 响应。要开始使用，请将一个闭包传递给 `assertJson` 方法。该闭包将被传入一个 `Illuminate\Testing\Fluent\AssertableJson` 的实例，可用于对返回的 JSON 进行断言。
`where` 方法可用于对 JSON 的特定属性进行断言，而 `missing` 方法可用于断言某个属性在 JSON 中缺失：

```php tab=Pest
use Illuminate\Testing\Fluent\AssertableJson;

test('fluent json', function () {
    $response = $this->getJson('/users/1');

    $response
        ->assertJson(fn (AssertableJson $json) =>
            $json->where('id', 1)
                ->where('name', 'Victoria Faith')
                ->where('email', fn (string $email) => str($email)->is('victoria@gmail.com'))
                ->whereNot('status', 'pending')
                ->missing('password')
                ->etc()
        );
});
```

```php tab=PHPUnit
use Illuminate\Testing\Fluent\AssertableJson;

/**
 * A basic functional test example.
 */
public function test_fluent_json(): void
{
    $response = $this->getJson('/users/1');

    $response
        ->assertJson(fn (AssertableJson $json) =>
            $json->where('id', 1)
                ->where('name', 'Victoria Faith')
                ->where('email', fn (string $email) => str($email)->is('victoria@gmail.com'))
                ->whereNot('status', 'pending')
                ->missing('password')
                ->etc()
        );
}
```

#### 理解 etc 方法

在上面的示例中，你可能注意到我们在断言链的结尾调用了 `etc` 方法。此方法告知 Laravel，在该 JSON 对象中可能还存在其他属性。
如果不使用 `etc` 方法，那么如果该 JSON 对象中存在你未进行断言的其他属性，测试将会失败。




该行为背后的意图是为了防止你在 JSON 响应中无意间暴露敏感信息，方法是强制你要么显式地对属性进行断言，要么通过 `etc` 方法显式允许额外的属性。

然而，你需要注意，不在断言链中包含 `etc` 方法**并不能**确保在嵌套于 JSON 对象内部的数组中不会添加额外属性。`etc` 方法**仅确保在调用该方法的嵌套层级中不存在额外属性**。

#### 断言属性的存在 / 缺失

要断言某个属性是否存在或缺失，你可以使用 `has` 和 `missing` 方法：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->has('data')
        ->missing('message')
);
```

此外，`hasAll` 和 `missingAll` 方法允许你同时断言多个属性的存在或缺失

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->hasAll(['status', 'data'])
        ->missingAll(['message', 'code'])
);
```

你可以使用 `hasAny` 方法来判断指定的一组属性中是否**至少有一个**存在：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->has('status')
        ->hasAny('data', 'message', 'code')
);
```

#### 针对 JSON 集合进行断言

通常，你的路由会返回包含多个项目的 JSON 响应，比如多个用户：

```php
Route::get('/users', function () {
    return User::all();
});
```

在这种情况下，我们可以使用 Fluent JSON 对象的 `has` 方法，对响应中包含的用户进行断言。例如，我们可以断言该 JSON 响应包含三个用户。接着，我们使用 `first` 方法对集合中的第一个用户进行断言。`first` 方法接受一个闭包，该闭包会接收另一个可用于断言的 JSON 字符串对象，用于对 JSON 集合中的第一个对象进行断言：

```php
$response
    ->assertJson(fn (AssertableJson $json) =>
        $json->has(3)
            ->first(fn (AssertableJson $json) =>
                $json->where('id', 1)
                    ->where('name', 'Victoria Faith')
                    ->where('email', fn (string $email) => str($email)->is('victoria@gmail.com'))
                    ->missing('password')
                    ->etc()
            )
    );
```



#### 为 JSON 集合设置作用域断言

有时，你的应用路由会返回包含命名键的 JSON 集合，例如：

```php
Route::get('/users', function () {
    return [
        'meta' => [...],
        'users' => User::all(),
    ];
})
```

在测试这些路由时，你可以使用 `has` 方法断言集合中的项数。此外，还可以通过 `has` 方法为一系列断言设定作用域：

```php
$response
    ->assertJson(fn (AssertableJson $json) =>
        $json->has('meta')
            ->has('users', 3)
            ->has('users.0', fn (AssertableJson $json) =>
                $json->where('id', 1)
                    ->where('name', 'Victoria Faith')
                    ->where('email', fn (string $email) => str($email)->is('victoria@gmail.com'))
                    ->missing('password')
                    ->etc()
            )
    );
```

不过，与其使用两个 `has` 方法来分别断言 `users` 集合的项数和第一项的属性，不如在一次 `has` 调用中传入第三个参数（闭包），此时该闭包将自动作用于集合中的第一项：

```php
$response
    ->assertJson(fn (AssertableJson $json) =>
        $json->has('meta')
            ->has('users', 3, fn (AssertableJson $json) =>
                $json->where('id', 1)
                    ->where('name', 'Victoria Faith')
                    ->where('email', fn (string $email) => str($email)->is('victoria@gmail.com'))
                    ->missing('password')
                    ->etc()
            )
    );
```

#### 断言 JSON 属性类型

你可能只想断言 JSON 响应中属性的类型是否符合预期。`Illuminate\Testing\Fluent\AssertableJson` 类提供了 `whereType` 和 `whereAllType` 方法来实现这一点：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->whereType('id', 'integer')
        ->whereAllType([
            'users.0.name' => 'string',
            'meta' => 'array'
        ])
);
```



你可以使用 `|` 字符指定多个类型，或者将类型数组作为第二个参数传递给 `whereType` 方法。只要响应值匹配其中任意一个类型，断言就会通过：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->whereType('name', 'string|null')
        ->whereType('id', ['string', 'integer'])
);
```

`whereType` 和 `whereAllType` 方法支持以下类型：`string`、`integer`、`double`、`boolean`、`array` 和 `null`。

## 测试文件上传

`Illuminate\Http\UploadedFile` 类提供了一个 `fake` 方法，可以用于生成测试用的假文件或图片。该方法通常与 `Storage` facade 的 `fake` 方法搭配使用，从而极大简化了文件上传功能的测试流程。例如，下面的代码就可以轻松测试头像上传表单：

```php tab=Pest
<?php

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

test('avatars can be uploaded', function () {
    Storage::fake('avatars');

    $file = UploadedFile::fake()->image('avatar.jpg');

    $response = $this->post('/avatar', [
        'avatar' => $file,
    ]);

    Storage::disk('avatars')->assertExists($file->hashName());
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_avatars_can_be_uploaded(): void
    {
        Storage::fake('avatars');

        $file = UploadedFile::fake()->image('avatar.jpg');

        $response = $this->post('/avatar', [
            'avatar' => $file,
        ]);

        Storage::disk('avatars')->assertExists($file->hashName());
    }
}
```

如果你想断言某个文件不存在，可以使用 `Storage` facade 提供的 `assertMissing` 方法：

```php
Storage::fake('avatars');

// ...

Storage::disk('avatars')->assertMissing('missing.jpg');
```



#### 虚拟文件的自定义

使用 `UploadedFile` 类提供的 `fake` 方法创建文件时，你可以指定图像的宽度、高度以及文件大小（以 KB 为单位），以便更好地测试应用程序的验证规则：

```php
UploadedFile::fake()->image('avatar.jpg', $width, $height)->size(100);
```

除了创建图片之外，你还可以使用 `create` 方法创建任意类型的文件：

```php
UploadedFile::fake()->create('document.pdf', $sizeInKilobytes);
```

如有需要，你还可以传递 `$mimeType` 参数来显式指定该文件返回的 MIME 类型：


```php
UploadedFile::fake()->create(
    'document.pdf', $sizeInKilobytes, 'application/pdf'
);
```

## 测试视图

Laravel 还允许你在不发起模拟 HTTP 请求的前提下渲染视图。在测试中，你可以通过调用 `view` 方法来完成这一操作。该方法接受视图名称及一个可选的数据数组，并返回一个 `Illuminate\Testing\TestView` 实例，该实例提供了一些便捷的方法来对视图内容进行断言：

```php tab=Pest
<?php

test('a welcome view can be rendered', function () {
    $view = $this->view('welcome', ['name' => 'Taylor']);

    $view->assertSee('Taylor');
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_a_welcome_view_can_be_rendered(): void
    {
        $view = $this->view('welcome', ['name' => 'Taylor']);

        $view->assertSee('Taylor');
    }
}
```

`TestView` 类提供了以下断言方法：
-   `assertSee`
-   `assertSeeInOrder`
-   `assertSeeText`
-   `assertSeeTextInOrder`
-   `assertDontSee`
-   `assertDontSeeText`

如有需要，你还可以通过将 `TestView` 实例强制转换为字符串来获取原始渲染后的视图内容：
```php
$contents = (string) $this->view('welcome');
```



#### 共享错误

某些视图可能依赖于 [Laravel 提供的全局错误包](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors)。你可以使用 `withViewErrors` 方法为错误包注入错误信息：

```php
$view = $this->withViewErrors([
    'name' => ['Please provide a valid name.']
])->view('form');

$view->assertSee('Please provide a valid name.');
```

### 渲染 Blade 和组件

如有需要，你可以使用 `blade` 方法来解析并渲染一段原始的 [Blade 模板字符串](/docs/laravel/12.x/blade)。与 `view` 方法类似，`blade` 方法返回 `Illuminate\Testing\TestView` 实例：

```php
$view = $this->blade(
    '<x-component :name="$name" />',
    ['name' => 'Taylor']
);

$view->assertSee('Taylor');
```

你也可以使用 `component` 方法来渲染一个 [Blade 组件](/docs/laravel/12.x/blade#components)。该方法返回一个 `Illuminate\Testing\TestComponent` 实例：

```php
$view = $this->component(Profile::class, ['name' => 'Taylor']);

$view->assertSee('Taylor');
```

## 可用的断言方法

### 响应断言

Laravel 的 `Illuminate\Testing\TestResponse` 类提供了丰富的自定义断言方法，可用于测试应用程序的 HTTP 响应。这些断言方法可以通过 `json`、`get`、`post`、`put` 和 `delete` 测试方法返回的响应对象进行调用。

<style>
    .collection-method-list > p {
        columns: 14.4em 2; -moz-columns: 14.4em 2; -webkit-columns: 14.4em 2;
    }

    .collection-method-list a {
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
</style>

<div class="collection-method-list" markdown="1">

[assertAccepted](#assert-accepted)
[assertBadRequest](#assert-bad-request)
[assertClientError](#assert-client-error)
[assertConflict](#assert-conflict)
[assertCookie](#assert-cookie)
[assertCookieExpired](#assert-cookie-expired)
[assertCookieNotExpired](#assert-cookie-not-expired)
[assertCookieMissing](#assert-cookie-missing)
[assertCreated](#assert-created)
[assertDontSee](#assert-dont-see)
[assertDontSeeText](#assert-dont-see-text)
[assertDownload](#assert-download)
[assertExactJson](#assert-exact-json)
[assertExactJsonStructure](#assert-exact-json-structure)
[assertForbidden](#assert-forbidden)
[assertFound](#assert-found)
[assertGone](#assert-gone)
[assertHeader](#assert-header)
[assertHeaderMissing](#assert-header-missing)
[assertInternalServerError](#assert-internal-server-error)
[assertJson](#assert-json)
[assertJsonCount](#assert-json-count)
[assertJsonFragment](#assert-json-fragment)
[assertJsonIsArray](#assert-json-is-array)
[assertJsonIsObject](#assert-json-is-object)
[assertJsonMissing](#assert-json-missing)
[assertJsonMissingExact](#assert-json-missing-exact)
[assertJsonMissingValidationErrors](#assert-json-missing-validation-errors)
[assertJsonPath](#assert-json-path)
[assertJsonMissingPath](#assert-json-missing-path)
[assertJsonStructure](#assert-json-structure)
[assertJsonValidationErrors](#assert-json-validation-errors)
[assertJsonValidationErrorFor](#assert-json-validation-error-for)
[assertLocation](#assert-location)
[assertMethodNotAllowed](#assert-method-not-allowed)
[assertMovedPermanently](#assert-moved-permanently)
[assertContent](#assert-content)
[assertNoContent](#assert-no-content)
[assertStreamed](#assert-streamed)
[assertStreamedContent](#assert-streamed-content)
[assertNotFound](#assert-not-found)
[assertOk](#assert-ok)
[assertPaymentRequired](#assert-payment-required)
[assertPlainCookie](#assert-plain-cookie)
[assertRedirect](#assert-redirect)
[assertRedirectBack](#assert-redirect-back)
[assertRedirectContains](#assert-redirect-contains)
[assertRedirectToRoute](#assert-redirect-to-route)
[assertRedirectToSignedRoute](#assert-redirect-to-signed-route)
[assertRequestTimeout](#assert-request-timeout)
[assertSee](#assert-see)
[assertSeeInOrder](#assert-see-in-order)
[assertSeeText](#assert-see-text)
[assertSeeTextInOrder](#assert-see-text-in-order)
[assertServerError](#assert-server-error)
[assertServiceUnavailable](#assert-service-unavailable)
[assertSessionHas](#assert-session-has)
[assertSessionHasInput](#assert-session-has-input)
[assertSessionHasAll](#assert-session-has-all)
[assertSessionHasErrors](#assert-session-has-errors)
[assertSessionHasErrorsIn](#assert-session-has-errors-in)
[assertSessionHasNoErrors](#assert-session-has-no-errors)
[assertSessionDoesntHaveErrors](#assert-session-doesnt-have-errors)
[assertSessionMissing](#assert-session-missing)
[assertStatus](#assert-status)
[assertSuccessful](#assert-successful)
[assertTooManyRequests](#assert-too-many-requests)
[assertUnauthorized](#assert-unauthorized)
[assertUnprocessable](#assert-unprocessable)
[assertUnsupportedMediaType](#assert-unsupported-media-type)
[assertValid](#assert-valid)
[assertInvalid](#assert-invalid)
[assertViewHas](#assert-view-has)
[assertViewHasAll](#assert-view-has-all)
[assertViewIs](#assert-view-is)
[assertViewMissing](#assert-view-missing)

</div>



#### assertAccepted

断言响应的 HTTP 状态码为 202 Accepted（已接受）：

```php
$response->assertAccepted();
```

#### assertBadRequest

断言响应的 HTTP 状态码为 400 Bad Request（错误请求）：

```php
$response->assertBadRequest();
```

#### assertClientError

断言响应的 HTTP 状态码属于客户端错误（范围：400–499）：

```php
$response->assertClientError();
```

#### assertConflict

断言响应的 HTTP 状态码为 409 Conflict（冲突）

```php
$response->assertConflict();
```

#### assertCookie

断言响应中包含指定名称的 Cookie，并可选验证其值：

```php
$response->assertCookie($cookieName, $value = null);
```

#### assertCookieExpired

断言响应中包含指定名称的 Cookie，且该 Cookie 已过期：

```php
$response->assertCookieExpired($cookieName);
```

#### assertCookieNotExpired

断言响应中包含指定名称的 Cookie，且该 Cookie 尚未过期：

```php
$response->assertCookieNotExpired($cookieName);
```

#### assertCookieMissing

断言响应中不包含指定名称的 Cookie：

```php
$response->assertCookieMissing($cookieName);
```

#### assertCreated

断言响应的 HTTP 状态码为 201 Created（已创建）：

```php
$response->assertCreated();
```

#### assertDontSee

断言响应内容中**不包含**指定字符串。默认情况下该字符串会被自动转义，除非你传入第二个参数为 `false`：

```php
$response->assertDontSee($value, $escape = true);
```

#### assertDontSeeText

断言响应的纯文本内容中**不包含**指定字符串。该方法会在断言前对响应内容执行 `strip_tags` 去除 HTML 标签：

```php
$response->assertDontSeeText($value, $escape = true);
```



#### assertDownload

断言响应是一个“文件下载”响应。通常意味着该响应是由 `Response::download`、`BinaryFileResponse` 或 `Storage::download` 返回的：

```php
$response->assertDownload();
```

如果需要，还可以断言下载文件的名称为指定值：

```php
$response->assertDownload('image.jpg');
```

#### assertExactJson

断言响应包含给定 JSON 数据的完全匹配：
```php
$response->assertExactJson(array $data);
```

#### assertExactJsonStructure

断言响应包含给定 JSON 结构的完全匹配：

```php
$response->assertExactJsonStructure(array $data);
```

该方法是 [`assertJsonStructure`](#assert-json-structure) 的一个更严格的变体。与 `assertJsonStructure` 不同，如果响应包含任何未被明确包含在预期 JSON 结构中的键，该方法将失败。

#### assertForbidden

断言响应具有一个禁止（403）HTTP 状态码：

```php
$response->assertForbidden();
```

#### assertFound

断言响应具有一个已找到（302）HTTP 状态码：

```php
$response->assertFound();
```

#### assertGone

断言响应具有一个已消失（410）HTTP 状态码：

```php
$response->assertGone();
```

#### assertHeader

断言给定的头和数值出现在响应中：

```php
$response->assertHeader($headerName, $value = null);
```

#### assertHeaderMissing

断言给定的头未出现在响应中：

```php
$response->assertHeaderMissing($headerName);
```

#### assertInternalServerError

断言响应具有一个“内部服务器错误”（500）HTTP 状态码：

```php
$response->assertInternalServerError();
```



#### assertJson

断言响应包含给定的 JSON 数据：

```php
$response->assertJson(array $data, $strict = false);
```

`assertJson` 方法会将响应转换为数组，以验证给定的数组是否存在于应用程序返回的 JSON 响应中。
因此，如果 JSON 响应中还有其他属性，只要给定的片段存在，该测试仍然会通过。

#### assertJsonCount

断言响应的 JSON 在给定的键处有一个数组，并且该数组的元素数量与预期相符：

```php
$response->assertJsonCount($count, $key = null);
```

#### assertJsonFragment

断言响应在任意位置包含给定的 JSON 数据：

```php
Route::get('/users', function () {
    return [
        'users' => [
            [
                'name' => 'Taylor Otwell',
            ],
        ],
    ];
});

$response->assertJsonFragment(['name' => 'Taylor Otwell']);
```

#### assertJsonIsArray

断言响应的 JSON 是一个数组：

```php
$response->assertJsonIsArray();
```

#### assertJsonIsObject

断言响应的 JSON 是一个对象：

```php
$response->assertJsonIsObject();
```

#### assertJsonMissing

断言响应不包含给定的 JSON 数据：

```php
$response->assertJsonMissing(array $data);
```

#### assertJsonMissingExact

断言响应不包含完全匹配的 JSON 数据：

```php
$response->assertJsonMissingExact(array $data);
```

#### assertJsonMissingValidationErrors

断言响应在给定的键处没有 JSON 验证错误：

```php
$response->assertJsonMissingValidationErrors($keys);
```

> 可以使用更通用的 [assertValid](#assert-valid) 方法来断言响应没有返回 JSON 格式的验证错误，**并且**没有向会话存储中闪存错误信息。



#### assertJsonPath

断言响应在指定路径中包含给定数据：

```php
$response->assertJsonPath($path, $expectedValue);
```

例如，如果应用程序返回以下 JSON 响应：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以断言 `user` 对象的 `name` 属性与给定值匹配，如下所示：

```php
$response->assertJsonPath('user.name', 'Steve Schoger');
```

#### assertJsonMissingPath

断言响应不包含给定路径：

```php
$response->assertJsonMissingPath($path);
```

例如，如果应用程序返回以下 JSON 响应：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以断言它不包含 `user` 对象的 `email` 属性：

```php
$response->assertJsonMissingPath('user.email');
```

#### assertJsonStructure

断言响应具有给定的 JSON 结构：

```php
$response->assertJsonStructure(array $structure);
```

例如，如果应用程序返回的 JSON 响应包含以下数据：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以断言 JSON 结构符合预期，如下所示：

```php
$response->assertJsonStructure([
    'user' => [
        'name',
    ]
]);
```

有时，应用程序返回的 JSON 响应中可能包含对象数组：

```json
{
    "user": [
        {
            "name": "Steve Schoger",
            "age": 55,
            "location": "Earth"
        },
        {
            "name": "Mary Schoger",
            "age": 60,
            "location": "Earth"
        }
    ]
}
```

在这种情况下，你可以使用 `*` 字符来断言数组中所有对象的结构：

```php
$response->assertJsonStructure([
    'user' => [
        '*' => [
             'name',
             'age',
             'location'
        ]
    ]
]);
```

#### assertJsonValidationErrors

断言响应在给定键处包含指定的 JSON 验证错误。
当验证错误以 JSON 结构返回（而不是被闪存到会话中）时，应使用此方法：

```php
$response->assertJsonValidationErrors(array $data, $responseKey = 'errors');
```

> 可以使用更通用的 [assertInvalid](#assert-invalid) 方法来断言响应包含以 JSON 返回的验证错误，**或者**错误已被闪存到会话存储中。



#### assertJsonValidationErrorFor

断言响应在给定键处存在任意 JSON 验证错误：

```php
$response->assertJsonValidationErrorFor(string $key, $responseKey = 'errors');
```

#### assertMethodNotAllowed

断言响应的 HTTP 状态码为方法不允许（405）：

```php
$response->assertMethodNotAllowed();
```

#### assertMovedPermanently

断言响应的 HTTP 状态码为永久移动（301）：

```php
$response->assertMovedPermanently();
```

#### assertLocation

断言响应在 `Location` 头中具有给定的 URI 值：

```php
$response->assertLocation($uri);
```

#### assertContent

断言给定字符串与响应内容匹配：

```php
$response->assertContent($value);
```

#### assertNoContent

断言响应具有给定的 HTTP 状态码且无内容：

```php
$response->assertNoContent($status = 204);
```

#### assertStreamed

断言响应是一个流式响应：

    $response->assertStreamed();

#### assertStreamedContent

断言给定字符串与流式响应内容匹配：

```php
$response->assertStreamedContent($value);
```

#### assertNotFound

断言响应的 HTTP 状态码为未找到（404）：

```php
$response->assertNotFound();
```

#### assertOk

断言响应的 HTTP 状态码为 200：

```php
$response->assertOk();
```

#### assertPaymentRequired

断言响应的 HTTP 状态码为需要付款（402）：

```php
$response->assertPaymentRequired();
```

#### assertPlainCookie

断言响应包含给定的未加密 Cookie：

```php
$response->assertPlainCookie($cookieName, $value = null);
```

#### assertRedirect

断言响应为重定向到给定 URI：

```php
$response->assertRedirect($uri = null);
```



#### assertRedirectBack

断言响应是否重定向回上一页：

```php
$response->assertRedirectBack();
```

#### assertRedirectContains

断言响应是否重定向到包含给定字符串的 URI：

```php
$response->assertRedirectContains($string);
```

#### assertRedirectToRoute

断言响应是否重定向到给定的[命名路由](/docs/laravel/12.x/routing#named-routes)：

```php
$response->assertRedirectToRoute($name, $parameters = []);
```

#### assertRedirectToSignedRoute

断言响应是否重定向到给定的[签名路由](/docs/laravel/12.x/urls#signed-urls)：

```php
$response->assertRedirectToSignedRoute($name = null, $parameters = []);
```

#### assertRequestTimeout

断言响应的 HTTP 状态码为请求超时（408）：

```php
$response->assertRequestTimeout();
```

#### assertSee

断言响应中包含给定字符串。除非传递第二个参数为 `false`，否则此断言会自动对给定字符串进行转义：

```php
$response->assertSee($value, $escape = true);
```

#### assertSeeInOrder

断言响应中按顺序包含给定字符串。除非传递第二个参数为 `false`，否则此断言会自动对给定字符串进行转义：

```php
$response->assertSeeInOrder(array $values, $escape = true);
```

#### assertSeeText

断言响应文本中包含给定字符串。除非传递第二个参数为 `false`，否则此断言会自动对给定字符串进行转义。在执行断言之前，响应内容会传递给 PHP 的 `strip_tags` 函数：

```php
$response->assertSeeText($value, $escape = true);
```

#### assertSeeTextInOrder



断言响应文本中按顺序包含给定字符串。除非传递第二个参数为 `false`，否则此断言会自动对给定字符串进行转义。在执行断言之前，响应内容会传递给 PHP 的 `strip_tags` 函数：

```php
$response->assertSeeTextInOrder(array $values, $escape = true);
```

#### assertServerError

断言响应的 HTTP 状态码为服务器错误（>= 500 且 < 600）：

```php
$response->assertServerError();
```

#### assertServiceUnavailable

断言响应的 HTTP 状态码为“服务不可用”（503）：

```php
$response->assertServiceUnavailable();
```

#### assertSessionHas

断言会话中包含给定数据：

```php
$response->assertSessionHas($key, $value = null);
```

如有需要，可以将闭包作为第二个参数传递给 `assertSessionHas` 方法。若闭包返回 `true`，断言将通过：

```php
$response->assertSessionHas($key, function (User $value) {
    return $value->name === 'Taylor Otwell';
});
```

#### assertSessionHasInput

断言会话的[闪存输入数组](/docs/laravel/12.x/responses#redirecting-with-flashed-session-data)中具有给定值：

```php
$response->assertSessionHasInput($key, $value = null);
```

如有需要，可以将闭包作为第二个参数传递给 `assertSessionHasInput` 方法。若闭包返回 `true`，断言将通过：

```php
use Illuminate\Support\Facades\Crypt;

$response->assertSessionHasInput($key, function (string $value) {
    return Crypt::decryptString($value) === 'secret';
});
```

#### assertSessionHasAll

断言会话中包含给定的键 / 值对数组：

```php
$response->assertSessionHasAll(array $data);
```

例如，如果应用的会话中包含 `name` 和 `status` 键，可以这样断言它们同时存在并具有指定的值：

```php
$response->assertSessionHasAll([
    'name' => 'Taylor Otwell',
    'status' => 'active',
]);
```



#### assertSessionHasErrors

断言会话中包含给定 `$keys` 的错误。
如果 `$keys` 是关联数组，则断言会话中每个字段（键）包含特定的错误消息（值）。
此方法应在测试那些将验证错误闪存到会话、而不是以 JSON 结构返回的路由时使用：


```php
$response->assertSessionHasErrors(
    array $keys = [], $format = null, $errorBag = 'default'
);
```

例如，要断言 `name` 和 `email` 字段有被闪存到会话的验证错误消息，可以这样调用 `assertSessionHasErrors` 方法：

```php
$response->assertSessionHasErrors(['name', 'email']);
```

或者，你可以断言某个字段具有特定的验证错误消息：

```php
$response->assertSessionHasErrors([
    'name' => 'The given name was invalid.'
]);
```

> 更通用的 [assertInvalid](#assert-invalid) 方法可用于断言响应中存在以 JSON 返回的验证错误 **或** 闪存到会话存储中的错误。

#### assertSessionHasErrorsIn

断言会话中指定的[错误包](/docs/laravel/12.x/validation#named-error-bags)内包含给定 `$keys` 的错误。
如果 `$keys` 是关联数组，则断言该错误包中每个字段（键）包含特定的错误消息（值）：

```php
$response->assertSessionHasErrorsIn($errorBag, $keys = [], $format = null);
```

#### assertSessionHasNoErrors

断言会话中没有验证错误：

```php
$response->assertSessionHasNoErrors();
```

#### assertSessionDoesntHaveErrors

断言会话中给定字段没有验证错误：

```php
$response->assertSessionDoesntHaveErrors($keys = [], $format = null, $errorBag = 'default');
```

> 更通用的 [assertValid](#assert-valid) 方法可用于断言响应中没有以 JSON 返回的验证错误，**并且** 没有将错误闪存到会话存储中。



#### assertSessionMissing

断言会话中不包含给定的键：

```php
$response->assertSessionMissing($key);
```

#### assertStatus

断言响应具有给定的 HTTP 状态码：

```php
$response->assertStatus($code);
```

#### assertSuccessful

断言响应具有成功的（>= 200 且 < 300）HTTP 状态码：

```php
$response->assertSuccessful();
```

#### assertTooManyRequests

断言响应具有“请求过多”（429）HTTP 状态码：

```php
$response->assertTooManyRequests();
```

#### assertUnauthorized

断言响应具有“未授权”（401）HTTP 状态码：

```php
$response->assertUnauthorized();
```

#### assertUnprocessable

断言响应具有“无法处理的实体”（422）HTTP 状态码：

```php
$response->assertUnprocessable();
```

#### assertUnsupportedMediaType

断言响应具有“不支持的媒体类型”（415）HTTP 状态码：

```php
$response->assertUnsupportedMediaType();
```

#### assertValid

断言响应针对给定键没有验证错误。该方法可用于断言验证错误以 JSON 结构返回或以闪存方式存储于会话中的响应：

```php
// 断言没有验证错误...
$response->assertValid();

// 断言给定键没有验证错误...
$response->assertValid(['name', 'email']);
```

#### assertInvalid

断言响应针对给定键存在验证错误。该方法可用于断言验证错误以 JSON 结构返回或以闪存方式存储于会话中的响应：

```php
$response->assertInvalid(['name', 'email']);
```



您也可以断言某个键具有特定的验证错误消息。
在这样做时，您可以提供完整的消息或消息的一小部分：

```php
$response->assertInvalid([
    'name' => 'The name field is required.',
    'email' => 'valid email address',
]);
```

如果您想断言只有给定字段存在验证错误，可以使用 `assertOnlyInvalid` 方法：

```php
$response->assertOnlyInvalid(['name', 'email']);
```

#### assertViewHas

断言响应的视图包含给定的数据项：

```php
$response->assertViewHas($key, $value = null);
```

将闭包作为第二个参数传递给 `assertViewHas` 方法，可以让您检查并断言特定的视图数据：

```php
$response->assertViewHas('user', function (User $user) {
    return $user->name === 'Taylor';
});
```

此外，可以将视图数据作为数组变量通过响应访问，从而方便检查：

```php tab=Pest
expect($response['name'])->toBe('Taylor');
```

```php tab=PHPUnit
$this->assertEquals('Taylor', $response['name']);
```

#### assertViewHasAll

断言响应视图拥有给定的数据列表：

```php
$response->assertViewHasAll(array $data);
```

此方法可用于断言视图仅包含与给定键匹配的数据：

```php
$response->assertViewHasAll([
    'name',
    'email',
]);
```

或者，您也可以断言视图数据存在且具有特定值：

```php
$response->assertViewHasAll([
    'name' => 'Taylor Otwell',
    'email' => 'taylor@example.com,',
]);
```

#### assertViewIs

断言路由返回了给定的视图：

```php
$response->assertViewIs($value);
```



#### assertViewMissing

断言给定的数据键未被提供给应用响应中返回的视图：

```php
$response->assertViewMissing($key);
```

### 认证断言

Laravel 还提供了多种认证相关的断言，您可以在应用的功能测试中使用。
注意，这些方法是在测试类本身上调用的，而不是在通过 `get` 或 `post` 等方法返回的 `Illuminate\Testing\TestResponse` 实例上调用

#### assertAuthenticated

断言用户已认证：

```php
$this->assertAuthenticated($guard = null);
```

#### assertGuest

断言用户未认证：

```php
$this->assertGuest($guard = null);
```

#### assertAuthenticatedAs

断言特定用户已认证：

```php
$this->assertAuthenticatedAs($user, $guard = null);
```

## 验证断言

Laravel 提供了两个主要的验证相关断言，用于确保请求中提供的数据有效或无效。

#### assertValid

断言响应中给定键没有验证错误。
此方法可用于断言返回 JSON 结构的验证错误，或验证错误已闪存到会话的响应：

```php
// 断言没有验证错误...
$response->assertValid();

// 断言给定键没有验证错误...
$response->assertValid(['name', 'email']);
```

#### assertInvalid

断言响应中给定键有验证错误。
此方法可用于断言返回 JSON 结构的验证错误，或验证错误已闪存到会话的响应：

```php
$response->assertInvalid(['name', 'email']);
```

您也可以断言某个键具有特定的验证错误消息。
此时可以提供完整的错误消息或消息的一小部分：

```php
$response->assertInvalid([
    'name' => 'The name field is required.',
    'email' => 'valid email address',
]);
```

# HTTP 测试

- [简介](#introduction)
- [发起请求](#making-requests)
    - [自定义请求头](#customizing-request-headers)
    - [Cookie](#cookies)
    - [会话 / 身份验证](#session-and-authentication)
    - [调试响应](#debugging-responses)
    - [异常处理](#exception-handling)
- [测试 JSON API](#testing-json-apis)
    - [链式 JSON 测试](#fluent-json-testing)
- [测试文件上传](#testing-file-uploads)
- [测试视图](#testing-views)
    - [渲染 Blade 和组件](#rendering-blade-and-components)
- [缓存路由](#caching-routes)
- [可用断言](#available-assertions)
    - [响应断言](#response-assertions)
    - [身份验证断言](#authentication-assertions)
    - [验证断言](#validation-assertions)

<a name="introduction"></a>
## 简介

Laravel 提供了流畅的 API，用于向应用发起 HTTP 请求并检查响应。例如，下面定义了一个功能测试：

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
     * 一个基本的测试示例。
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }
}
```

`get` 方法会向应用发起 `GET` 请求，而 `assertStatus` 方法则断言返回的响应具有给定的 HTTP 状态码。除了这个简单的断言，Laravel 还提供了多种断言，用于检查响应头、内容、JSON 结构等。

<a name="making-requests"></a>
## 发起请求

你可以在测试中调用 `get`、`post`、`put`、`patch` 或 `delete` 方法，向应用发起请求。这些方法不会向应用发出「真实的」HTTP 请求，而是在内部模拟整个网络请求。

测试请求方法返回的是 `Illuminate\Testing\TestResponse` 实例，而非 `Illuminate\Http\Response` 实例。它提供了[多种实用的断言](#available-assertions)，方便你检查应用的响应：

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
     * 一个基本的测试示例。
     */
    public function test_a_basic_request(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }
}
```

通常，每个测试应该只向应用发起一次请求。在同一个测试方法中执行多个请求可能导致意外行为。

> [!NOTE]
> 为了方便测试，运行测试时会自动禁用 CSRF 中间件。

<a name="customizing-request-headers"></a>
### 自定义请求头

你可以使用 `withHeaders` 方法，在请求发送到应用之前自定义请求头。该方法允许你为请求添加任意自定义请求头：

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
     * 一个基本的功能测试示例。
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
### Cookie

你可以使用 `withCookie` 或 `withCookies` 方法，在发起请求前设置 Cookie 值。`withCookie` 方法接收 Cookie 名称和值两个参数，而 `withCookies` 方法接收一个名称 / 值键值对数组：

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

<a name="session-and-authentication"></a>
### 会话 / 身份验证

Laravel 提供了多个辅助方法，用于在 HTTP 测试期间与会话交互。首先，你可以使用 `withSession` 方法，将给定数组设为会话数据。这有助于在向应用发起请求之前，预先向会话中写入数据：

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

Laravel 的会话通常用于维护当前已认证用户的状态。因此，`actingAs` 辅助方法让你能够轻松地将给定用户认证为当前用户。例如，我们可以使用[模型工厂](/docs/{{version}}/eloquent-factories)生成并认证一个用户：

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

你也可以将 guard 名称作为第二个参数传递给 `actingAs` 方法，指定用于认证该用户的 guard。传递给 `actingAs` 方法的 guard 也会在本次测试期间成为默认 guard：

```php
$this->actingAs($user, 'web');
```

如果你想确保请求处于未认证状态，可以使用 `actingAsGuest` 方法：

```php
$this->actingAsGuest();
```

<a name="debugging-responses"></a>
### 调试响应

向应用发起测试请求后，你可以使用 `dump`、`dumpHeaders` 和 `dumpSession` 方法，查看并调试响应内容：

```php tab=Pest
<?php

test('basic test', function () {
    $response = $this->get('/');

    $response->dump();
    $response->dumpHeaders();
    $response->dumpSession();
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

        $response->dump();
        $response->dumpHeaders();
        $response->dumpSession();
    }
}
```

你也可以使用 `dd`、`ddHeaders`、`ddBody`、`ddJson` 和 `ddSession` 方法，输出响应信息并停止执行：

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

<a name="exception-handling"></a>
### 异常处理

有时，你可能需要测试应用是否抛出了特定异常。为此，可以通过 `Exceptions` facade 模拟异常处理器。模拟异常处理器后，你可以使用 `assertReported` 和 `assertNotReported` 方法，对请求期间抛出的异常进行断言：

```php tab=Pest
<?php

use App\Exceptions\InvalidOrderException;
use Illuminate\Support\Facades\Exceptions;

test('exception is thrown', function () {
    Exceptions::fake();

    $response = $this->get('/order/1');

    // 断言抛出了异常……
    Exceptions::assertReported(InvalidOrderException::class);

    // 对异常进行断言……
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

        // 断言抛出了异常……
        Exceptions::assertReported(InvalidOrderException::class);

        // 对异常进行断言……
        Exceptions::assertReported(function (InvalidOrderException $e) {
            return $e->getMessage() === 'The order was invalid.';
        });
    }
}
```

`assertNotReported` 和 `assertNothingReported` 方法可用于断言请求期间未抛出给定异常，或没有抛出任何异常：

```php
Exceptions::assertNotReported(InvalidOrderException::class);

Exceptions::assertNothingReported();
```

你可以在发起请求之前调用 `withoutExceptionHandling` 方法，完全禁用该请求的异常处理：

```php
$response = $this->withoutExceptionHandling()->get('/');
```

此外，如果你想确保应用没有使用 PHP 语言或应用所用库中已弃用的功能，可以在发起请求前调用 `withoutDeprecationHandling` 方法。禁用弃用警告处理后，弃用警告会转换为异常，从而导致测试失败：

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

如果你想检查抛出的异常并对其进行断言，可以将闭包作为第二个参数传递给 `assertThrows` 方法：

```php
$this->assertThrows(
    fn () => (new ProcessOrder)->execute(),
    fn (OrderInvalid $e) => $e->orderId() === 123
);
```

`assertDoesntThrow` 方法可用于断言给定闭包中的代码没有抛出任何异常：

```php
$this->assertDoesntThrow(fn () => (new ProcessOrder)->execute());
```

<a name="testing-json-apis"></a>
## 测试 JSON API

Laravel 还提供了多个辅助方法，用于测试 JSON API 及其响应。例如，`json`、`getJson`、`postJson`、`putJson`、`patchJson`、`deleteJson` 和 `optionsJson` 方法可用于通过不同的 HTTP 动词发起 JSON 请求。你也可以轻松地向这些方法传递数据和请求头。首先，让我们编写一个测试，向 `/api/user` 发起 `POST` 请求，并断言返回了预期的 JSON 数据：

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

此外，你可以像访问数组变量一样访问响应中的 JSON 数据，方便检查 JSON 响应返回的各个值：

```php tab=Pest
expect($response['created'])->toBeTrue();
```

```php tab=PHPUnit
$this->assertTrue($response['created']);
```

> [!NOTE]
> `assertJson` 方法会将响应转换为数组，以验证给定数组是否包含在应用返回的 JSON 响应中。因此，即使 JSON 响应中还有其他属性，只要给定片段存在，测试仍会通过。

<a name="verifying-exact-match"></a>
#### 断言 JSON 完全匹配

如前所述，`assertJson` 方法可用于断言 JSON 响应中包含某个 JSON 片段。如果你想验证给定数组与应用返回的 JSON **完全匹配**，应该使用 `assertExactJson` 方法：

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
     * 一个基本的功能测试示例。
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

<a name="verifying-json-paths"></a>
#### 断言 JSON 路径

如果你想验证 JSON 响应在指定路径处包含给定数据，应该使用 `assertJsonPath` 方法：

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
     * 一个基本的功能测试示例。
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

`assertJsonPath` 方法也接收闭包，用于动态判断断言是否通过：

```php
$response->assertJsonPath('team.owner.name', fn (string $name) => strlen($name) >= 3);
```

如果你需要一次断言多个 JSON 路径，可以使用 `assertJsonPaths` 方法。每个路径的预期值也可以是闭包：

```php
$response->assertJsonPaths([
    'team.owner.name' => 'Darian',
    'team.owner.email' => fn (string $email) => str($email)->is('*@laravel.com'),
    'team.members.0.name' => 'Sally',
]);
```

你可以使用 `assertJsonMissingPaths` 方法，断言响应中不存在多个 JSON 路径：

```php
$response->assertJsonMissingPaths([
    'team.owner.password',
    'team.members.0.api_token',
]);
```

<a name="fluent-json-testing"></a>
### 链式 JSON 测试

Laravel 还提供了优雅的方式，让你以链式调用测试应用的 JSON 响应。首先，向 `assertJson` 方法传递一个闭包。调用该闭包时，会传入一个 `Illuminate\Testing\Fluent\AssertableJson` 实例，用于对应用返回的 JSON 进行断言。`where` 方法可用于断言 JSON 中的特定属性，而 `missing` 方法可用于断言 JSON 中不存在某个属性：

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
 * 一个基本的功能测试示例。
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

#### 理解 `etc` 方法

在上面的示例中，你可能注意到我们在断言链末尾调用了 `etc` 方法。该方法告知 Laravel，JSON 对象中可能还存在其他属性。如果没有使用 `etc` 方法，而 JSON 对象中存在未经断言的其他属性，测试就会失败。

这种行为旨在防止你无意间在 JSON 响应中暴露敏感信息：你必须显式地对属性进行断言，或者通过 `etc` 方法明确允许额外的属性。

不过，你需要注意，未在断言链中调用 `etc` 方法，并不能保证 JSON 对象内部嵌套的数组中不会出现额外属性。`etc` 方法只针对调用它的嵌套层级控制是否允许额外属性。

<a name="asserting-json-attribute-presence-and-absence"></a>
#### 断言属性存在 / 缺失

要断言某个属性存在或缺失，可以使用 `has` 和 `missing` 方法：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->has('data')
        ->missing('message')
);
```

此外，`hasAll` 和 `missingAll` 方法允许你同时断言多个属性存在或缺失：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->hasAll(['status', 'data'])
        ->missingAll(['message', 'code'])
);
```

你可以使用 `hasAny` 方法，判断给定的一组属性中是否至少有一个存在：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->has('status')
        ->hasAny('data', 'message', 'code')
);
```

<a name="asserting-against-json-collections"></a>
#### 对 JSON 集合进行断言

路由通常会返回包含多个项目的 JSON 响应，例如多个用户：

```php
Route::get('/users', function () {
    return User::all();
});
```

在这种情况下，我们可以使用链式 JSON 对象的 `has` 方法，对响应中包含的用户进行断言。例如，先断言 JSON 响应包含三个用户，再使用 `first` 方法对集合中的第一个用户进行断言。`first` 方法接收一个闭包，该闭包会接收另一个可用于断言的 JSON 对象，供我们对 JSON 集合中的第一个对象进行断言：

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

如果你想对 JSON 集合中的每个项目进行相同的断言，可以使用 `each` 方法：

```php
$response
  ->assertJson(fn (AssertableJson $json) =>
      $json->has(3)
          ->each(fn (AssertableJson $json) =>
              $json->whereType('id', 'integer')
                  ->whereType('name', 'string')
                  ->whereType('email', 'string')
                  ->missing('password')
                  ->etc()
          )
  );
```

<a name="scoping-json-collection-assertions"></a>
#### 限定 JSON 集合断言的作用范围

有时，应用的路由会返回分配给命名键的 JSON 集合：

```php
Route::get('/users', function () {
    return [
        'meta' => [...],
        'users' => User::all(),
    ];
});
```

测试这些路由时，你可以使用 `has` 方法断言集合中的项目数量。此外，还可以使用 `has` 方法限定一系列断言的作用范围：

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

你也可以只调用一次 `has` 方法，并将闭包作为第三个参数传入，而无需分别调用两次 `has` 方法对 `users` 集合进行断言。此时，闭包会被自动调用，其作用范围会限定为集合中的第一个项目：

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

<a name="asserting-json-types"></a>
#### 断言 JSON 类型

你可能只想断言 JSON 响应中属性的类型。`Illuminate\Testing\Fluent\AssertableJson` 类提供了 `whereType` 和 `whereAllType` 方法，用于实现这一点：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->whereType('id', 'integer')
        ->whereAllType([
            'users.0.name' => 'string',
            'meta' => 'array'
        ])
);
```

你可以使用 `|` 字符指定多个类型，或将类型数组作为第二个参数传递给 `whereType` 方法。只要响应值属于所列类型之一，断言就会通过：

```php
$response->assertJson(fn (AssertableJson $json) =>
    $json->whereType('name', 'string|null')
        ->whereType('id', ['string', 'integer'])
);
```

`whereType` 和 `whereAllType` 方法支持以下类型：`string`、`integer`、`double`、`boolean`、`array` 和 `null`。

<a name="testing-file-uploads"></a>
## 测试文件上传

`Illuminate\Http\UploadedFile` 类提供了 `fake` 方法，可用于生成测试用的模拟文件或图片。结合 `Storage` facade 的 `fake` 方法，可以大幅简化文件上传测试。例如，你可以结合这两个功能，轻松测试头像上传表单：

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

如果你想断言给定文件不存在，可以使用 `Storage` facade 提供的 `assertMissing` 方法：

```php
Storage::fake('avatars');

// ...

Storage::disk('avatars')->assertMissing('missing.jpg');
```

<a name="fake-file-customization"></a>
#### 自定义模拟文件

使用 `UploadedFile` 类提供的 `fake` 方法创建文件时，你可以指定图片的宽度、高度和大小（单位为 KB），以便更好地测试应用的验证规则：

```php
UploadedFile::fake()->image('avatar.jpg', $width, $height)->size(100);
```

除了创建图片，你还可以使用 `create` 方法创建任意其他类型的文件：

```php
UploadedFile::fake()->create('document.pdf', $sizeInKilobytes);
```

如有需要，你可以向该方法传递 `$mimeType` 参数，显式指定文件应返回的 MIME 类型：

```php
UploadedFile::fake()->create(
    'document.pdf', $sizeInKilobytes, 'application/pdf'
);
```

<a name="testing-views"></a>
## 测试视图

Laravel 还允许你在不向应用发起模拟 HTTP 请求的情况下渲染视图。为此，可以在测试中调用 `view` 方法。该方法接收视图名称和一个可选的数据数组，并返回 `Illuminate\Testing\TestView` 实例。该实例提供了多个方法，方便你对视图内容进行断言：

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

`TestView` 类提供了以下断言方法：`assertSee`、`assertSeeInOrder`、`assertSeeText`、`assertSeeTextInOrder`、`assertDontSee` 和 `assertDontSeeText`。

如有需要，你可以将 `TestView` 实例转换为字符串，获取渲染后的原始视图内容：

```php
$contents = (string) $this->view('welcome');
```

<a name="sharing-errors"></a>
#### 共享错误

某些视图可能依赖 [Laravel 提供的全局错误包](/docs/{{version}}/validation#quick-displaying-the-validation-errors)中的错误。你可以使用 `withViewErrors` 方法向错误包填充错误消息：

```php
$view = $this->withViewErrors([
    'name' => ['Please provide a valid name.']
])->view('form');

$view->assertSee('Please provide a valid name.');
```

<a name="rendering-blade-and-components"></a>
### 渲染 Blade 和组件

如有需要，你可以使用 `blade` 方法解析并渲染原始的 [Blade](/docs/{{version}}/blade) 字符串。与 `view` 方法一样，`blade` 方法会返回一个 `Illuminate\Testing\TestView` 实例：

```php
$view = $this->blade(
    '<x-component :name="$name" />',
    ['name' => 'Taylor']
);

$view->assertSee('Taylor');
```

你可以使用 `component` 方法解析并渲染一个 [Blade 组件](/docs/{{version}}/blade#components)。该方法会返回一个 `Illuminate\Testing\TestComponent` 实例：

```php
$view = $this->component(Profile::class, ['name' => 'Taylor']);

$view->assertSee('Taylor');
```

<a name="caching-routes"></a>
## 缓存路由

每次测试运行前，Laravel 都会启动一个全新的应用实例，包括收集所有已定义的路由。如果应用有很多路由文件，你可能希望为测试用例添加 `Illuminate\Foundation\Testing\WithCachedRoutes` trait。使用该 trait 时，路由只会构建一次并存储在内存中，这意味着整个测试套件只需执行一次路由收集过程：

```php tab=Pest
<?php

use App\Http\Controllers\UserController;
use Illuminate\Foundation\Testing\WithCachedRoutes;

pest()->use(WithCachedRoutes::class);

test('basic example', function () {
    $this->get(action([UserController::class, 'index']));

    // ...
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Http\Controllers\UserController;
use Illuminate\Foundation\Testing\WithCachedRoutes;
use Tests\TestCase;

class BasicTest extends TestCase
{
    use WithCachedRoutes;

    /**
     * 一个基本的功能测试示例。
     */
    public function test_basic_example(): void
    {
        $response = $this->get(action([UserController::class, 'index']));

        // ...
    }
}
```

<a name="available-assertions"></a>
## 可用断言

<a name="response-assertions"></a>
### 响应断言

Laravel 的 `Illuminate\Testing\TestResponse` 类提供了多种自定义断言方法，供你测试应用。你可以在 `json`、`get`、`post`、`put` 和 `delete` 测试方法返回的响应上调用这些断言：

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
[assertFailedDependency](#assert-failed-dependency)
[assertForbidden](#assert-forbidden)
[assertFound](#assert-found)
[assertGone](#assert-gone)
[assertHeader](#assert-header)
[assertHeaderContains](#assert-header-contains)
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
[assertJsonPaths](#assert-json-paths)
[assertJsonMissingPath](#assert-json-missing-path)
[assertJsonMissingPaths](#assert-json-missing-paths)
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
[assertRedirectBackWithErrors](#assert-redirect-back-with-errors)
[assertRedirectBackWithoutErrors](#assert-redirect-back-without-errors)
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
[assertSessionMissingInput](#assert-session-missing-input)
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

<a name="assert-accepted"></a>
#### assertAccepted

断言响应的 HTTP 状态码为已接受（202）：

```php
$response->assertAccepted();
```

<a name="assert-bad-request"></a>
#### assertBadRequest

断言响应的 HTTP 状态码为错误请求（400）：

```php
$response->assertBadRequest();
```

<a name="assert-client-error"></a>
#### assertClientError

断言响应的 HTTP 状态码为客户端错误（>= 400，< 500）：

```php
$response->assertClientError();
```

<a name="assert-conflict"></a>
#### assertConflict

断言响应的 HTTP 状态码为冲突（409）：

```php
$response->assertConflict();
```

<a name="assert-cookie"></a>
#### assertCookie

断言响应包含给定的 Cookie：

```php
$response->assertCookie($cookieName, $value = null);
```

<a name="assert-cookie-expired"></a>
#### assertCookieExpired

断言响应包含给定的 Cookie，且该 Cookie 已过期：

```php
$response->assertCookieExpired($cookieName);
```

<a name="assert-cookie-not-expired"></a>
#### assertCookieNotExpired

断言响应包含给定的 Cookie，且该 Cookie 尚未过期：

```php
$response->assertCookieNotExpired($cookieName);
```

<a name="assert-cookie-missing"></a>
#### assertCookieMissing

断言响应不包含给定的 Cookie：

```php
$response->assertCookieMissing($cookieName);
```

<a name="assert-created"></a>
#### assertCreated

断言响应的 HTTP 状态码为 201：

```php
$response->assertCreated();
```

<a name="assert-dont-see"></a>
#### assertDontSee

断言应用返回的响应中不包含给定字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串：

```php
$response->assertDontSee($value, $escape = true);
```

<a name="assert-dont-see-text"></a>
#### assertDontSeeText

断言响应文本中不包含给定字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串。该方法会在执行断言前，将响应内容传递给 PHP 的 `strip_tags` 函数：

```php
$response->assertDontSeeText($value, $escape = true);
```

<a name="assert-download"></a>
#### assertDownload

断言响应为「下载」响应。通常，这意味着返回该响应的路由返回了 `Response::download` 响应、`BinaryFileResponse` 或 `Storage::download` 响应：

```php
$response->assertDownload();
```

如有需要，你还可以断言下载文件被指定了给定的文件名：

```php
$response->assertDownload('image.jpg');
```

<a name="assert-exact-json"></a>
#### assertExactJson

断言响应与给定的 JSON 数据完全匹配：

```php
$response->assertExactJson(array $data);
```

<a name="assert-exact-json-structure"></a>
#### assertExactJsonStructure

断言响应与给定的 JSON 结构完全匹配：

```php
$response->assertExactJsonStructure(array $data);
```

该方法是 [assertJsonStructure](#assert-json-structure) 的更严格版本。与 `assertJsonStructure` 不同，如果响应包含预期 JSON 结构中未明确列出的任何键，该断言就会失败。

<a name="assert-failed-dependency"></a>
#### assertFailedDependency

断言响应的 HTTP 状态码为依赖失败（424）：

```php
$response->assertFailedDependency();
```

<a name="assert-forbidden"></a>
#### assertForbidden

断言响应的 HTTP 状态码为禁止访问（403）：

```php
$response->assertForbidden();
```

<a name="assert-found"></a>
#### assertFound

断言响应的 HTTP 状态码为已找到（302）：

```php
$response->assertFound();
```

<a name="assert-gone"></a>
#### assertGone

断言响应的 HTTP 状态码为已移除（410）：

```php
$response->assertGone();
```

<a name="assert-header"></a>
#### assertHeader

断言响应中存在给定的响应头名称和值：

```php
$response->assertHeader($headerName, $value = null);
```

<a name="assert-header-contains"></a>
#### assertHeaderContains

断言给定的响应头包含指定的子字符串值：

```php
$response->assertHeaderContains($headerName, $value);
```

<a name="assert-header-missing"></a>
#### assertHeaderMissing

断言响应中不存在给定的响应头：

```php
$response->assertHeaderMissing($headerName);
```

<a name="assert-internal-server-error"></a>
#### assertInternalServerError

断言响应的 HTTP 状态码为「内部服务器错误」（500）：

```php
$response->assertInternalServerError();
```

<a name="assert-json"></a>
#### assertJson

断言响应包含给定的 JSON 数据：

```php
$response->assertJson(array $data, $strict = false);
```

`assertJson` 方法会将响应转换为数组，以验证给定数组是否包含在应用返回的 JSON 响应中。因此，即使 JSON 响应中还有其他属性，只要给定片段存在，测试仍会通过。

<a name="assert-json-count"></a>
#### assertJsonCount

断言响应 JSON 中给定键对应的数组包含预期数量的项目：

```php
$response->assertJsonCount($count, $key = null);
```

<a name="assert-json-fragment"></a>
#### assertJsonFragment

断言响应中的任意位置包含给定的 JSON 数据：

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

<a name="assert-json-is-array"></a>
#### assertJsonIsArray

断言响应 JSON 为数组：

```php
$response->assertJsonIsArray();
```

<a name="assert-json-is-object"></a>
#### assertJsonIsObject

断言响应 JSON 为对象：

```php
$response->assertJsonIsObject();
```

<a name="assert-json-missing"></a>
#### assertJsonMissing

断言响应不包含给定的 JSON 数据：

```php
$response->assertJsonMissing(array $data);
```

<a name="assert-json-missing-exact"></a>
#### assertJsonMissingExact

断言响应中不存在与给定 JSON 数据完全匹配的内容：

```php
$response->assertJsonMissingExact(array $data);
```

<a name="assert-json-missing-validation-errors"></a>
#### assertJsonMissingValidationErrors

断言响应中给定的键没有 JSON 验证错误：

```php
$response->assertJsonMissingValidationErrors($keys);
```

> [!NOTE]
> 你可以使用更通用的 [assertValid](#assert-valid) 方法，断言响应没有以 JSON 返回的验证错误，**并且**没有错误被暂存到会话中。

<a name="assert-json-path"></a>
#### assertJsonPath

断言响应在指定路径处包含给定数据：

```php
$response->assertJsonPath($path, $expectedValue);
```

例如，应用返回了以下 JSON 响应：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以像下面这样，断言 `user` 对象的 `name` 属性与给定值匹配：

```php
$response->assertJsonPath('user.name', 'Steve Schoger');
```

<a name="assert-json-paths"></a>
#### assertJsonPaths

断言响应在多个指定路径处包含给定数据：

```php
$response->assertJsonPaths(array $paths);
```

例如，你可以一次断言响应中的多个值：

```php
$response->assertJsonPaths([
    'user.name' => 'Steve Schoger',
    'user.email' => fn (string $email) => str($email)->endsWith('@laravel.com'),
]);
```

<a name="assert-json-missing-path"></a>
#### assertJsonMissingPath

断言响应中不存在给定路径：

```php
$response->assertJsonMissingPath($path);
```

例如，应用返回了以下 JSON 响应：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以断言响应中不存在 `user` 对象的 `email` 属性：

```php
$response->assertJsonMissingPath('user.email');
```

<a name="assert-json-missing-paths"></a>
#### assertJsonMissingPaths

断言响应中不存在给定的多个路径：

```php
$response->assertJsonMissingPaths($paths);
```

例如，你可以断言响应中不存在多个路径：

```php
$response->assertJsonMissingPaths([
    'user.email',
    'user.password',
]);
```

<a name="assert-json-structure"></a>
#### assertJsonStructure

断言响应具有给定的 JSON 结构：

```php
$response->assertJsonStructure(array $structure);
```

例如，应用返回的 JSON 响应包含以下数据：

```json
{
    "user": {
        "name": "Steve Schoger"
    }
}
```

你可以像下面这样，断言 JSON 结构符合预期：

```php
$response->assertJsonStructure([
    'user' => [
        'name',
    ]
]);
```

有时，应用返回的 JSON 响应中可能包含对象数组：

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

在这种情况下，你可以使用 `*` 字符，断言数组中所有对象的结构：

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

<a name="assert-json-validation-errors"></a>
#### assertJsonValidationErrors

断言响应中给定的键存在指定的 JSON 验证错误。验证错误以 JSON 结构返回，而非暂存到会话中时，应该使用该方法：

```php
$response->assertJsonValidationErrors(array $data, $responseKey = 'errors');
```

> [!NOTE]
> 你可以使用更通用的 [assertInvalid](#assert-invalid) 方法，断言响应包含以 JSON 返回的验证错误，**或者**错误已被暂存到会话中。

<a name="assert-json-validation-error-for"></a>
#### assertJsonValidationErrorFor

断言响应中给定的键存在任意 JSON 验证错误：

```php
$response->assertJsonValidationErrorFor(string $key, $responseKey = 'errors');
```

<a name="assert-method-not-allowed"></a>
#### assertMethodNotAllowed

断言响应的 HTTP 状态码为方法不允许（405）：

```php
$response->assertMethodNotAllowed();
```

<a name="assert-moved-permanently"></a>
#### assertMovedPermanently

断言响应的 HTTP 状态码为永久移动（301）：

```php
$response->assertMovedPermanently();
```

<a name="assert-location"></a>
#### assertLocation

断言响应的 `Location` 头包含给定的 URI 值：

```php
$response->assertLocation($uri);
```

<a name="assert-content"></a>
#### assertContent

断言给定字符串与响应内容匹配：

```php
$response->assertContent($value);
```

<a name="assert-no-content"></a>
#### assertNoContent

断言响应具有给定的 HTTP 状态码，且没有内容：

```php
$response->assertNoContent($status = 204);
```

<a name="assert-streamed"></a>
#### assertStreamed

断言响应为流式响应：

    $response->assertStreamed();

<a name="assert-streamed-content"></a>
#### assertStreamedContent

断言给定字符串与流式响应的内容匹配：

```php
$response->assertStreamedContent($value);
```

<a name="assert-not-found"></a>
#### assertNotFound

断言响应的 HTTP 状态码为未找到（404）：

```php
$response->assertNotFound();
```

<a name="assert-ok"></a>
#### assertOk

断言响应的 HTTP 状态码为 200：

```php
$response->assertOk();
```

<a name="assert-payment-required"></a>
#### assertPaymentRequired

断言响应的 HTTP 状态码为需要付款（402）：

```php
$response->assertPaymentRequired();
```

<a name="assert-plain-cookie"></a>
#### assertPlainCookie

断言响应包含给定的未加密 Cookie：

```php
$response->assertPlainCookie($cookieName, $value = null);
```

<a name="assert-redirect"></a>
#### assertRedirect

断言响应重定向到给定的 URI：

```php
$response->assertRedirect($uri = null);
```

<a name="assert-redirect-back"></a>
#### assertRedirectBack

断言响应重定向回上一页：

```php
$response->assertRedirectBack();
```

<a name="assert-redirect-back-with-errors"></a>
#### assertRedirectBackWithErrors

断言响应重定向回上一页，且[会话中包含给定的错误](#assert-session-has-errors)：

```php
$response->assertRedirectBackWithErrors(
    array $keys = [], $format = null, $errorBag = 'default'
);
```

<a name="assert-redirect-back-without-errors"></a>
#### assertRedirectBackWithoutErrors

断言响应重定向回上一页，且会话中没有任何错误消息：

```php
$response->assertRedirectBackWithoutErrors();
```

<a name="assert-redirect-contains"></a>
#### assertRedirectContains

断言响应重定向到的 URI 包含给定字符串：

```php
$response->assertRedirectContains($string);
```

<a name="assert-redirect-to-route"></a>
#### assertRedirectToRoute

断言响应重定向到给定的[命名路由](/docs/{{version}}/routing#named-routes)：

```php
$response->assertRedirectToRoute($name, $parameters = []);
```

<a name="assert-redirect-to-signed-route"></a>
#### assertRedirectToSignedRoute

断言响应重定向到给定的[签名路由](/docs/{{version}}/urls#signed-urls)：

```php
$response->assertRedirectToSignedRoute($name = null, $parameters = []);
```

<a name="assert-request-timeout"></a>
#### assertRequestTimeout

断言响应的 HTTP 状态码为请求超时（408）：

```php
$response->assertRequestTimeout();
```

<a name="assert-see"></a>
#### assertSee

断言响应中包含给定字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串：

```php
$response->assertSee($value, $escape = true);
```

<a name="assert-see-in-order"></a>
#### assertSeeInOrder

断言响应中按顺序包含给定的多个字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串：

```php
$response->assertSeeInOrder(array $values, $escape = true);
```

<a name="assert-see-text"></a>
#### assertSeeText

断言响应文本中包含给定字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串。在执行断言前，响应内容会传递给 PHP 的 `strip_tags` 函数：

```php
$response->assertSeeText($value, $escape = true);
```

<a name="assert-see-text-in-order"></a>
#### assertSeeTextInOrder

断言响应文本中按顺序包含给定的多个字符串。除非将第二个参数设为 `false`，否则此断言会自动转义给定字符串。在执行断言前，响应内容会传递给 PHP 的 `strip_tags` 函数：

```php
$response->assertSeeTextInOrder(array $values, $escape = true);
```

<a name="assert-server-error"></a>
#### assertServerError

断言响应的 HTTP 状态码为服务器错误（>= 500，< 600）：

```php
$response->assertServerError();
```

<a name="assert-service-unavailable"></a>
#### assertServiceUnavailable

断言响应的 HTTP 状态码为「服务不可用」（503）：

```php
$response->assertServiceUnavailable();
```

<a name="assert-session-has"></a>
#### assertSessionHas

断言会话中包含给定的数据：

```php
$response->assertSessionHas($key, $value = null);
```

如有需要，你可以将闭包作为第二个参数传递给 `assertSessionHas` 方法。如果闭包返回 `true`，断言就会通过：

```php
$response->assertSessionHas($key, function (User $value) {
    return $value->name === 'Taylor Otwell';
});
```

<a name="assert-session-has-input"></a>
#### assertSessionHasInput

断言会话的[暂存输入数组](/docs/{{version}}/responses#redirecting-with-flashed-session-data)中包含给定值：

```php
$response->assertSessionHasInput($key, $value = null);
```

如有需要，你可以将闭包作为第二个参数传递给 `assertSessionHasInput` 方法。如果闭包返回 `true`，断言就会通过：

```php
use Illuminate\Support\Facades\Crypt;

$response->assertSessionHasInput($key, function (string $value) {
    return Crypt::decryptString($value) === 'secret';
});
```

<a name="assert-session-has-all"></a>
#### assertSessionHasAll

断言会话中包含给定数组中的所有键 / 值对：

```php
$response->assertSessionHasAll(array $data);
```

例如，如果应用的会话中包含 `name` 和 `status` 键，你可以像下面这样，断言这两个键都存在且具有指定的值：

```php
$response->assertSessionHasAll([
    'name' => 'Taylor Otwell',
    'status' => 'active',
]);
```

<a name="assert-session-has-errors"></a>
#### assertSessionHasErrors

断言会话中给定的 `$keys` 存在错误。如果 `$keys` 是关联数组，则断言会话中每个字段（键）都有指定的错误消息（值）。测试将验证错误暂存到会话、而非以 JSON 结构返回错误的路由时，应该使用该方法：

```php
$response->assertSessionHasErrors(
    array $keys = [], $format = null, $errorBag = 'default'
);
```

例如，要断言 `name` 和 `email` 字段的验证错误消息已被暂存到会话中，你可以像下面这样调用 `assertSessionHasErrors` 方法：

```php
$response->assertSessionHasErrors(['name', 'email']);
```

或者，你可以断言给定字段具有特定的验证错误消息：

```php
$response->assertSessionHasErrors([
    'name' => 'The given name was invalid.'
]);
```

> [!NOTE]
> 你可以使用更通用的 [assertInvalid](#assert-invalid) 方法，断言响应包含以 JSON 返回的验证错误，**或者**错误已被暂存到会话中。

<a name="assert-session-has-errors-in"></a>
#### assertSessionHasErrorsIn

断言会话中指定的[错误包](/docs/{{version}}/validation#named-error-bags)包含给定 `$keys` 的错误。如果 `$keys` 是关联数组，则断言该错误包中每个字段（键）都有指定的错误消息（值）：

```php
$response->assertSessionHasErrorsIn($errorBag, $keys = [], $format = null);
```

<a name="assert-session-has-no-errors"></a>
#### assertSessionHasNoErrors

断言会话中没有验证错误：

```php
$response->assertSessionHasNoErrors();
```

<a name="assert-session-doesnt-have-errors"></a>
#### assertSessionDoesntHaveErrors

断言会话中给定的键没有验证错误：

```php
$response->assertSessionDoesntHaveErrors($keys = [], $format = null, $errorBag = 'default');
```

> [!NOTE]
> 你可以使用更通用的 [assertValid](#assert-valid) 方法，断言响应没有以 JSON 返回的验证错误，**并且**没有错误被暂存到会话中。

<a name="assert-session-missing"></a>
#### assertSessionMissing

断言会话中不存在给定的键：

```php
$response->assertSessionMissing($key);
```

<a name="assert-session-missing-input"></a>
#### assertSessionMissingInput

断言会话的暂存输入数组中不存在给定的输入键：

```php
$response->assertSessionMissingInput($key);
```

<a name="assert-status"></a>
#### assertStatus

断言响应具有给定的 HTTP 状态码：

```php
$response->assertStatus($code);
```

<a name="assert-successful"></a>
#### assertSuccessful

断言响应的 HTTP 状态码为成功状态（>= 200 且 < 300）：

```php
$response->assertSuccessful();
```

<a name="assert-too-many-requests"></a>
#### assertTooManyRequests

断言响应的 HTTP 状态码为请求过多（429）：

```php
$response->assertTooManyRequests();
```

<a name="assert-unauthorized"></a>
#### assertUnauthorized

断言响应的 HTTP 状态码为未授权（401）：

```php
$response->assertUnauthorized();
```

<a name="assert-unprocessable"></a>
#### assertUnprocessable

断言响应的 HTTP 状态码为无法处理的实体（422）：

```php
$response->assertUnprocessable();
```

<a name="assert-unsupported-media-type"></a>
#### assertUnsupportedMediaType

断言响应的 HTTP 状态码为不支持的媒体类型（415）：

```php
$response->assertUnsupportedMediaType();
```

<a name="assert-valid"></a>
#### assertValid

断言响应中给定的键没有验证错误。验证错误以 JSON 结构返回或被暂存到会话中时，都可以使用该方法进行断言：

```php
// 断言不存在验证错误……
$response->assertValid();

// 断言给定的键没有验证错误……
$response->assertValid(['name', 'email']);
```

<a name="assert-invalid"></a>
#### assertInvalid

断言响应中给定的键存在验证错误。验证错误以 JSON 结构返回或被暂存到会话中时，都可以使用该方法进行断言：

```php
$response->assertInvalid(['name', 'email']);
```

你也可以断言给定的键具有特定的验证错误消息。此时，你可以提供完整的错误消息，也可以只提供其中一小部分：

```php
$response->assertInvalid([
    'name' => 'The name field is required.',
    'email' => 'valid email address',
]);
```

如果你想断言只有给定的字段存在验证错误，可以使用 `assertOnlyInvalid` 方法：

```php
$response->assertOnlyInvalid(['name', 'email']);
```

<a name="assert-view-has"></a>
#### assertViewHas

断言响应中的视图包含给定的数据：

```php
$response->assertViewHas($key, $value = null);
```

将闭包作为第二个参数传递给 `assertViewHas` 方法，可以让你检查特定的视图数据，并对其进行断言：

```php
$response->assertViewHas('user', function (User $user) {
    return $user->name === 'Taylor';
});
```

此外，你可以像访问数组变量一样访问响应中的视图数据，方便对其进行检查：

```php tab=Pest
expect($response['name'])->toBe('Taylor');
```

```php tab=PHPUnit
$this->assertEquals('Taylor', $response['name']);
```

<a name="assert-view-has-all"></a>
#### assertViewHasAll

断言响应中的视图包含给定的数据列表：

```php
$response->assertViewHasAll(array $data);
```

你可以使用该方法，仅断言视图包含与给定键对应的数据：

```php
$response->assertViewHasAll([
    'name',
    'email',
]);
```

或者，你可以断言视图数据存在且具有指定的值：

```php
$response->assertViewHasAll([
    'name' => 'Taylor Otwell',
    'email' => 'taylor@example.com,',
]);
```

<a name="assert-view-is"></a>
#### assertViewIs

断言路由返回了给定的视图：

```php
$response->assertViewIs($value);
```

<a name="assert-view-missing"></a>
#### assertViewMissing

断言给定的数据键没有提供给应用响应所返回的视图：

```php
$response->assertViewMissing($key);
```

<a name="authentication-assertions"></a>
### 身份验证断言

Laravel 还提供了多种与身份验证相关的断言，供你在应用的功能测试中使用。请注意，这些方法是在测试类本身上调用的，而非在 `get`、`post` 等方法返回的 `Illuminate\Testing\TestResponse` 实例上调用。

<a name="assert-authenticated"></a>
#### assertAuthenticated

断言用户已通过身份验证：

```php
$this->assertAuthenticated($guard = null);
```

<a name="assert-guest"></a>
#### assertGuest

断言用户未通过身份验证：

```php
$this->assertGuest($guard = null);
```

<a name="assert-authenticated-as"></a>
#### assertAuthenticatedAs

断言指定用户已通过身份验证：

```php
$this->assertAuthenticatedAs($user, $guard = null);
```

<a name="validation-assertions"></a>
## 验证断言

Laravel 提供了两个主要的验证相关断言，用于确保请求中提供的数据有效或无效。

<a name="validation-assert-valid"></a>
#### assertValid

断言响应中给定的键没有验证错误。验证错误以 JSON 结构返回或被暂存到会话中时，都可以使用该方法进行断言：

```php
// 断言不存在验证错误……
$response->assertValid();

// 断言给定的键没有验证错误……
$response->assertValid(['name', 'email']);
```

<a name="validation-assert-invalid"></a>
#### assertInvalid

断言响应中给定的键存在验证错误。验证错误以 JSON 结构返回或被暂存到会话中时，都可以使用该方法进行断言：

```php
$response->assertInvalid(['name', 'email']);
```

你也可以断言给定的键具有特定的验证错误消息。此时，你可以提供完整的错误消息，也可以只提供其中一小部分：

```php
$response->assertInvalid([
    'name' => 'The name field is required.',
    'email' => 'valid email address',
]);
```

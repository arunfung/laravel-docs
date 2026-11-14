# Laravel Sanctum

- [简介](#introduction)
    - [工作原理](#how-it-works)
- [安装](#installation)
- [配置](#configuration)
    - [覆盖默认模型](#overriding-default-models)
- [API 令牌认证](#api-token-authentication)
    - [颁发 API 令牌](#issuing-api-tokens)
    - [令牌权限](#token-abilities)
    - [保护路由](#protecting-routes)
    - [撤销令牌](#revoking-tokens)
    - [令牌过期](#token-expiration)
- [SPA 认证](#spa-authentication)
    - [配置](#spa-configuration)
    - [认证](#spa-authenticating)
    - [保护路由](#protecting-spa-routes)
    - [授权私有广播频道](#authorizing-private-broadcast-channels)
- [移动应用认证](#mobile-application-authentication)
    - [颁发 API 令牌](#issuing-mobile-api-tokens)
    - [保护路由](#protecting-mobile-api-routes)
    - [撤销令牌](#revoking-mobile-api-tokens)
- [测试](#testing)

<a name="introduction"></a>
## 简介

[Laravel Sanctum](https://github.com/laravel/sanctum) 为 SPA（单页应用程序）、移动应用程序和简单的基于令牌的 API 提供了一个轻量级的身份验证系统。Sanctum 允许应用程序的每个用户为他们的账户生成多个 API 令牌。这些令牌可以被授予能力和作用域，用来指定令牌被允许执行的操作。

<a name="how-it-works"></a>
### 工作原理

Laravel Sanctum 旨在解决两个不同的问题。在深入研究该库之前，让我们先讨论一下这两个问题。

<a name="how-it-works-api-tokens"></a>
#### API 令牌

首先，Sanctum 是一个简单的包，你可以用它来为用户颁发 API 令牌，而无需使用复杂的 OAuth。这个功能受到了 GitHub 和其他颁发"个人访问令牌"的应用程序的启发。例如，假设你的应用程序的"账户设置"有一个屏幕，用户可以在那里为他们的账户生成 API 令牌。你可以使用Sanctum 来生成和管理这些令牌。这些令牌通常有很长的过期时间（几年），但用户可以随时手动撤销它们。

Laravel Sanctum 通过将用户 API 令牌存储在单个数据库表中，并通过包含有效 API 令牌的`Authorization`头来验证传入的 HTTP 请求来提供此功能。

<a name="how-it-works-spa-authentication"></a>
#### SPA 认证

其次，Sanctum 提供了一种简单的方法来认证需要与 Laravel 驱动的 API 通信的单页应用程序（SPA）。这些 SPA 可能与你的 Laravel 应用存在于同一个仓库中，也可能存在于完全独立的仓库中，例如使用 Next.js 或 Nuxt 创建的 SPA。

对于这一功能，Sanctum 不使用任何类型的令牌。相反，Sanctum 使用 Laravel 内置的基于 cookie 的会话认证服务。通常，Sanctum 利用 Laravel 的 `web` 认证守卫来实现这一点。这提供了 CSRF 保护、会话认证的好处，同时还防止了通过 XSS 泄露认证凭据。

当传入请求来自你自己的 SPA 前端时，Sanctum 仅尝试使用 cookie 进行认证。当 Sanctum 检查一个传入的 HTTP 请求时，它首先检查认证 cookie，如果不存在，Sanctum 然后会检查 `Authorization` 头部以寻找有效的 API 令牌。

> [!NOTE]
> 仅将 Sanctum 用于 API 令牌认证或仅用于 SPA 认证都是完全可以的。使用 Sanctum 并不意味着你必须使用它提供的两个功能。

<a name="installation"></a>
## 安装

你可以通过 `install:api` Artisan 命令安装 Laravel Sanctum:

```shell
php artisan install:api
```

接下来，如果你计划使用Sanctum 来认证一个 SPA, 请参考本文档的 [SPA 认证](#spa-authentication) 部分

<a name="configuration"></a>
## 配置

<a name="overriding-default-models"></a>
### 重写默认模型

虽然通常不需要，但你可以自由扩展 Sanctum 内部使用的 `PersonalAccessToken` 模型:

```php
use Laravel\Sanctum\PersonalAccessToken as SanctumPersonalAccessToken;

class PersonalAccessToken extends SanctumPersonalAccessToken
{
    // ...
}
```

然后，你可以通过 Sanctum 提供的 `usePersonalAccessTokenModel` 方法指示 Sanctum 使用你的自定义模型。通常，你应该在你的应用程序的  `AppServiceProvider` 文件的 `boot` 方法中调用此方法:

```php
use App\Models\Sanctum\PersonalAccessToken;
use Laravel\Sanctum\Sanctum;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Sanctum::usePersonalAccessTokenModel(PersonalAccessToken::class);
}
```

<a name="api-token-authentication"></a>
## API 令牌认证

> [!NOTE]
> 你不应该使用 API 令牌来认证你自己的第一方 SPA。相反，应使用 Sanctum 内置的 [SPA 认证功能](#spa-authentication).

<a name="issuing-api-tokens"></a>
### 发放 API 令牌

Sanctum 允许你发放可用于向你的应用程序发起 API 请求的 API 令牌 / 个人访问令牌。在使用 API 令牌发起请求时，令牌应该作为 `Bearer` 令牌包含在 `Authorization` 请求头中。

要开始为用户发放令牌，你的 User 模型应该使用 `Laravel\Sanctum\HasApiTokens` trait:

```php
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;
}
```

要发放令牌，你可以使用 `createToken` 方法。`createToken` 方法会返回一个 `Laravel\Sanctum\NewAccessToken` 实例。 API 令牌在存储到数据库之前会使用 SHA-256 进行哈希处理，但你可以通过 `NewAccessToken` 实例的 `plainTextToken` 属性访问令牌的明文值。你应该在令牌创建后立即将此值显示给用户：

```php
use Illuminate\Http\Request;

Route::post('/tokens/create', function (Request $request) {
    $token = $request->user()->createToken($request->token_name);

    return ['token' => $token->plainTextToken];
});
```

你可以使用 `HasApiTokens` trait 提供的 `tokens` Eloquent 关系来访问用户的所有令牌：

```php
foreach ($user->tokens as $token) {
    // ...
}
```

<a name="token-abilities"></a>
### 令牌权限

Sanctum 允许你为令牌分配"权限"。权限的作用类似于 OAuth 的"作用域"。你可以将字符串权限数组作为第二个参数传递给 `createToken` 方法：

```php
return $user->createToken('token-name', ['server:update'])->plainTextToken;
```

当处理一个由 Sanctum 认证的传入请求时，你可以使用 `tokenCan` 或 `tokenCant` 方法来确定令牌是否具有给定的权限：

```php
if ($user->tokenCan('server:update')) {
    // ...
}

if ($user->tokenCant('server:update')) {
    // ...
}
```

<a name="token-ability-middleware"></a>
#### 令牌权限中间件

Sanctum 还包含了两个中间件，可用于验证传入请求是否由具有给定权限的令牌进行认证。首先，在你的应用程序的 `bootstrap/app.php` 文件中定义以下中间件别名：

```php
use Laravel\Sanctum\Http\Middleware\CheckAbilities;
use Laravel\Sanctum\Http\Middleware\CheckForAnyAbility;

->withMiddleware(function (Middleware $middleware): void {
    $middleware->alias([
        'abilities' => CheckAbilities::class,
        'ability' => CheckForAnyAbility::class,
    ]);
})
```

`abilities` 中间件可以分配给路由，以验证传入请求的令牌是否具有所有列出的权限：

```php
Route::get('/orders', function () {
    // 令牌同时具有 "check-status" 和 "place-orders" 权限...
})->middleware(['auth:sanctum', 'abilities:check-status,place-orders']);
```

`ability` 中间件可以分配给路由，以验证传入请求的令牌是否具有列出权限中的至少一个：

```php
Route::get('/orders', function () {
    // 令牌具有 "check-status" 或 "place-orders" 权限...
})->middleware(['auth:sanctum', 'ability:check-status,place-orders']);
```

<a name="first-party-ui-initiated-requests"></a>
#### 第一方 UI 发起的请求

为了方便起见，如果传入的已认证请求来自你的第一方 SPA，并且你正在使用 Sanctum 内置的 [SPA 认证](#spa-authentication) ，那么  `tokenCan` 将始终返回 `true`。

然而，这并不一定意味着你的应用程序必须允许用户执行该操作。通常，你的应用程序的 [授权策略](/docs/{{version}}/authorization#creating-policies) 将确定令牌是否被授予执行这些权限的权限，以及检查用户实例本身是否应该被允许执行该操作。

例如，如果我们想象一个管理服务器的应用程序，这可能意味着检查令牌是否被授权更新服务器**并且**服务器属于该用户：

```php
return $request->user()->id === $server->user_id &&
       $request->user()->tokenCan('server:update');
```

起初，允许 `tokenCan` 方法被调用并始终为第一方 UI 发起的请求返回 `true` 可能看起来很奇怪；但是，能够始终假设 API 令牌可用并通过 `tokenCan` 方法进行检查是很方便的。通过采用这种方法，你可以在应用程序的授权策略中始终调用 `tokenCan` 方法，而无需担心请求是从你的应用程序 UI 触发的还是由你的 API 的第三方消费者发起的。

<a name="protecting-routes"></a>
### 保护路由

为了保护路由，确保所有传入请求都必须经过身份验证，你应该在 `routes/web.php` 和 `routes/api.php` 路由文件中，将 `sanctum` 认证守卫附加到受保护的路由上。该守卫确保传入请求要么是使用 cookie 认证的有状态请求，要么在来自第三方时包含有效的 API 令牌请求头。

你可能想知道为什么我们建议在应用程序的`routes/web.php` 文件中使用 `sanctum` 守卫来保护路由。请记住，Sanctum 会首先尝试使用 Laravel 标准的会话认证 cookie 来验证传入请求。如果该 cookie 不存在，Sanctum 将尝试使用请求 `Authorization` 头中的令牌进行认证。此外，使用 Sanctum 认证所有请求可以确保我们始终能够在当前认证的用户实例上调用 `tokenCan` 方法：

```php
use Illuminate\Http\Request;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');
```

<a name="revoking-tokens"></a>
### 撤销令牌

你可以使用 `Laravel\Sanctum\HasApiTokens` trait 提供的 `tokens` 关系从数据库中删除令牌来"撤销"令牌：

```php
// 撤销所有令牌...
$user->tokens()->delete();

// 撤销用于认证当前请求的令牌...
$request->user()->currentAccessToken()->delete();

// 撤销特定令牌...
$user->tokens()->where('id', $tokenId)->delete();
```

<a name="token-expiration"></a>
### 令牌过期

默认情况下，Sanctum 令牌永不过期，只能通过[撤销令牌](#revoking-tokens)来使其失效。但是，如果你希望为应用程序的 API 令牌配置过期时间，可以通过应用程序 `sanctum` 配置文件中的 `expiration` 配置选项来设置。此配置选项定义了令牌颁发后多少分钟内有效：

```php
'expiration' => 525600,
```

如果你想为每个令牌单独指定过期时间，可以将过期时间作为第三个参数传递给 `createToken` 方法：

```php
return $user->createToken(
    'token-name', ['*'], now()->plus(weeks: 1)
)->plainTextToken;
```

如果你已经为应用程序配置了令牌过期时间，你可能还希望 [安排任务](/docs/{{version}}/scheduling) 来清理过期的令牌。幸运的是，Sanctum 提供了一个 `sanctum:prune-expired`  命令来帮助你完成这项工作。例如，你可以配置一个计划任务来删除已过期至少 24 小时的所有令牌数据库记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('sanctum:prune-expired --hours=24')->daily();
```

<a name="spa-authentication"></a>
## SPA 认证

Sanctum 还提供了一种简单的方法来认证需要与 Laravel 驱动的 API 进行通信的单页应用程序（SPA）。这些 SPA 可能与你的 Laravel 应用程序存在于同一个代码库中，也可能是完全独立的代码库。

对于此功能，Sanctum 不使用任何形式的令牌。相反，Sanctum 使用 Laravel 内置的基于 cookie 的会话认证服务。这种认证方式提供了 CSRF 保护、会话认证的好处，同时还能防止通过 XSS 泄露认证凭证。

> [!WARNING]
> 为了进行认证，你的 SPA 和 API 必须共享相同的顶级域名。但是，它们可以位于不同的子域名上。此外，你应该确保在请求中发送 `Accept: application/json`  头部以及 `Referer` 或 `Origin` 头部。

<a name="spa-configuration"></a>
### 配置

<a name="configuring-your-first-party-domains"></a>
#### 配置第一方域名

首先，你应该配置 SPA 将从哪些域名发起请求。你可以使用 `sanctum` 配置文件中的 `stateful` 配置选项来配置这些域名。此配置设置决定了在向你的 API 发起请求时，哪些域名将使用 Laravel 会话 cookie 来维持"有状态"的认证。

为了帮助你设置第一方有状态域名，Sanctum 提供了两个辅助函数，你可以将它们包含在配置中。首先，`Sanctum::currentApplicationUrlWithPort()` 将从 `APP_URL`  环境变量返回当前应用程序 URL，而 `Sanctum::currentRequestHost()`  将在有状态域名列表中注入一个占位符，该占位符在运行时会被当前请求的主机名替换，这样所有来自相同域名的请求都被视为有状态的。

> [!WARNING]
> 如果你通过包含端口的 URL（如 `127.0.0.1:8000`）访问应用程序，你应该确保在域名中包含端口号。

<a name="sanctum-middleware"></a>
#### Sanctum 中间件

接下来，你应该告知 Laravel 来自 SPA 的传入请求可以使用 Laravel 的会话 cookie 进行认证，同时仍然允许来自第三方或移动应用程序的请求使用 API 令牌进行认证。这可以通过在应用程序的 `bootstrap/app.php` 文件中调用 `statefulApi` 中间件方法轻松实现：

```php
->withMiddleware(function (Middleware $middleware): void {
    $middleware->statefulApi();
})
```

<a name="cors-and-cookies"></a>
#### CORS 和 Cookies

如果你在从不同子域名上运行的 SPA 向应用程序进行认证时遇到问题，可能是你的 CORS（跨域资源共享）或会话 cookie 设置配置错误。

默认情况下，`config/cors.php` 配置文件不会被自动发布。如果你需要自定义 Laravel 的 CORS 选项，应使用 `config:publish` Artisan 命令发布完整的 `cors` 配置文件：

```shell
php artisan config:publish cors
```

接下来，你应该确保应用程序的 CORS 配置返回值为 `True` 的 `Access-Control-Allow-Credentials` 头部。这可以通过将应用程序 `config/cors.php` 配置文件中的 `supports_credentials` 选项设置为 `true` 来实现。

此外，你应该在应用的全局 `axios` 实例上启用 `withCredentials` 和 `withXSRFToken` 选项。这可以在 `resources/js/app.js` 文件中完成。如果你不使用 Axios 从前端发起 HTTP 请求，应在自己的 HTTP 客户端上执行等效配置：

```js
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;
```

最后，您应确保应用的会话 Cookie 域配置支持根域的任何子域。 您可以在应用的 `config/session.php` 配置文件中通过为域名添加前导 `.` 来实现：

```php
'domain' => '.domain.com',
```

<a name="spa-authenticating"></a>
### 身份验证

<a name="csrf-protection"></a>
#### CSRF 保护

要对 SPA 进行身份验证，您的 SPA 的「登录」页面应首先向 `/sanctum/csrf-cookie` 端点发起请求，以初始化应用的 CSRF 保护：

```js
axios.get('/sanctum/csrf-cookie').then(response => {
    // 登录...
});
```

在此请求期间，Laravel 将设置一个包含当前 CSRF 令牌的 `XSRF-TOKEN` Cookie。 该令牌应进行 URL 解码，并在后续请求中通过 `X-XSRF-TOKEN` 标头传递，一些 HTTP 客户端库（如 Axios 和 Angular HttpClient）会自动为您完成此操作。 如果您的 JavaScript HTTP 库没有为您设置该值，您需要手动将 `X-XSRF-TOKEN` 标头设置为与此路由设置的 `XSRF-TOKEN` Cookie 的 URL 解码值匹配。

<a name="logging-in"></a>
#### 登录

初始化 CSRF 保护后，您应向 Laravel 应用的 `/login` 路由发起 `POST` 请求。 该 `/login` 路由可以 [手动实现](/docs/{{version}}/authentication#authenticating-users) 或使用无头身份验证包（如 [Laravel Fortify](/docs/{{version}}/fortify)）来实现。

如果登录请求成功，您将通过身份验证，并且对应用程序路由的后续请求将通过 Laravel 应用程序颁发给客户端的会话 Cookie 自动进行身份验证。此外，由于您的应用程序已经向 `/sanctum/csrf-cookie` 路由发出了请求，只要您的 JavaScript HTTP 客户端在 `X-XSRF-TOKEN` 标头中发送 `XSRF-TOKEN` Cookie 的值，后续请求就会自动受到 CSRF 保护。

当然，如果由于长时间无活动导致用户会话过期，后续对 Laravel 应用程序的请求可能会收到 401 或 419 HTTP 错误响应。在这种情况下，您应将用户重定向到 SPA 的登录页面。

由于这种 SPA 认证方式基于会话，你可以使用 Laravel 的标准认证服务，包括[「记住我」](/docs/{{version}}/authentication#remembering-users)功能。

> [!WARNING]
> 您可以自由编写自己的 `/login` 端点；但是，您应确保它使用 Laravel 提供的标准的 [基于会话的身份验证服务](/docs/{{version}}/authentication#authenticating-users) 对用户进行身份验证。通常，这意味着使用 `web` 认证守卫。

<a name="protecting-spa-routes"></a>
### 保护路由

为了保护路由，使得所有传入请求都必须经过身份验证，您应该在 `routes/api.php` 文件中的 API 路由上附加 `sanctum` 身份验证守卫。此守卫将确保传入的请求要么是来自您的 SPA 的有状态认证请求，要么如果请求来自第三方，则包含有效的 API 令牌头：

```php
use Illuminate\Http\Request;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');
```

<a name="authorizing-private-broadcast-channels"></a>
### 授权私有广播频道

如果您的 SPA 需要通过 [私有/存在广播频道](/docs/{{version}}/broadcasting#authorizing-channels) 进行身份验证，您应该从应用程序 `bootstrap/app.php` 文件中的 `withRouting` 方法中移除 `channels` 条目。相反，您应该调用 `withBroadcasting` 方法，以便为应用程序的广播路由指定正确的中间件：

```php
return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        // ...
    )
    ->withBroadcasting(
        __DIR__.'/../routes/channels.php',
        ['prefix' => 'api', 'middleware' => ['api', 'auth:sanctum']],
    )
    ->create();
```

接下来，为了让 Pusher 的授权请求成功，您需要在初始化 [Laravel Echo](/docs/{{version}}/broadcasting#client-side-installation) 时提供一个自定义的 Pusher `authorizer`。这允许您的应用配置 Pusher 使用 [为跨域请求正确配置](#cors-and-cookies) 的 `axios` 实例：

```js
window.Echo = new Echo({
    broadcaster: "pusher",
    cluster: import.meta.env.VITE_PUSHER_APP_CLUSTER,
    encrypted: true,
    key: import.meta.env.VITE_PUSHER_APP_KEY,
    authorizer: (channel, options) => {
        return {
            authorize: (socketId, callback) => {
                axios.post('/api/broadcasting/auth', {
                    socket_id: socketId,
                    channel_name: channel.name
                })
                .then(response => {
                    callback(false, response.data);
                })
                .catch(error => {
                    callback(true, error);
                });
            }
        };
    },
})
```

<a name="mobile-application-authentication"></a>
## 移动应用身份验证

您也可以使用 Sanctum 令牌来验证移动应用向 API 发出的请求。移动应用请求的身份验证过程与验证第三方 API 请求类似；但是，在发放 API 令牌的方式上存在一些小的差异。

<a name="issuing-mobile-api-tokens"></a>
### 发放 API 令牌

首先，创建一个路由来接收用户的电子邮件/用户名、密码和设备名称，然后将这些凭据交换为一个新的 Sanctum 令牌。给予此端点的「设备名称」用于信息目的，可以是您希望的任何值。通常，设备名称值应该是用户能够识别的名称，例如「Nuno 的 iPhone 17」。

通常，您将从移动应用的「登录」屏幕向令牌端点发出请求。该端点将返回纯文本 API 令牌，然后可以将其存储在移动设备上并用于发出其他 API 请求：

```php
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

Route::post('/sanctum/token', function (Request $request) {
    $request->validate([
        'email' => 'required|email',
        'password' => 'required',
        'device_name' => 'required',
    ]);

    $user = User::where('email', $request->email)->first();

    if (! $user || ! Hash::check($request->password, $user->password)) {
        throw ValidationException::withMessages([
            'email' => ['The provided credentials are incorrect.'],
        ]);
    }

    return $user->createToken($request->device_name)->plainTextToken;
});
```

当移动应用使用令牌向您的应用发起 API 请求时，应在 `Authorization` 头中以 `Bearer` 令牌的形式传递该令牌。

> [!NOTE]
> 在为移动应用发放令牌时，您也可以自由指定 [令牌权限](#token-abilities)。

<a name="protecting-mobile-api-routes"></a>
### 保护路由

如前所述，您可以通过附加 `sanctum` 认证守卫来保护路由，使得所有传入请求都必须经过身份验证：

```php
Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');
```

<a name="revoking-mobile-api-tokens"></a>
### 撤销令牌

为了让用户能够撤销发放给移动设备的 API 令牌，您可以在 Web 应用 UI 的「账户设置」部分按名称列出它们，并提供一个「撤销」按钮。当用户点击「撤销」按钮时，您可以从数据库中删除该令牌。请记住，您可以通过 `Laravel\Sanctum\HasApiTokens` trait 提供的 `tokens` 关联关系访问用户的 API 令牌：

```php
// 撤销所有令牌...
$user->tokens()->delete();

// 撤销特定令牌...
$user->tokens()->where('id', $tokenId)->delete();
```

<a name="testing"></a>
## 测试

在测试时，可以使用 `Sanctum::actingAs` 方法来验证用户身份并指定应授予其令牌的权限：

```php tab=Pest
use App\Models\User;
use Laravel\Sanctum\Sanctum;

test('task list can be retrieved', function () {
    Sanctum::actingAs(
        User::factory()->create(),
        ['view-tasks']
    );

    $response = $this->get('/api/task');

    $response->assertOk();
});
```

```php tab=PHPUnit
use App\Models\User;
use Laravel\Sanctum\Sanctum;

public function test_task_list_can_be_retrieved(): void
{
    Sanctum::actingAs(
        User::factory()->create(),
        ['view-tasks']
    );

    $response = $this->get('/api/task');

    $response->assertOk();
}
```

如果您想授予令牌所有权限，应在提供给 `actingAs` 方法的权限列表中包含 `*`：

```php
Sanctum::actingAs(
    User::factory()->create(),
    ['*']
);
```

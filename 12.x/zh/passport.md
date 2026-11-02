
# Laravel Passport

- [简介](#introduction)
    - [Passport 还是 Sanctum?](#passport-or-sanctum)
- [安装](#installation)
    - [部署 Passport](#deploying-passport)
    - [升级 Passport](#upgrading-passport)
- [配置](#configuration)
    - [令牌生命周期](#token-lifetimes)
    - [覆盖默认模型](#overriding-default-models)
    - [覆盖默认路由](#overriding-routes)
- [授权码模式](#authorization-code-grant)
    - [管理客户端](#managing-clients)
    - [请求令牌](#requesting-tokens)
    - [管理令牌](#managing-tokens)
    - [刷新令牌](#refreshing-tokens)
    - [撤销令牌](#revoking-tokens)
    - [清理令牌](#purging-tokens)
- [带 PKCE 的授权码模式](#code-grant-pkce)
    - [创建客户端](#creating-a-auth-pkce-grant-client)
    - [请求令牌](#requesting-auth-pkce-grant-tokens)
- [设备授权模式](#device-authorization-grant)
    - [创建设备授权客户端](#creating-a-device-authorization-grant-client)
    - [请求令牌](#requesting-device-authorization-grant-tokens)
- [密码模式](#password-grant)
    - [创建密码授权客户端](#creating-a-password-grant-client)
    - [请求令牌](#requesting-password-grant-tokens)
    - [请求所有作用域](#requesting-all-scopes)
    - [自定义用户提供器](#customizing-the-user-provider)
    - [自定义用户名字段](#customizing-the-username-field)
    - [自定义密码验证](#customizing-the-password-validation)
- [隐式授权模式](#implicit-grant)
- [客户端凭证模式](#client-credentials-grant)
- [个人访问令牌](#personal-access-tokens)
    - [创建个人访问客户端](#creating-a-personal-access-client)
    - [自定义用户提供器](#customizing-the-user-provider-for-pat)
    - [管理个人访问令牌](#managing-personal-access-tokens)
- [路由保护](#protecting-routes)
    - [通过中间件](#via-middleware)
    - [传递访问令牌](#passing-the-access-token)
- [令牌作用域](#token-scopes)
    - [定义作用域](#defining-scopes)
    - [默认作用域](#default-scope)
    - [分配作用域给令牌](#assigning-scopes-to-tokens)
    - [检查作用域](#checking-scopes)
- [SPA 认证](#spa-authentication)
- [事件](#events)
- [测试](#testing)

<a name="introduction"></a>
## 简介

[Laravel Passport](https://github.com/laravel/passport) 能在几分钟内为您的 Laravel 应用提供完整的 OAuth2 服务器实现。Passport 基于 [League OAuth2 server](https://github.com/thephpleague/oauth2-server) 构建，该项目由 Andy Millington 和 Simon Hamp 维护。

> [!注意]
> 本文档假设您已熟悉 OAuth2。如果您对 OAuth2 不了解，建议先熟悉其通用的 [术语](https://oauth2.thephpleague.com/terminology/) 和特性再继续阅读。



<a name="passport-or-sanctum"></a>
### Passport 还是 Sanctum?

在开始之前，您可能需要确定您的应用更适合使用 Laravel Passport 还是 [Laravel Sanctum](/docs/laravel/12.x/sanctum)。如果您的应用必须支持 OAuth2，那么应该使用 Laravel Passport。

但是，如果您需要为单页应用、移动应用提供认证，或仅需发放 API 令牌，那么应该使用 [Laravel Sanctum](/docs/laravel/12.x/sanctum)。Laravel Sanctum 不支持 OAuth2，但它提供了更简单的 API 认证开发体验。

<a name="installation"></a>
## 安装

您可以通过 `install:api` Artisan 命令安装 Laravel Passport：

```shell
php artisan install:api --passport
```

该命令将发布并运行必要的数据库迁移，创建用于存储 OAuth2 客户端和访问令牌的表。同时还会创建生成安全访问令牌所需的加密密钥。

运行  `install:api` 命令后，将 `Laravel\Passport\HasApiTokens` trait 和 `Laravel\Passport\Contracts\OAuthenticatable` 接口添加到您的 `App\Models\User` 模型中。该 trait 会为模型提供一些辅助方法，用于检查已认证用户的令牌和作用域：

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Passport\Contracts\OAuthenticatable;
use Laravel\Passport\HasApiTokens;

class User extends Authenticatable implements OAuthenticatable
{
    use HasApiTokens, HasFactory, Notifiable;
}
```

最后，在应用的 `config/auth.php` 配置文件中，应定义一个 `api` 认证守卫并将 `driver` 选项设置为 `passport`。这将指示应用在认证传入的 API 请求时使用 Passport 的 `TokenGuard`:

```php
'guards' => [
    'web' => [
        'driver' => 'session',
        'provider' => 'users',
    ],

    'api' => [
        'driver' => 'passport',
        'provider' => 'users',
    ],
],
```



<a name="deploying-passport"></a>
### 部署 Passport

首次将 Passport 部署到应用服务器时，可能需要运行 `passport:keys` 命令。该命令生成 Passport 生成访问令牌所需的加密密钥。生成的密钥通常不纳入版本控制：

```shell
php artisan passport:keys
```

如有需要，可以定义 Passport 密钥的加载路径。使用 `Passport::loadKeysFrom` 方法实现此功能。通常，应在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用此方法：

```php
/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Passport::loadKeysFrom(__DIR__.'/../secrets/oauth');
}
```

<a name="loading-keys-from-the-environment"></a>
#### 从环境变量加载密钥

或者，您可以使用 `vendor:publish` Artisan 命令发布 Passport 的配置文件：

```shell
php artisan vendor:publish --tag=passport-config
```

发布配置文件后，可以通过环境变量定义应用的加密密钥：

```ini
PASSPORT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
<private key here>
-----END RSA PRIVATE KEY-----"

PASSPORT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
<public key here>
-----END PUBLIC KEY-----"
```

<a name="upgrading-passport"></a>
### 升级 Passport

升级到 Passport 的新主要版本时，请务必仔细查阅 [升级指南](https://github.com/laravel/passport/blob/master/UPGRADE.md)。

<a name="configuration"></a>
## 配置

<a name="token-lifetimes"></a>
### 令牌生命周期

默认情况下，Passport 颁发长期有效的访问令牌，有效期为一年。如需配置更长或更短的令牌生命周期，可以使用 `tokensExpireIn`, `refreshTokensExpireIn`, 和 `personalAccessTokensExpireIn` 方法。这些方法应在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用：

```php
use Carbon\CarbonInterval;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Passport::tokensExpireIn(CarbonInterval::days(15));
    Passport::refreshTokensExpireIn(CarbonInterval::days(30));
    Passport::personalAccessTokensExpireIn(CarbonInterval::months(6));
}
```

> [!警告]
> Passport 数据库表中的 `expires_at` 列是只读的，仅用于显示目的。颁发令牌时，Passport 将过期信息存储在签名和加密的令牌中。如需使令牌失效，应 [撤销令牌](#revoking-tokens).



### 覆盖默认模型（Overriding Default Models）

你可以通过定义你自己的模型并扩展相应的 Passport 模型，来自由地扩展 Passport 内部使用的模型：

```php
use Laravel\Passport\Client as PassportClient;

class Client extends PassportClient
{
    // ...
}
```

在定义你的模型之后，你可以通过 `Laravel\Passport\Passport` 类指示 Passport 使用你的自定义模型。通常，你应该在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中告知 Passport 你的自定义模型：

```php
use App\Models\Passport\AuthCode;
use App\Models\Passport\Client;
use App\Models\Passport\DeviceCode;
use App\Models\Passport\RefreshToken;
use App\Models\Passport\Token;

/**
 * 初始化应用程序所需的服务。
 */
public function boot(): void
{
    Passport::useTokenModel(Token::class);
    Passport::useRefreshTokenModel(RefreshToken::class);
    Passport::useAuthCodeModel(AuthCode::class);
    Passport::useClientModel(Client::class);
    Passport::useDeviceCodeModel(DeviceCode::class)
}
```

### 覆盖路由（Overriding Routes）

有时你可能希望自定义 Passport 定义的路由。为了实现这一点，你首先需要通过在应用程序的 `AppServiceProvider` 的 `register` 方法中添加 `Passport::ignoreRoutes` 来忽略 Passport 注册的路由：

```php
use Laravel\Passport\Passport;

/**
 * 注册应用程序中需要的服务。
 */
public function register(): void
{
    Passport::ignoreRoutes();
}
```

然后，你可以将 Passport 在其 [路由文件](https://github.com/laravel/passport/blob/master/routes/web.php) 中定义的路由复制到你应用程序的 `routes/web.php` 文件中，并根据你的需要进行修改：

```php
Route::group([
    'as' => 'passport.',
    'prefix' => config('passport.path', 'oauth'),
    'namespace' => '\Laravel\Passport\Http\Controllers',
], function () {
    // Passport routes...
});
```

## 授权码授权流程（Authorization Code Grant）



使用 OAuth2 的授权码模式是大多数开发者最熟悉的方式。在这种模式下，客户端应用会把用户重定向到你的服务器，由用户决定是否授权该客户端获取访问令牌。

要开始使用这一流程，我们需要告诉 Passport 如何渲染授权页面。

你可以通过 `Laravel\Passport\Passport` 类提供的方法，自定义授权页面的渲染逻辑。一般来说，你会在应用的 `App\Providers\AppServiceProvider` 的 `boot` 方法中进行配置，例如：

```php
use Inertia\Inertia;
use Laravel\Passport\Passport;

public function boot(): void
{
    // 使用 Blade 视图
    Passport::authorizationView('auth.oauth.authorize');

    // 使用闭包自定义渲染（例如 Inertia）
    Passport::authorizationView(
        fn ($parameters) => Inertia::render('Auth/OAuth/Authorize', [
            'request' => $parameters['request'],
            'authToken' => $parameters['authToken'],
            'client' => $parameters['client'],
            'user' => $parameters['user'],
            'scopes' => $parameters['scopes'],
        ])
    );
}
```

Passport 会自动注册 `/oauth/authorize` 路由，并返回你所配置的授权页面。
你的 `auth.oauth.authorize` 视图需要包含两个表单：

-   一个发送 **POST** 请求到 `passport.authorizations.approve`，用于批准授权；

-   一个发送 **DELETE** 请求到 `passport.authorizations.deny`，用于拒绝授权。

这两个路由都会要求提交：`state`、`client_id`、`auth_token` 这几个字段。

### 客户端管理

如果其他开发者想让他们的应用与您的 API 通信，他们需要先在你的系统里为他们的应用创建一个“客户端”。通常，他们只需要提供应用的名称，以及在用户授权后，你的系统应将用户重定向回去的 URI。




#### 第一方客户端

创建客户端最简单的方式是使用 `passport:client` Artisan 命令。此命令可用于创建第一方客户端或测试你的 OAuth2 功能。当你运行 `passport:client` 命令时，Passport 会提示你提供关于你的客户端的更多信息，并会向你提供一个客户端 ID 和 secret：

```shell
php artisan passport:client
```

如果你想为你的客户端允许多个重定向 URI，你可以在 `passport:client` 命令提示输入 URI 时，使用逗号分隔的列表来指定它们。任何包含逗号的 URI 应当进行 URI 编码：

```shell
https://third-party-app.com/callback,https://example.com/oauth/redirect
```

#### 第三方客户端

由于你的应用程序的用户无法使用 `passport:client` 命令，你可以使用 `Laravel\Passport\ClientRepository` 类的 `createAuthorizationCodeGrantClient` 方法，为指定用户注册一个客户端：

```php
use App\Models\User;
use Laravel\Passport\ClientRepository;

$user = User::find($userId);

// 创建一个属于给定用户的 OAuth 应用客户端…
$client = app(ClientRepository::class)->createAuthorizationCodeGrantClient(
    user: $user,
    name: 'Example App',
    redirectUris: ['https://third-party-app.com/callback'],
    confidential: false,
    enableDeviceFlow: true
);

// 获取所有属于该用户的 OAuth 应用客户端…
$clients = $user->oauthApps()->get();
```

`createAuthorizationCodeGrantClient` 方法返回一个 `Laravel\Passport\Client` 实例。你可以将 `$client->id` 显示为客户端 ID，并将 `$client->plainSecret` 显示为客户端 secret 给用户。

### 请求令牌（Requesting Tokens）




#### 重定向以进行授权

一旦客户端被创建，开发者可以使用他们的客户端 ID 和密钥向你的应用请求授权码和访问令牌。首先，使用者的应用应向你的应用的 `/oauth/authorize` 路由发起重定向请求，如下所示：

```php
use Illuminate\Http\Request;
use Illuminate\Support\Str;

Route::get('/redirect', function (Request $request) {
    $request->session()->put('state', $state = Str::random(40));

    $query = http_build_query([
        'client_id' => 'your-client-id',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'response_type' => 'code',
        'scope' => 'user:read orders:create',
        'state' => $state,
        // 'prompt' => '', // "none", "consent", 或 "login"
    ]);

    return redirect('https://passport-app.test/oauth/authorize?'.$query);
});
```

`prompt` 参数可用于指定 Passport 应用的认证行为。

如果 `prompt` 值为 `none`，当用户尚未在 Passport 应用中认证时，Passport 将始终抛出认证错误。
如果值为 `consent`，即使所有权限（scopes）之前已授予给使用应用，Passport 也将始终显示授权批准界面。
如果值为 `login`，即使用户已有现有会话，Passport 也将始终提示用户重新登录应用。

如果未提供 `prompt` 值，只有当用户之前未授权使用应用访问请求的权限时，才会提示用户进行授权。

> [!注意]
> 请记住，`/oauth/authorize` 路由已经由 Passport 定义。你不需要手动定义此路由。

#### 批准请求


在接收授权请求时，Passport 会根据 `prompt` 参数的值（如果存在）自动响应，并可能向用户显示一个模板，让他们批准或拒绝该授权请求。如果用户批准请求，他们将被重定向回由使用应用指定的 `redirect_uri`。该 `redirect_uri` 必须与创建客户端时指定的 `redirect` URL 匹配。

有时你可能希望跳过授权提示，例如在授权**第一方客户端**时。你可以通过[扩展 `Client` 模型](#overriding-default-models)并定义 `skipsAuthorization` 方法来实现这一点。如果 `skipsAuthorization` 返回 `true`，客户端将被自动批准，并且用户将立即被重定向回 `redirect_uri`，除非使用应用在进行授权重定向时明确设置了 `prompt` 参数：

```php
<?php

namespace App\Models\Passport;

use Illuminate\Contracts\Auth\Authenticatable;
use Laravel\Passport\Client as BaseClient;

class Client extends BaseClient
{
    /**
     * 判断客户端是否应跳过授权提示。
     *
     * @param  \Laravel\Passport\Scope[]  $scopes
     */
    public function skipsAuthorization(Authenticatable $user, array $scopes): bool
    {
        return $this->firstParty();
    }
}
```

#### 将授权码转换为访问令牌

如果用户批准了授权请求，他们将被重定向回使用应用。使用应用首先应验证 `state` 参数是否与重定向前存储的值一致。如果 `state` 参数匹配，则使用应用应向你的应用发起 `POST` 请求，以请求访问令牌。请求应包含在用户批准授权请求时由你的应用发放的授权码：

```php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

Route::get('/callback', function (Request $request) {
    $state = $request->session()->pull('state');

    throw_unless(
        strlen($state) > 0 && $state === $request->state,
        InvalidArgumentException::class,
        '状态值无效。'
    );

    $response = Http::asForm()->post('https://passport-app.test/oauth/token', [
        'grant_type' => 'authorization_code',
        'client_id' => 'your-client-id',
        'client_secret' => 'your-client-secret',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'code' => $request->code,
    ]);

    return $response->json();
});
```



这个 `/oauth/token` 路由将返回一个包含 `access_token`、`refresh_token` 和 `expires_in` 属性的 JSON 响应。`expires_in` 属性包含访问令牌过期前的秒数。

> [!注意]
> 与 `/oauth/authorize` 路由一样，`/oauth/token` 路由已由 Passport 为你定义。无需手动定义此路由。

### 管理令牌

你可以使用 `Laravel\Passport\HasApiTokens` trait 的 `tokens` 方法检索用户已授权的令牌。例如，这可用于为用户提供一个仪表盘，以跟踪他们与第三方应用的连接情况：

```php
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\Date;
use Laravel\Passport\Token;

$user = User::find($userId);

// 获取该用户的所有有效令牌...
$tokens = $user->tokens()
    ->where('revoked', false)
    ->where('expires_at', '>', Date::now())
    ->get();

// 获取该用户与第三方 OAuth 应用客户端的所有连接...
$connections = $tokens->load('client')
    ->reject(fn (Token $token) => $token->client->firstParty())
    ->groupBy('client_id')
    ->map(fn (Collection $tokens) => [
        'client' => $tokens->first()->client,
        'scopes' => $tokens->pluck('scopes')->flatten()->unique()->values()->all(),
        'tokens_count' => $tokens->count(),
    ])
    ->values();
```

### 刷新令牌

如果你的应用发放的是短期访问令牌，用户将需要通过在发放访问令牌时提供的刷新令牌来刷新他们的访问令牌：

```php
use Illuminate\Support\Facades\Http;

$response = Http::asForm()->post('https://passport-app.test/oauth/token', [
    'grant_type' => 'refresh_token',
    'refresh_token' => 'the-refresh-token',
    'client_id' => 'your-client-id',
    'client_secret' => 'your-client-secret', // 仅对机密客户端必需...
    'scope' => 'user:read orders:create',
]);

return $response->json();
```

这个 `/oauth/token` 路由将返回一个包含 `access_token`、`refresh_token` 和 `expires_in` 属性的 JSON 响应。`expires_in` 属性包含访问令牌过期前的秒数。



### 撤销令牌

你可以使用 `Laravel\Passport\Token` 模型的 `revoke` 方法撤销一个令牌。你也可以使用 `Laravel\Passport\RefreshToken` 模型的 `revoke` 方法撤销令牌的刷新令牌：

```php
use Laravel\Passport\Passport;
use Laravel\Passport\Token;

$token = Passport::token()->find($tokenId);

// 撤销访问令牌...
$token->revoke();

// 撤销该令牌的刷新令牌...
$token->refreshToken?->revoke();

// 撤销该用户的所有令牌...
User::find($userId)->tokens()->each(function (Token $token) {
    $token->revoke();
    $token->refreshToken?->revoke();
});
```

### 清理令牌

当令牌被撤销或已过期时，你可能希望从数据库中清理它们。Passport 自带的 `passport:purge` Artisan 命令可以为你执行此操作：

```shell
# 清理已撤销和已过期的令牌、授权码和设备码...
php artisan passport:purge

# 仅清理已过期超过 6 小时的令牌...
php artisan passport:purge --hours=6

# 仅清理已撤销的令牌、授权码和设备码...
php artisan passport:purge --revoked

# 仅清理已过期的令牌、授权码和设备码...
php artisan passport:purge --expired
```

你还可以在应用的 `routes/console.php` 文件中配置[计划任务](/docs/laravel/12.x/scheduling)，定期自动修剪令牌：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('passport:purge')->hourly();
```

## 使用 PKCE 的授权码模式

带有 “Proof Key for Code Exchange” (PKCE) 的授权码模式是一种安全方式，用于让单页应用或移动应用认证以访问你的 API。当你无法保证客户端密钥能够被安全存储，或者为了降低授权码被攻击者截获的风险时，应使用此授权模式。在将授权码交换为访问令牌时，一组 “code verifier” 和 “code challenge” 将替代客户端密钥。



### 创建客户端

在你的应用可以通过带 PKCE 的授权码模式发放令牌之前，你需要创建一个启用 PKCE 的客户端。你可以使用 `passport:client` Artisan 命令并加上 `--public` 选项来完成此操作：

```shell
php artisan passport:client --public
```

### 请求令牌

#### Code Verifier 与 Code Challenge

由于此授权模式不提供客户端密钥，开发者需要生成一组 code verifier 和 code challenge 组合，以便请求令牌。

code verifier 应为 43 到 128 个字符之间的随机字符串，包含字母、数字，以及 `"-"`、`"."`、`"_"`、`"~"` 字符，如 [RFC 7636 规范](https://tools.ietf.org/html/rfc7636) 所定义。

code challenge 应为使用 URL 和文件名安全字符的 Base64 编码字符串。末尾的 `'='` 字符应移除，并且不应有换行符、空白或其他额外字符。

```php
$encoded = base64_encode(hash('sha256', $codeVerifier, true));

$codeChallenge = strtr(rtrim($encoded, '='), '+/', '-_');
```

#### 重定向以进行授权

一旦客户端被创建，你可以使用客户端 ID 以及生成的 code verifier 和 code challenge 向你的应用请求授权码和访问令牌。首先，使用应用应向你的应用的 `/oauth/authorize` 路由发起重定向请求：

```php
use Illuminate\Http\Request;
use Illuminate\Support\Str;

Route::get('/redirect', function (Request $request) {
    $request->session()->put('state', $state = Str::random(40));

    $request->session()->put(
        'code_verifier', $codeVerifier = Str::random(128)
    );

    $codeChallenge = strtr(rtrim(
        base64_encode(hash('sha256', $codeVerifier, true))
    , '='), '+/', '-_');

    $query = http_build_query([
        'client_id' => 'your-client-id',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'response_type' => 'code',
        'scope' => 'user:read orders:create',
        'state' => $state,
        'code_challenge' => $codeChallenge,
        'code_challenge_method' => 'S256',
        // 'prompt' => '', // "none", "consent", or "login"
    ]);

    return redirect('https://passport-app.test/oauth/authorize?'.$query);
});
```



### 将授权码转换为访问令牌

如果用户批准了授权请求，他们将被重定向回使用该授权的应用程序。和标准的授权码授权模式一样，消费端应当将 `state` 参数与重定向前存储的值进行验证。

如果 `state` 参数匹配，消费端应当向你的应用程序发起一个 `POST` 请求以请求访问令牌。该请求应当包含当用户批准授权请求时你的应用程序颁发的授权码，以及最初生成的 code verifier：

```php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

Route::get('/callback', function (Request $request) {
    $state = $request->session()->pull('state');

    $codeVerifier = $request->session()->pull('code_verifier');

    throw_unless(
        strlen($state) > 0 && $state === $request->state,
        InvalidArgumentException::class
    );

    $response = Http::asForm()->post('https://passport-app.test/oauth/token', [
        'grant_type' => 'authorization_code',
        'client_id' => 'your-client-id',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'code_verifier' => $codeVerifier,
        'code' => $request->code,
    ]);

    return $response->json();
});
```
### 设备授权许可（Device Authorization Grant）

OAuth2 设备授权许可允许无浏览器或输入受限的设备（例如电视和游戏主机）通过交换 “device code” 来获取访问令牌。当使用设备流程时，设备客户端会指示用户使用另一台设备（如电脑或智能手机）连接到你的服务器，在那里输入提供的 “user code”，并批准或拒绝访问请求。

为了开始，我们需要指示 Passport 如何返回我们的 “user code” 和 “authorization” 视图。



授权视图的所有渲染逻辑都可以通过 `Laravel\Passport\Passport` 类提供的相应方法进行自定义。通常，你应该在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用这些方法。

```php
use Inertia\Inertia;
use Laravel\Passport\Passport;

/**
 * 启动应用程序所需的各项服务。
 */
public function boot(): void
{
    // 通过提供视图名称...
    Passport::deviceUserCodeView('auth.oauth.device.user-code');
    Passport::deviceAuthorizationView('auth.oauth.device.authorize');

    // 通过提供闭包...
    Passport::deviceUserCodeView(
        fn ($parameters) => Inertia::render('Auth/OAuth/Device/UserCode')
    );

    Passport::deviceAuthorizationView(
        fn ($parameters) => Inertia::render('Auth/OAuth/Device/Authorize', [
            'request' => $parameters['request'],
            'authToken' => $parameters['authToken'],
            'client' => $parameters['client'],
            'user' => $parameters['user'],
            'scopes' => $parameters['scopes'],
        ])
    );

    // ...
}
```

Passport 会自动定义返回这些视图的路由。你的 `auth.oauth.device.user-code` 模板应包含一个表单，该表单向 `passport.device.authorizations.authorize` 路由发起 GET 请求。`passport.device.authorizations.authorize` 路由需要一个 `user_code` 查询参数。

你的 `auth.oauth.device.authorize` 模板应包含一个表单，用于向 `passport.device.authorizations.approve` 路由发起 POST 请求以批准授权，以及一个表单用于向 `passport.device.authorizations.deny` 路由发起 DELETE 请求以拒绝授权。`passport.device.authorizations.approve` 和 `passport.device.authorizations.deny` 路由需要 `state`、`client_id` 和 `auth_token` 字段。

### 创建设备授权许可客户端

在你的应用程序能够通过设备授权许可颁发令牌之前，你需要创建一个启用设备流程的客户端。你可以使用带有 `--device` 选项的 `passport:client` Artisan 命令来完成此操作。此命令将创建一个第一方的、启用设备流程的客户端，并向你提供客户端 ID 和密钥：

```shell
php artisan passport:client --device
```



此外，你可以在 `ClientRepository` 类上使用 `createDeviceAuthorizationGrantClient` 方法，为指定用户注册一个第三方客户端：

```php
use App\Models\User;
use Laravel\Passport\ClientRepository;

$user = User::find($userId);

$client = app(ClientRepository::class)->createDeviceAuthorizationGrantClient(
    user: $user,
    name: 'Example Device',
    confidential: false,
);
```

### 请求令牌

#### 请求设备代码（Device Code）

一旦客户端被创建，开发者可以使用其客户端 ID 从你的应用程序请求设备代码。首先，消费设备应向你的应用程序的 `/oauth/device/code` 路由发送一个 `POST` 请求，以请求设备代码：

```php
use Illuminate\Support\Facades\Http;

$response = Http::asForm()->post('https://passport-app.test/oauth/device/code', [
    'client_id' => 'your-client-id',
    'scope' => 'user:read orders:create',
]);

return $response->json();
```

这将返回一个包含 `device_code`、`user_code`、`verification_uri`、`interval` 和 `expires_in` 属性的 JSON 响应。`expires_in` 属性包含距离设备代码过期的秒数。`interval` 属性包含消费设备在轮询 `/oauth/token` 路由时，为避免速率限制错误应等待的秒数。

> [!注意]
> 请记住，`/oauth/device/code` 路由已经由 Passport 定义，你不需要手动定义此路由。

#### 显示验证 URI 和用户代码

一旦获得设备代码请求，消费设备应指示用户使用另一台设备访问提供的 `verification_uri`，并输入 `user_code` 以批准授权请求。




#### 轮询令牌请求（Polling Token Request）

由于用户将使用一台独立的设备来授予（或拒绝）访问权限，消费设备应当轮询你的应用程序的 `/oauth/token` 路由，以确定用户何时对请求作出了响应。消费设备在请求设备代码时，应使用 JSON 响应中提供的最小轮询 `interval`，以避免速率限制错误：

```php
use Illuminate\Support\Facades.Http;
use Illuminate\Support\Sleep;

$interval = 5;

do {
    Sleep::for($interval)->seconds();

    $response = Http::asForm()->post('https://passport-app.test/oauth/token', [
        'grant_type' => 'urn:ietf:params:oauth:grant-type:device_code',
        'client_id' => 'your-client-id',
        'client_secret' => 'your-client-secret', // 仅对保密客户端（confidential clients）需要...
        'device_code' => 'the-device-code',
    ]);

    if ($response->json('error') === 'slow_down') {
        $interval += 5;
    }
} while (in_array($response->json('error'), ['authorization_pending', 'slow_down']));

return $response->json();
```

如果用户已批准授权请求，这将返回一个包含 `access_token`、`refresh_token` 和 `expires_in` 属性的 JSON 响应。`expires_in` 属性包含距离访问令牌过期的秒数。

## 密码授权（Password Grant）

> [!警告]
> 我们不再推荐使用密码授权令牌。相反，你应当选择 **[OAuth2 Server 当前推荐的授予类型](https://oauth2.thephpleague.com/authorization-server/which-grant/)**。

OAuth2 密码授权允许你的其他第一方客户端（例如移动应用）使用电子邮件地址 / 用户名和密码来获取访问令牌。这使你能够安全地向你的第一方客户端签发访问令牌，而无需让用户经历完整的 OAuth2 授权码重定向流程。


要启用密码授权（password grant），请在你应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `enablePasswordGrant` 方法：

```php
/**
 * 初始化应用程序服务。
 */
public function boot(): void
{
    Passport::enablePasswordGrant();
}
```

### 创建密码授权客户端

在你的应用程序能够通过密码授权颁发令牌之前，你需要创建一个密码授权客户端。你可以使用带有 `--password` 选项的 `passport:client` Artisan 命令来完成此操作。

```shell
php artisan passport:client --password
```

### 请求令牌

一旦你启用了授权方式并创建了密码授权客户端，你可以向 `/oauth/token` 路由发起一个 `POST` 请求，通过提供用户的电子邮件地址和密码来请求访问令牌。请记住，此路由已经由 Passport 注册，因此无需手动定义它。如果请求成功，你将从服务器返回的 JSON 响应中收到一个 `access_token` 和 `refresh_token`：

```php
use Illuminate\Support\Facades.Http;

$response = Http::asForm()->post('https://passport-app.test/oauth/token', [
    'grant_type' => 'password',
    'client_id' => 'your-client-id',
    'client_secret' => 'your-client-secret', // 仅对保密客户端（confidential clients）需要...
    'username' => 'taylor@laravel.com',
    'password' => 'my-password',
    'scope' => 'user:read orders:create',
]);

return $response->json();
```

> [!注意]
> 请记住，访问令牌默认是长时效的。但是，如果需要，你可以自由地 **[配置你的访问令牌的最大生命周期](#configuration)**。

### 请求所有作用域（Scopes）

当使用密码授权或客户端凭据授权（client credentials grant）时，你可能希望为令牌授权你的应用程序所支持的所有作用域。你可以通过请求 `*` 作用域来实现这一点。如果你请求了 `*` 作用域，那么令牌实例上的 `can` 方法将始终返回 `true`。此作用域只能分配给使用 `password` 或 `client_credentials` 授权方式签发的令牌：

```php
use Illuminate\Support\Facades\Http;

$response = Http::asForm()->post('https://passport-app.test/oauth/token', [
    'grant_type' => 'password',
    'client_id' => 'your-client-id',
    'client_secret' => 'your-client-secret', // Required for confidential clients only...
    'username' => 'taylor@laravel.com',
    'password' => 'my-password',
    'scope' => '*',
]);
```



### 自定义用户提供者

如果你的应用程序使用了多个[认证用户提供者](/docs/laravel/12.x/authentication#introduction)，你可以在通过 `artisan passport:client --password` 命令创建客户端时，提供 `--provider` 选项来指定密码授权客户端所使用的用户提供者。所给的提供者名称应当与应用程序的 `config/auth.php` 配置文件中定义的有效提供者相匹配。然后，你可以使用[中间件来保护你的路由](#multiple-authentication-guards)，以确保只有来自该守卫所指定提供者的用户才被授权。

### 自定义用户名字段

在使用密码授权进行认证时，Passport 会使用你的可认证模型的 `email` 属性作为“用户名”。然而，你可以通过在模型上定义一个 `findForPassport` 方法来自定义此行为：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Passport\Contracts\OAuthenticatable;
use Laravel\Passport\HasApiTokens;

class User extends Authenticatable implements OAuthenticatable
{
    use HasApiTokens, Notifiable;

    /**
     * 查找给定用户名的用户实例。
     */
    public function findForPassport(string $username): User
    {
        return $this->where('username', $username)->first();
    }
}
```

### 自定义密码验证

在使用密码授权进行认证时，Passport 会使用你模型的 `password` 属性来验证所给密码。如果你的模型没有 `password` 属性，或者你希望自定义密码验证逻辑，你可以在模型上定义一个 `validateForPassportPasswordGrant` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Support\Facades\Hash;
use Laravel\Passport\Contracts\OAuthenticatable;
use Laravel\Passport\HasApiTokens;

class User extends Authenticatable implements OAuthenticatable
{
    use HasApiTokens, Notifiable;

    /**
     * 为 Passport 密码授权验证用户的密码。
     */
    public function validateForPassportPasswordGrant(string $password): bool
    {
        return Hash::check($password, $this->password);
    }
}
```



## 隐式授权（Implicit Grant）

> [!警告]
> 我们不再推荐使用隐式授权令牌。相反，你应该选择 [OAuth2 Server 当前推荐的授权类型](https://oauth2.thephpleague.com/authorization-server/which-grant/)。

隐式授权与授权码授权类似；然而，该令牌会直接返回给客户端，而无需交换授权码。此授权最常用于无法安全存储客户端凭据的 JavaScript 或移动应用程序。要启用该授权，请在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `enableImplicitGrant` 方法：

```php
/**
 * 在应用启动时进行服务的初始化配置。
 */
public function boot(): void
{
    Passport::enableImplicitGrant();
}
```

在你的应用程序能够通过隐式授权发放令牌之前，你需要创建一个隐式授权客户端。你可以使用带有 `--implicit` 选项的 `passport:client` Artisan 命令来完成此操作。

```shell
php artisan passport:client --implicit
```

一旦授权已启用并创建了隐式客户端，开发者就可以使用其客户端 ID 从你的应用程序请求访问令牌。消费端应用程序应当这样向你的应用程序的 `/oauth/authorize` 路由发起一个重定向请求：

```php
use Illuminate\Http\Request;

Route::get('/redirect', function (Request $request) {
    $request->session()->put('state', $state = Str::random(40));

    $query = http_build_query([
        'client_id' => 'your-client-id',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'response_type' => 'token',
        'scope' => 'user:read orders:create',
        'state' => $state,
        // 'prompt' => '', // "none", "consent", or "login"
    ]);

    return redirect('https://passport-app.test/oauth/authorize?'.$query);
});
```

> [!注意]
> 请记住，`/oauth/authorize` 路由已经由 Passport 定义。你无需手动定义此路由。



## 客户端凭据授权（Client Credentials Grant）

客户端凭据授权适用于机器对机器的认证。例如，你可以在一个计划任务中使用这种授权，该任务通过 API 执行维护操作。

在你的应用程序能够通过客户端凭据授权发放令牌之前，你需要创建一个客户端凭据授权客户端。你可以使用 `passport:client` Artisan 命令的 `--client` 选项来完成此操作：

```shell
php artisan passport:client --client
```

接下来，将 `Laravel\Passport\Http\Middleware\EnsureClientIsResourceOwner` 中间件分配给一个路由：

```php
use Laravel\Passport\Http\Middleware\EnsureClientIsResourceOwner;

Route::get('/orders', function (Request $request) {
    // 访问令牌有效，并且该客户端是资源所有者……
})->middleware(EnsureClientIsResourceOwner::class);
```

要将路由访问限制为特定的作用域（scopes），你可以向 `using` 方法提供所需作用域的列表：

```php
Route::get('/orders', function (Request $request) {
     // 访问令牌有效，客户端是资源所有者，并且拥有 “servers:read” 和 “servers:create” 这两个作用域……
})->middleware(EnsureClientIsResourceOwner::using('servers:read', 'servers:create');
```

### 获取令牌（Retrieving Tokens）

要使用此授权类型获取一个令牌，向 `oauth/token` 端点发起一个请求：

```php
use Illuminate\Support\Facades\Http;

$response = Http::asForm()->post('https://passport-app.test/oauth/token', [
    'grant_type' => 'client_credentials',
    'client_id' => 'your-client-id',
    'client_secret' => 'your-client-secret',
    'scope' => 'servers:read servers:create',
]);

return $response->json()['access_token'];
```

## 个人访问令牌（Personal Access Tokens）

有时，你的用户可能希望在不经过典型的授权码重定向流程的情况下给自己发放访问令牌。允许用户通过你的应用程序的 UI 自行发放令牌，对于让用户尝试你的 API 非常有用，或者可以作为一种更简单的方式来发放访问令牌。

> [!笔记]
> 如果你的应用程序主要使用 Passport 来发放个人访问令牌，考虑使用 [Laravel Sanctum](/docs/laravel/12.x/sanctum)，Laravel 的轻量级一方库，用于发放 API 访问令牌。



### 创建个人访问客户端（Creating a Personal Access Client）

在你的应用程序能够发放个人访问令牌之前，你需要创建一个个人访问客户端。你可以通过执行带有 `--personal` 选项的 `passport:client` Artisan 命令来完成此操作。如果你已经运行过 `passport:install` 命令，则不需要再次运行此命令：

```shell
php artisan passport:client --personal
```

### 自定义用户提供者（Customizing the User Provider）

如果你的应用程序使用了多个[认证用户提供者](/docs/laravel/12.x/authentication#introduction)，你可以在通过 `artisan passport:client --personal` 命令创建客户端时，通过提供 `--provider` 选项来指定个人访问授权客户端所使用的用户提供者。所给的提供者名称应当与应用程序的 `config/auth.php` 配置文件中定义的有效提供者相匹配。然后，你可以使用[中间件保护你的路由](#multiple-authentication-guards)，以确保只有来自该守卫所指定提供者的用户被授权。

### 管理个人访问令牌（Managing Personal Access Tokens）

创建个人访问客户端之后，你可以使用 `App\Models\User` 模型实例上的 `createToken` 方法为指定用户发放令牌。`createToken` 方法接收令牌名称作为其第一个参数，并将一个可选的[作用域（scopes）](#token-scopes)数组作为第二个参数：

```php
use App\Models\User;
use Illuminate\Support\Facades\Date;
use Laravel\Passport\Token;

$user = User::find($userId);

// 创建一个无作用域的令牌...
$token = $user->createToken('My Token')->accessToken;

// 创建一个带作用域的令牌...
$token = $user->createToken('My Token', ['user:read', 'orders:create'])->accessToken;

// 创建一个包含所有作用域的令牌...
$token = $user->createToken('My Token', ['*'])->accessToken;

// 获取属于该用户的所有有效个人访问令牌...
$tokens = $user->tokens()
    ->with('client')
    ->where('revoked', false)
    ->where('expires_at', '>', Date::now())
    ->get()
    ->filter(fn (Token $token) => $token->client->hasGrantType('personal_access'));

```



## 保护路由（Protecting Routes）

### 通过中间件（Via Middleware）

Passport 包含一个[认证守卫](/docs/laravel/12.x/authentication#adding-custom-guards)，它将验证传入请求中的访问令牌。一旦你将 `api` 守卫配置为使用 `passport` 驱动，你只需要在任何应当要求有效访问令牌的路由上指定 `auth:api` 中间件即可：

```php
Route::get('/user', function () {
    // 只有通过 API 认证的用户才能访问此路由...
})->middleware('auth:api');
```

> [!警告]
> 如果你使用的是[客户端凭据授权](#client-credentials-grant)，你应该使用 [`Laravel\Passport\Http\Middleware\EnsureClientIsResourceOwner` 中间件](#client-credentials-grant)来保护你的路由，而不是使用 `auth:api` 中间件。

#### 多个认证守卫（Multiple Authentication Guards）

如果你的应用程序对不同类型的用户进行认证，并且这些用户可能使用完全不同的 Eloquent 模型，那么你可能需要在应用程序中为每种用户提供者类型定义一个守卫配置。这允许你保护针对特定用户提供者的请求。例如，给定 `config/auth.php` 配置文件中的以下守卫配置：

```php
'guards' => [
    'api' => [
        'driver' => 'passport',
        'provider' => 'users',
    ],

    'api-customers' => [
        'driver' => 'passport',
        'provider' => 'customers',
    ],
],
```

下面的路由将使用 `api-customers` 守卫（该守卫使用 `customers` 用户提供者）来认证传入的请求：

```php
Route::get('/customer', function () {
    // ...
})->middleware('auth:api-customers');
```

> [!注意]
> 关于在 Passport 中使用多个用户提供者的更多信息，请查阅[个人访问令牌文档](#customizing-the-user-provider-for-pat)和[密码授权文档](#customizing-the-user-provider)。

### 传递访问令牌（Passing the Access Token）

当调用由 Passport 保护的路由时，你的应用程序的 API 使用者应当在请求的 `Authorization` 头中，将他们的访问令牌作为 `Bearer` 令牌进行指定。例如，当使用 `Http` Facade 时：

```php
use Illuminate\Support\Facades\Http;

$response = Http::withHeaders([
    'Accept' => 'application/json',
    'Authorization' => "Bearer $accessToken",
])->get('https://passport-app.test/api/user');

return $response->json();
```



## 令牌作用域（Token Scopes）

作用域允许你的 API 客户端在请求授权以访问账户时，请求一组特定的权限。
例如，如果你正在构建一个电子商务应用，并不是所有 API 使用者都需要下单的能力。相反，你可以只允许这些使用者请求授权来访问订单的发货状态。
换句话说，作用域允许你应用的用户限制第三方应用代表他们可以执行的操作。

### 定义作用域（Defining Scopes）

你可以在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中，使用 `Passport::tokensCan` 方法来定义 API 的作用域。
`tokensCan` 方法接受一个由作用域名称和作用域描述组成的数组。
作用域描述可以是你希望的任何内容，并将显示在授权批准界面上供用户查看：

```php
/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    Passport::tokensCan([
        'user:read' => 'Retrieve the user info',
        'orders:create' => 'Place orders',
        'orders:read:status' => 'Check order status',
    ]);
}
```

### 默认作用域（Default Scope）

如果客户端没有请求任何特定的作用域，你可以使用 `defaultScopes` 方法来配置 Passport 服务器，将默认作用域附加到令牌上。
通常，你应该在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Passport\Passport;

Passport::tokensCan([
    'user:read' => 'Retrieve the user info',
    'orders:create' => 'Place orders',
    'orders:read:status' => 'Check order status',
]);

Passport::defaultScopes([
    'user:read',
    'orders:create',
]);
```

### 将作用域分配给令牌（Assigning Scopes to Tokens）



#### 当请求授权码时（When Requesting Authorization Codes）

当使用**授权码模式（authorization code grant）**请求访问令牌时，使用者（客户端）应通过 `scope` 查询字符串参数指定其所需的作用域。
`scope` 参数应为一个**以空格分隔的作用域列表**：

```php
Route::get('/redirect', function () {
    $query = http_build_query([
        'client_id' => 'your-client-id',
        'redirect_uri' => 'https://third-party-app.com/callback',
        'response_type' => 'code',
        'scope' => 'user:read orders:create',
    ]);

    return redirect('https://passport-app.test/oauth/authorize?'.$query);
});
```

#### 当签发个人访问令牌时（When Issuing Personal Access Tokens）

如果你使用 `App\Models\User` 模型的 `createToken` 方法来签发个人访问令牌，你可以将所需作用域的数组作为该方法的第二个参数传入：

```php
$token = $user->createToken('My Token', ['orders:create'])->accessToken;
```

### 检查作用域（Checking Scopes）

Passport 包含两个中间件，可用于验证传入请求是否通过**已被授予指定作用域的令牌**进行身份验证。

#### 检查是否拥有所有作用域（Check For All Scopes）

`Laravel\Passport\Http\Middleware\CheckToken` 中间件可以分配给路由，用于验证传入请求的访问令牌是否**拥有所有列出的作用域**：

```php
use Laravel\Passport\Http\Middleware\CheckToken;

Route::get('/orders', function () {
    // 访问令牌同时拥有「orders:read」和「orders:create」两个作用域。
})->middleware(['auth:api', CheckToken::using('orders:read', 'orders:create');
```

#### 检查是否拥有任意一个作用域（Check for Any Scopes）

`Laravel\Passport\Http\Middleware\CheckTokenForAnyScope` 中间件可以分配给路由，用于验证传入请求的访问令牌是否**至少拥有列出的作用域之一**：

```php
use Laravel\Passport\Http\Middleware\CheckTokenForAnyScope;

Route::get('/orders', function () {
    // 访问令牌拥有「orders:read」或「orders:create」其中任意一个作用域。
})->middleware(['auth:api', CheckTokenForAnyScope::using('orders:read', 'orders:create');
```



#### 在令牌实例上检查作用域（Checking Scopes on a Token Instance）

一旦一个通过访问令牌进行身份验证的请求进入你的应用，你仍然可以通过已认证的 `App\Models\User` 实例上的 `tokenCan` 方法，来检查该令牌是否拥有某个指定的作用域：

```php
use Illuminate\Http\Request;

Route::get('/orders', function (Request $request) {
    if ($request->user()->tokenCan('orders:create')) {
        // ...
    }
});
```

#### 额外的作用域方法（Additional Scope Methods）

`scopeIds` 方法将返回一个包含所有已定义 ID / 名称的数组：

```php
use Laravel\Passport\Passport;

Passport::scopeIds();
```

`scopes` 方法将返回一个由 `Laravel\Passport\Scope` 实例组成的数组，表示所有已定义的作用域：

```php
Passport::scopes();
```

`scopesFor` 方法将返回一个由 `Laravel\Passport\Scope` 实例组成的数组，这些实例与给定的 ID / 名称相匹配：

```php
Passport::scopesFor(['user:read', 'orders:create']);
```

你可以使用 `hasScope` 方法来判断某个给定的作用域是否已被定义：

```php
Passport::hasScope('orders:create');
```

## SPA 认证（SPA Authentication）

在构建 API 时，能够从你的 JavaScript 应用中直接使用你自己的 API 通常会非常有用。
这种 API 开发方式允许你自己的应用使用同一个你向外界公开的 API。
同一个 API 可以被你的 Web 应用、移动应用、第三方应用，以及你可能在各类包管理器上发布的任何 SDK 所使用。

通常情况下，如果你希望从 JavaScript 应用中使用你的 API，你需要手动向应用发送一个访问令牌，并在每次请求时将其传递给你的应用。
然而，Passport 提供了一个中间件，可以为你处理这些事情。
你只需要在应用的 `bootstrap/app.php` 文件中，将 `CreateFreshApiToken` 中间件追加到 `web` 中间件组中即可：

```php
use Laravel\Passport\Http\Middleware\CreateFreshApiToken;

->withMiddleware(function (Middleware $middleware) {
    $middleware->web(append: [
        CreateFreshApiToken::class,
    ]);
})
```

> [!警告]
> 你应当确保 CreateFreshApiToken 中间件是你的中间件栈中最后一个被列出的中间件。



该中间件会在你的响应中附加一个名为 `laravel_token` 的 Cookie。
该 Cookie 包含一个**加密的 JWT**，Passport 将使用它来对来自你的 JavaScript 应用的 API 请求进行身份验证。
该 JWT 的有效期等同于你的 `session.lifetime` 配置值。
现在，由于浏览器会在后续的所有请求中自动发送该 Cookie，你可以在不显式传递访问令牌的情况下，向应用的 API 发起请求：

```js
axios.get('/api/user')
    .then(response => {
        console.log(response.data);
    });
```

#### 自定义 Cookie 名称（Customizing the Cookie Name）

如有需要，你可以使用 `Passport::cookie` 方法来自定义 `laravel_token` Cookie 的名称。
通常，应当在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用该方法：

```php
/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    Passport::cookie('custom_name');
}
```

#### CSRF 保护（CSRF Protection）

当使用这种认证方式时，你需要确保在请求中包含一个有效的 CSRF 令牌请求头。
Laravel 默认提供的 JavaScript 脚手架（包含在骨架应用和所有起始套件中）内置了一个 [Axios](https://github.com/axios/axios) 实例，该实例会自动使用加密的 `XSRF-TOKEN` Cookie 值，在同源请求中发送 `X-XSRF-TOKEN` 请求头。

> [!注意]
> 如果你选择发送 `X-CSRF-TOKEN` 请求头而不是 `X-XSRF-TOKEN`，则需要使用 `csrf_token()` 提供的**未加密**令牌。


## 事件（Events）

Passport 在签发访问令牌和刷新令牌时会触发事件。
你可以[监听这些事件](/docs/laravel/12.x/events)，以便在数据库中清理或撤销其他访问令牌：

<div class="overflow-auto">

| Event Name |
| --- |
| `Laravel\Passport\Events\AccessTokenCreated` |
| `Laravel\Passport\Events\AccessTokenRevoked` |
| `Laravel\Passport\Events\RefreshTokenCreated` |

</div>



## 测试（Testing）

Passport 的 `actingAs` 方法可用于指定当前已认证的用户以及其作用域。
传递给 `actingAs` 方法的第一个参数是用户实例，第二个参数是应当授予该用户令牌的作用域数组：

```php tab=Pest
use App\Models\User;
use Laravel\Passport\Passport;

test('orders can be created', function () {
    Passport::actingAs(
        User::factory()->create(),
        ['orders:create']
    );

    $response = $this->post('/api/orders');

    $response->assertStatus(201);
});
```

```php tab=PHPUnit
use App\Models\User;
use Laravel\Passport\Passport;

public function test_orders_can_be_created(): void
{
    Passport::actingAs(
        User::factory()->create(),
        ['orders:create']
    );

    $response = $this->post('/api/orders');

    $response->assertStatus(201);
}
```

Passport 的 `actingAsClient` 方法可用于指定当前已认证的客户端以及其作用域。
传递给 `actingAsClient` 方法的第一个参数是客户端实例，第二个参数是应当授予该客户端令牌的作用域数组：

```php tab=Pest
use Laravel\Passport\Client;
use Laravel\Passport\Passport;

test('servers can be retrieved', function () {
    Passport::actingAsClient(
        Client::factory()->create(),
        ['servers:read']
    );

    $response = $this->get('/api/servers');

    $response->assertStatus(200);
});
```

```php tab=PHPUnit
use Laravel\Passport\Client;
use Laravel\Passport\Passport;

public function test_servers_can_be_retrieved(): void
{
    Passport::actingAsClient(
        Client::factory()->create(),
        ['servers:read']
    );

    $response = $this->get('/api/servers');

    $response->assertStatus(200);
}
```
